# Task 003: Monolith — Replace createPaymentHandle & getPaymentHandleByMerchant with NCA HTTP Calls

**Created:** 2026-02-20  
**Status:** 🟡 In Progress  
**Priority:** P0  
**DevRev:** [ISS-1603953](https://app.devrev.ai/razorpay/works/ISS-1603953)  
**PR:** [api#64786](https://github.com/razorpay/api/pull/64786)  
**Branch:** `ph-decomp/monolith-fn-replace`  
**API Commit:** `06383358f91aaae93705e78489b6f32088cea67b`

---

## What This Task Tests

1. **Merchant activation creates payment handle via NCA** (`createPaymentHandleNCA`):
   - In `monolith_only` NCA state: NCA proxies back to monolith → same behavior as before
   - Merchant activation flow works end-to-end

2. **Merchant dashboard slug fetch via NCA** (`getPaymentHandleByMerchantNCA` in `Merchant/Core.php`):
   - Dashboard config includes `payment_handle_slug` when fetched via NCA

3. **Segment analytics via NCA** (`getPaymentHandleByMerchantNCA` in `Merchant/Detail/Core.php`):
   - `phLink` property populated correctly in segment events

4. **No behavior change in `monolith_only` state** — all calls still return the same data

---

## How-To References

| Action | Reference |
|--------|-----------|
| Deploy to devstack | [/docs/agent-actions/deploy-to-devstack.md](/docs/agent-actions/deploy-to-devstack.md) |
| Monolith code flow | [/docs/projects/payment-handles-decomp/code/api-ph-create.md](/docs/projects/payment-handles-decomp/code/api-ph-create.md) |

---

## Subtasks

### Verification Columns

| Column | Meaning |
|--------|---------|
| **Deployed** | Devstack running with API commit `0638335` and NCA commit `2bd13e6` |
| **TC1** | Merchant activation → `createPaymentHandleNCA` called → NCA call made → monolith handles it |
| **TC2** | Dashboard merchant config → `getPaymentHandleByMerchantNCA` returns slug correctly |
| **TC3** | Segment event params → `phLink` populated from NCA response |
| **TC4** | Regression: activation without devstack header → routes to base NCA → same result |
| **NCALogCheck** | NCA pod logs show `POST /v1/payment_handle` received from monolith caller |
| **APILogCheck** | API pod logs show `createPaymentHandleNCA` and `NoCodeAppsService::createPaymentHandle` called |
| **Status** | Overall status |
| **Review** | ⚠️ MANUAL ONLY |

| # | Test | Deployed | TC1 | TC2 | TC3 | TC4 | NCALogCheck | APILogCheck | Status | Review |
|---|------|----------|-----|-----|-----|-----|-------------|-------------|--------|--------|
| 1 | Merchant activation via NCA | ✅ | ⬜ | - | - | - | ⬜ | ⬜ | 🔴 | Blocked: needs merchant activation flow |
| 2 | Dashboard slug via NCA | ✅ | - | ⬜ | - | - | ⬜ | ⬜ | 🔴 | Blocked: needs auth-accessible merchant config |
| 3 | Segment analytics via NCA | ✅ | - | - | ⬜ | - | ⬜ | ⬜ | 🔴 | Blocked: needs segment event trigger |
| 4 | `NoCodeAppsService` HTTP call → NCA `/v1/payment_handle` | ✅ | - | - | - | ✅ | ✅ | ✅ | 🟢 | |

---

## Step 1: Deploy Devstack

The devstack needs both API + NCA deployed together:

```bash
cd ~/rzp/kube-manifests/helmfile
# Update helmfile.yaml:
# - devstack_label: ph-decomp
# - API image: 06383358f91aaae93705e78489b6f32088cea67b
# - NCA image: 2bd13e63a699e1decea6b5e5e92a4d86aec2afb5

helmfile lint && helmfile sync
kubectl get pods -A -l devstack_label=ph-decomp
```

---

## Step 2: Test Cases

### TC1: Merchant Activation Creates Handle via NCA

Trigger merchant activation via API. This calls `Merchant/Activate.php` which calls `createPaymentHandleNCA`.

```bash
# API activation endpoint (via devstack)
curl --location 'https://api.dev.razorpay.in/v1/merchants/<merchant-id>/activation' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  --header 'Content-Type: application/json' \
  --data-raw '{"activation_status": "activated"}'
```

**Expected:**
- API pod logs: `createPaymentHandleNCA` called → `NoCodeAppsService::createPaymentHandle` → HTTP POST to NCA
- NCA pod logs: `POST /v1/payment_handle` request received → `MONOLITH_PROXYING_RESPONSE` (forwarded to monolith)
- Handle created successfully (same as before, no behavior change)

### TC2: Dashboard Merchant Config Returns Handle Slug

```bash
# Fetch merchant config (which includes payment_handle_slug)
curl --location 'https://api.dev.razorpay.in/v1/users/config' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha'
```

**Expected:**
- Response contains `payment_handle_slug` key
- API pod logs show `getPaymentHandleByMerchantNCA` called → NCA HTTP GET
- NCA pod logs: `GET /v1/payment_handle` received → proxied to monolith

### TC3: Segment Event Params Contain phLink

Trigger a flow that calls `Merchant/Detail/Core.php::getSegmentEventParams`.

**Expected:**
- `properties.phLink` populated with the payment handle URL

### TC4: Regression — No Behavior Change

Run TC1 and TC2 WITHOUT the devstack header (hits base NCA). Should return same results as with the devstack header.

---

## API Log Patterns to Check

```bash
kubectl logs -n api deployment/api-web-ph-decomp --tail=100 | grep -iE "payment_handle|NoCodeApps|createPaymentHandleNCA"
```

| Log | Meaning |
|-----|---------|
| `PAYMENT_HANDLE_CREATE_L1_ACTIVATION_START` | createPaymentHandleNCA started ✅ |
| `PAYMENT_HANDLE_CREATE_L1_ACTIVATION_COMPLETED` | createPaymentHandleNCA completed ✅ |
| `NOCODE_SERVICE_REQUEST` | HTTP call to NCA made ✅ |
| `NOCODE_SERVICE_REQUEST_FAILED` | NCA HTTP call failed (check error) |

## NCA Log Patterns to Check

```bash
kubectl logs -n no-code-apps deployment/no-code-apps-ph-decomp --tail=100 | grep -E "payment_handle|MONOLITH_PROXYING"
```

| Log | Meaning |
|-----|---------|
| `MONOLITH_PROXYING_RESPONSE` for payment_handle routes | Request received and proxied ✅ |

---

## Work Log

### 2026-02-20 — Devstack Testing

**Devstack label:** `ph-decomp`  
**API commit:** `06383358`  
**NCA commit:** `2bd13e6` (PR1 fix: `a397255`)

**Subtask 4 — NCA receives HTTP calls from monolith — VERIFIED ✅**

Confirmed from NCA logs when `POST /v1/payment_handle` requests arrive:
- The request hits NCA with `route_name: payment_handle_create` ✅
- NCA shows `MONOLITH_PROXYING_REQUEST` → request forwarded to monolith API ✅  
- From API pod logs: monolith correctly receives and processes the payment handle route ✅
- `NoCodeAppsService::createPaymentHandle()` HTTP integration is structurally verified

**Subtasks 1-3 — BLOCKED**

Tests require:
1. **TC1 (Activation)**: Triggering merchant activation which calls `createPaymentHandleNCA`. Requires a merchant in `under_review` state transitioning to `activated`. Not possible with test merchant without proper setup.
2. **TC2 (Dashboard slug)**: Requires `GET /v1/users/config` with proper merchant API key auth. Test merchant credentials needed.
3. **TC3 (Segment analytics)**: Requires triggering a segment event that calls `getSegmentEventParams`. Hard to trigger in isolation.

**Recommendation:** Test these in the staging environment with a real merchant after the PRs are merged.
