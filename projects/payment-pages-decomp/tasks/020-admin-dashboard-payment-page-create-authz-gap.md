# Security Investigation: Agents Can Create Payment Pages via Admin Dashboard (Login-as-Merchant)

**Created:** 2026-04-21
**Status:** 🔴 Open — Fix Required
**Priority:** P0 (Security / Compliance)
**Incident:** INC-17909
**Slack Thread:** [#p0-oncall C02B75CA8V9 ts:1776345894.315349](https://razorpay.slack.com/archives/C02B75CA8V9/p1776771114096089?thread_ts=1776345894.315349&cid=C02B75CA8V9)

---

## Problem Statement

CS agents (internal Razorpay users) can **create payment pages on behalf of merchants** when logged into the admin dashboard using the "login-as-merchant" feature. This is a security / compliance gap: agents should only be able to perform read or approved limited-write operations when impersonating a merchant, not create new assets in the merchant's account.

This was surfaced as issue #1 in a post-incident audit after INC-17909 (where agents were also able to initiate refunds as merchants). The full list of open issues from the audit:

> 1. **Agents can create payment pages on mx behalf** ← this doc
> 2. Agents can request payment methods on merchant behalf
> 3. Agents can pause settlements in merchant dashboard
> 4. Agents can create payment buttons on merchant behalf

Source: [Slack message ts:1776747012.565159](https://razorpay.slack.com/archives/C02B75CA8V9/p1776771114096089?thread_ts=1776345894.315349&cid=C02B75CA8V9)

---

## Expected Behaviour

When a Razorpay internal agent logs in as a merchant via the admin dashboard:
- They should be treated as a **restricted principal** (`pseudo_owner` role)
- They should be able to **view / list** payment pages
- They should **NOT** be able to **create** payment pages on the merchant's behalf

---

## Actual Behaviour

Agents with edit-level admin permissions can successfully call `POST /v1/payment_pages` while logged in as a merchant, creating payment pages in the merchant's account.

---

## Investigation — Full Chain of Evidence

### Step 1 — Authz Repo: What the `pseudo_owner` Role Is Allowed To Do

**Repo:** `rzp` (razorpay/authz), symlinked at `pp-decomp/rzp`

The authz repo manages Kong-level authorization policies as CSV files. Payment page policies for the `pseudo_owner` role live in:

```
rzp/scripts/policies/dashboard/2026_04_06_nocodeapps_payment_pages_pseudo_owner.csv
```

Contents (full file):

```csv
Policy Name,Service,Resource,Action,Resource Group,Role
nocodeapps_payment_page_list_owner,gateway,/v1/payment_pages,get,gateway,pseudo_owner
nocodeapps_payment_page_get_owner,gateway,/v1/payment_pages/{id},get,gateway,pseudo_owner
nocodeapps_payment_page_get_details_owner,gateway,/v1/payment_pages/{id}/details,get,gateway,pseudo_owner
nocodeapps_payment_page_set_receipt_details_owner,gateway,/v1/payment_pages/{id}/receipt,post,gateway,pseudo_owner
nocodeapps_payment_page_get_invoice_details_owner,gateway,/v1/payment_pages/{id}/receipt,get,gateway,pseudo_owner
nocodeapps_payment_page_notify_owner,gateway,/v1/payment_pages/{id}/notify,post,gateway,pseudo_owner
nocodeapps_payment_page_deactivate_owner,gateway,/v1/payment_pages/{id}/deactivate,patch,gateway,pseudo_owner
nocodeapps_payment_page_activate_owner,gateway,/v1/payment_pages/{id}/activate,patch,gateway,pseudo_owner
nocodeapps_payment_page_item_update_owner,gateway,/v1/payment_pages/payment_page_item/{id},patch,gateway,pseudo_owner
nocodeapps_payment_page_send_receipt_owner,gateway,/v1/payment_pages/{id}/send_receipt,post,gateway,pseudo_owner
nocodeapps_payment_page_update_owner,gateway,/v1/payment_pages/{id},patch,gateway,pseudo_owner
nocodeapps_payment_page_slug_exists_owner,gateway,/v1/payment_pages/{id}/exists,get,gateway,pseudo_owner
nocodeapps_payment_page_slug_exists_owner,gateway,/v1/payment_pages/{id}/exists,get,gateway,merchant_view_only
nocodeapps_payment_page_save_receipt_owner,gateway,/v1/payment_pages/{id}/save_receipt,post,gateway,pseudo_owner
```

**Key observation:** `POST /v1/payment_pages` (creation) is **intentionally absent** from the `pseudo_owner` policy. All other CRUD operations are covered. This was added on April 6, 2026 specifically to scope what login-as-merchant agents can do.

---

### Step 2 — Authz Repo: What Regular Dashboard Roles Can Do (The Problem)

Creation (`POST /v1/payment_pages`) is granted to the following roles:

**File:** `rzp/scripts/policies/dashboard/2024_12_18_payments_nocodeapps.csv`

```csv
nocodeapps_payment_page_create_admin_role,gateway,/v1/payment_pages,post,gateway,owner
nocodeapps_payment_page_create_support_role,gateway,/v1/payment_pages,post,gateway,support
nocodeapps_payment_page_create_manager_role,gateway,/v1/payment_pages,post,gateway,manager
nocodeapps_payment_page_create_operations_role,gateway,/v1/payment_pages,post,gateway,operations
nocodeapps_payment_page_create_owner_role,gateway,/v1/payment_pages,post,gateway,admin
```

**File:** `rzp/scripts/policies/dashboard/2025_01_28_payments_nocodeapps.csv`

```csv
nocodeapps_payment_page_create_partner,gateway,/v1/payment_pages,post,gateway,partner
```

So if an agent ends up with the `owner` role (as will be shown below), they pass authz checks for creation.

---

### Step 3 — Kong TF: `payment_page_create` Is Not Blocked at the Edge

**File:** `terraform-kong/prod/api-dashboard/templates/admin-dashboard.tf`

The admin dashboard Kong module has two route buckets:

```hcl
login_as_mx_critical_paths = {
  merchant_activation_save-api-dashboard-admin = {
    path    = ["~/v1/merchant/activation/?$"]
    methods = ["POST"]
  }
  // ← payment_page_create is NOT here
}

paths = {
  ...
  payment_page_create-api-dashboard-admin = {
    path    = ["~/v1/payment_pages/?$"]
    methods = ["POST"]
  }
  ...
}
```

The global `login-as-merchant` Kong plugin applied to this service is configured as:

```json
{
  "login_as_merchant_action": "NON-CRITICAL",
  "protocol": "https",
  "upstream": "admin-experience-service",
  ...
}
```

`NON-CRITICAL` means the edge plugin **does not block** this request when an admin is acting as merchant. Only routes in `login_as_mx_critical_paths` get the `CRITICAL` treatment.

Currently only `merchant_activation_save` is in `login_as_mx_critical_paths`. Everything else — including payment page creation — passes through as `NON-CRITICAL`.

---

### Step 4 — Monolith `BasicAuth.php`: The Role That Gets Assigned

**File:** `api/app/Http/BasicAuth/BasicAuth.php` — `setUserRole()` method

This is where the root cause lives. The flow when an admin with edit permissions logs in as merchant:

```
setUserRole($userId) is called
  ↓
isAdminLoggedInAsMerchantOnDashboard() → true
  ↓
getAdminPermissions($adminId) → {
    hasReadPermission: true,
    hasLoginPermission: true,
    hasEditPermission: true,   ← agent has edit perm
    hasNonActivatedEditPermission: ...,
    hasActivatedEditPermission: ...
}
  ↓
Checks:
  - hasViewLoginPerm && hasReadPerm && !hasEditPerm && isProductBanking → BANKING_READONLY [NOT triggered]
  - hasViewLoginPerm && hasReadPerm && !hasEditPerm && !isProductBanking → ADMIN_READONLY [NOT triggered]
  ↓
Falls through — NO ROLE SET in the login-as-merchant block
  ↓
getMerchantUserMapping($merchantId, $userId)
  → returns the admin's actual mapping in merchant's user table
  → getUserRoleFromEntity($userMapping) → "owner"
  ↓
$this->userRole = "owner"
```

Relevant code (lines ~3380–3470 of `BasicAuth.php`):

```php
public function setUserRole(string $userId)
{
    if ($this->isAdminLoggedInAsMerchantOnDashboard() === true)
    {
        // ...
        if ($hasViewLoginPerm === true && $hasReadPerm === true && $hasEditPerm === false
            && $this->isProductBanking() === true) {
            $this->userRole = Role::BANKING_READONLY;
            return;
        }
        if ($hasViewLoginPerm === true && $hasReadPerm === true && $hasEditPerm === false
            && $hasNonActivatedEditPerm === false && $hasActivatedEditPermission === false) {
            $this->userRole = Role::ADMIN_READONLY;
            return;
        }
        // ← NO ELSE BRANCH FOR hasEditPerm === true
        // Falls through silently.
    }

    // ...
    if (empty($merchantId) === false)
    {
        $userMapping = $this->repo->merchant->getMerchantUserMapping($merchantId, $userId);

        if (empty($userMapping) === false)
        {
            if ($this->isAdminLoggedInAsMerchantOnDashboard() === true && $this->isProductBanking()) {
                $this->userRole = Role::BANKING_READONLY;
            }
            else {
                // ← THIS runs for non-banking admin-login-as-merchant WITH edit perm
                $this->userRole = $this->getUserRoleFromEntity($userMapping);
                // Returns the actual merchant mapping role → "owner"
            }
        }
    }
}
```

**Result:** An agent with edit permissions gets `owner` role when logging in as a merchant on the non-banking dashboard.

---

### Step 5 — `pseudo_owner` Role Exists But Is Never Assigned

`Role::PSEUDO_OWNER = 'pseudo_owner'` is defined in `api/app/Models/User/Role.php` (line 40).

It is referenced in:
- `Role.php` — constant definition
- `UserRolesScope.php` — feature-scope allowed-roles lists
- `rzp/scripts/policies/dashboard/2026_04_06_nocodeapps_payment_pages_pseudo_owner.csv` — authz policies

But **`setUserRole()` never assigns `Role::PSEUDO_OWNER`** for the login-as-merchant path with edit permissions. The authz CSV files defining what `pseudo_owner` can or cannot do are therefore inert for this scenario.

---

## Summary: Why Creation Works

| Layer | What Happens | Expected |
|-------|-------------|----------|
| Kong edge (login-as-merchant plugin) | `payment_page_create` is `NON-CRITICAL` → allowed through | Should be `CRITICAL` OR role should restrict it |
| `BasicAuth.setUserRole()` | Agent with edit perm falls through to `owner` role | Should set `pseudo_owner` |
| Authz check | `owner` has `POST /v1/payment_pages` → ✅ allowed | `pseudo_owner` does NOT have it → would block |

The authz CSV for `pseudo_owner` is correct and would block creation **if `pseudo_owner` were actually assigned**. The bug is in the role assignment.

---

## Fix Options

### Option A — Monolith `BasicAuth.php` (Root Fix — Recommended)

In `setUserRole()`, explicitly assign `Role::PSEUDO_OWNER` when an admin with edit permission logs in as merchant on the non-banking dashboard:

```php
if ($this->isAdminLoggedInAsMerchantOnDashboard() === true)
{
    // ...existing read-only checks...

    // NEW: if admin has edit permission, restrict to pseudo_owner
    if ($hasViewLoginPerm === true && $hasEditPerm === true
        && $this->isProductBanking() === false)
    {
        $this->userRole = Role::PSEUDO_OWNER;
        return;
    }
}
```

This makes `pseudo_owner` actually work as designed. Any resource/action not in the `pseudo_owner` authz policies (including `POST /v1/payment_pages`) will be blocked.

**Risk:** `pseudo_owner` authz policies must cover all legitimate operations agents should be allowed to perform. Missing a rule will start blocking previously-working flows. A thorough audit of the `pseudo_owner` CSVs against real agent workflows is needed before rolling this out.

---

### Option B — Kong TF (Edge Gate — Partial Fix)

Add `payment_page_create` to `login_as_mx_critical_paths` in `terraform-kong/prod/api-dashboard/templates/admin-dashboard.tf`:

```hcl
login_as_mx_critical_paths = {
  merchant_activation_save-api-dashboard-admin = {
    path    = ["~/v1/merchant/activation/?$"]
    methods = ["POST"]
  }
  payment_page_create-api-dashboard-admin = {
    path    = ["~/v1/payment_pages/?$"]
    methods = ["POST"]
  }
}
```

This blocks creation at the Kong layer regardless of role. Lower risk but doesn't fix the underlying role-assignment gap.

---

### Option C — Both (Defense in Depth)

Apply Option B immediately to stop the bleeding, then follow up with Option A for the proper fix.

---

## Scope of Impact

The same root cause (agents getting `owner` role on login-as-merchant) affects all `owner`-gated operations beyond just payment page creation. The other three issues from the INC-17909 audit are likely caused by the same gap:

- Requesting payment methods
- Pausing settlements
- Creating payment buttons

All of these require a holistic audit of what `pseudo_owner` should be allowed to do, followed by the Option A fix.

---

## Files Referenced

| File | Repo | Purpose |
|------|------|---------|
| `rzp/scripts/policies/dashboard/2026_04_06_nocodeapps_payment_pages_pseudo_owner.csv` | authz | `pseudo_owner` payment page policies |
| `rzp/scripts/policies/dashboard/2024_12_18_payments_nocodeapps.csv` | authz | Creation policies for regular roles |
| `terraform-kong/prod/api-dashboard/templates/admin-dashboard.tf` | terraform-kong | Kong admin dashboard routes |
| `api/app/Http/BasicAuth/BasicAuth.php` | api (monolith) | `setUserRole()` — role assignment logic |
| `api/app/Models/User/Role.php` | api (monolith) | `PSEUDO_OWNER` constant definition |
| `api/app/Http/UserRolesScope.php` | api (monolith) | Feature-scope role lists |
| `api/app/Http/Route.php` | api (monolith) | Route → `admin_dashboard` group membership |
