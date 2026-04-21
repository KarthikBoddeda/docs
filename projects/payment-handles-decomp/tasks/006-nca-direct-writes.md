# Task 006: NCA-Direct Writes + Merchant Settings Sync

**Created:** 2026-02-23
**Status:** ⬜ Not Started
**Priority:** P0
**Repos:** `no-code-apps` (PRs #1006, #1007) + `api` (PR #64786)
**Spec:** [PaymentHandleDecomp_v2.md](/projects/payment-handles-decomp/PaymentHandleDecomp_v2.md) — Sections 5.1, 5.2, 6.1, 6.2

---

## Context

This task supersedes the dual-write approach from Tasks 001 and 002. Instead of proxying writes to monolith and then backfilling NCA DB, **all new merchant payment handle writes go directly to NCA** from day 1.

The experiment simplifies to two states only:
- `monolith_only` — emergency rollback valve
- `nca_only` — default for all new merchants

Monolith still syncs `merchant_settings` after each NCA write response (so the old monolith read path works as a fallback/rollback).

---

## How-To References

| What | Where |
|------|-------|
| **Spec (v2)** — strategy, diagrams, PR impact | [/projects/payment-handles-decomp/PaymentHandleDecomp_v2.md](/projects/payment-handles-decomp/PaymentHandleDecomp_v2.md) |
| **NCA code navigation** — controller, core, repo, proxy wiring | [/projects/payment-handles-decomp/code/_index.md](/projects/payment-handles-decomp/code/_index.md) |
| **NCA ph-create flow** — current dual write path being replaced | [/projects/payment-handles-decomp/code/nca-ph-create.md](/projects/payment-handles-decomp/code/nca-ph-create.md) |
| **Monolith ph-create flow** — `createPaymentHandleNCA`, `upsertDefaultPaymentHandleForMerchant` | [/projects/payment-handles-decomp/code/api-ph-create.md](/projects/payment-handles-decomp/code/api-ph-create.md) |
| **Proxy states** — `monolith_only`, `nca_only`, dual write explained | [/projects/payment-handles-decomp/code/proxying.md](/projects/payment-handles-decomp/code/proxying.md) |
| **Monolith navigation** — how to find PHP classes/methods | [/projects/payment-handles-decomp/code/monolith-navigation-guide.md](/projects/payment-handles-decomp/code/monolith-navigation-guide.md) |
| **NCA navigation** — how to navigate Go code | [/projects/payment-handles-decomp/code/guide-to-navigate-nca-code.md](/projects/payment-handles-decomp/code/guide-to-navigate-nca-code.md) |
| **Deploy devstack** | [/docs/agent-actions/deploy-to-devstack.md](/docs/agent-actions/deploy-to-devstack.md) |
| **Hot reload** | [/docs/agent-actions/hot-reload-devspace.md](/docs/agent-actions/hot-reload-devspace.md) |
| **Payment pages equivalent** — `CreatePaymentPage` being reused here | [/projects/payment-pages-decomp/code/_index.md](/projects/payment-pages-decomp/code/_index.md) |
| **Previous task (003)** — monolith HTTP wiring already done in PR #64786 | [/projects/payment-handles-decomp/tasks/003-monolith-fn-replace.md](/projects/payment-handles-decomp/tasks/003-monolith-fn-replace.md) |
| **Previous task (002)** — dual write task being superseded | [/projects/payment-handles-decomp/tasks/002-ph-create-update.md](/projects/payment-handles-decomp/tasks/002-ph-create-update.md) |

---

## Changes Required

### NCA (no-code-apps) — PRs #1006 + #1007

#### 1. Remove `DualWriteHandlerForHandleWrites` from write path (`PR #1006`)

**File:** `internal/controllers/payment_handle.go`

Current (remove this):
```go
func (controller *PaymentHandleController) Create(req request.IRequest) response.IResponse {
    return controller.handleDualWriteHandler.Handle(req, controller.ncaCreate)
}
```

New (direct handler — no proxy to monolith):
```go
func (controller *PaymentHandleController) Create(req request.IRequest) response.IResponse {
    proxyState := app.GetProxyStateFromContext(req.Ctx())
    if proxyState == constants.ProxyStateMonolithOnly {
        return controller.monolithProxy.Handle(req)
    }
    return controller.handleCore.CreatePaymentHandle(req.Ctx(), req)
}
```

Similarly for `Update`.

Remove `handleDualWriteHandler` from the `PaymentHandleController` struct entirely.

#### 2. Remove `dual_write` experiment states (`PR #1006`)

**File:** `internal/monolith_decomp/dual_write_handlers/handle_writes.go` (or wherever `DualWriteHandlerForHandleWrites` is defined)

Remove the entire `DualWriteHandlerForHandleWrites` type — it is no longer used. The experiment handler for handles now only needs to distinguish `monolith_only` vs everything-else (`nca_only`).

**File:** `internal/modules/payment_page/core.go` — `GetPaymentHandleProxyStateFromSplitz`

No proxy state change needed in the Splitz call itself, but ensure `dual_write_*` variants are not acted upon for handle routes (they can fall through to `nca_only` behavior if someone accidentally sets them).

#### 3. Rewrite `CreatePaymentHandle` to use `CreatePaymentPage` (`PR #1007`)

**File:** `internal/modules/payment_handle/core.go`

Current signature (remove this):
```go
func (c *Core) CreatePaymentHandle(ctx context.Context, monolithResponse *proxy.ProxyResponse) errors.IError
```

New signature (takes the HTTP request, owns the full write):
```go
func (c *Core) CreatePaymentHandle(ctx context.Context, req payment_handle.ICreateRequest) (*payment_handle.CreateResponse, errors.IError)
```

**Implementation:**

Reuse `PaymentPageCore.CreatePaymentPage` with handle-specific defaults. This is the same path as `nca_only` for payment pages.

Build the `IPaymentPageRequest` from the handle request input:

| Field | Value |
|-------|-------|
| `view_type` | `PAYMENT_HANDLE` |
| `title` | Merchant billing label (from `merchantModule.GetMerchantDetails`) |
| `currency` | `INR` (default) |
| `payment_page_items` | Single item: `name=amount`, `mandatory=true`, `min_amount=100` |
| `settings.udf_schema` | `[{"name":"comment","title":"Comment","required":true,"type":"string","options":{},"settings":{"position":1}}]` |
| `slug` | From request input (validated) |
| `short_url` | `<paymentHandleHostedBaseUrl>/<slug>` |

**No ID reuse from monolith needed.** NCA calls `paymentPageEntity.GenerateAndSetId()` natively.

After `CreatePaymentPage` returns, build the response:
```go
type CreateResponse struct {
    Id       string `json:"id"`       // pl_ prefixed public ID
    Slug     string `json:"slug"`
    ShortUrl string `json:"short_url"`
    Title    string `json:"title"`
}
```

Remove `parseHandleMonolithResponse`, `plSign`, and `handleMonolithResponse` struct — no longer needed.

#### 4. Rewrite `UpdatePaymentHandle` similarly (`PR #1007`)

**File:** `internal/modules/payment_handle/core.go`

Current: takes `monolithResponse *proxy.ProxyResponse`, parses it.

New: takes the update request directly. Finds handle in NCA DB by `merchant_id + mode`, updates `slug`, `short_url`, `title`.

If entity not found (old merchant pre-migration): return a specific "not found" error so the controller can fall back to proxying monolith.

#### 5. Update `ICore` interface (`PR #1007`)

**File:** `internal/modules/payment_handle/core.go`

```go
type ICore interface {
    CreatePaymentHandle(ctx context.Context, req ICreateRequest) (*CreateResponse, errors.IError)
    UpdatePaymentHandle(ctx context.Context, req IUpdateRequest) (*UpdateResponse, errors.IError)
}
```

Remove the old `monolithResponse *proxy.ProxyResponse` parameters entirely.

---

### Monolith (api) — PR #64786

#### 6. Add `upsertDefaultPaymentHandleForMerchant` after NCA create response

**File:** `app/Models/PaymentLink/Service.php` — `createPaymentHandleNCA()`

After the NCA call returns successfully, sync monolith `merchant_settings` so the monolith read fallback path continues to work:

```php
$response = $ncaService->createPaymentHandle();

if (empty($response['data']) === false)
{
    $modifiedResponse = $response['data'];

    // Sync monolith merchant_settings so getPaymentHandleByMerchant
    // fallback path still works (emergency rollback + old merchant reads)
    $this->core->upsertDefaultPaymentHandleForMerchant(
        $modifiedResponse[Entity::SLUG],
        $modifiedResponse[Entity::ID]
    );
}
```

> **Note:** `upsertDefaultPaymentHandleForMerchant` uses `$this->merchant` internally. Ensure the merchant context is set before this call (it is — `getPrevAuthAndSetVariables` sets it).

#### 7. Remove `isPaymentHandleNCAEnabled` Splitz gate for writes

**File:** `app/Models/PaymentLink/Service.php` — `createPaymentHandleNCA()`

The experiment gate in `createPaymentHandleNCA` (the `isPaymentHandleNCAEnabled` check) should be removed. All activation-path writes always go to NCA. NCA itself handles `monolith_only` vs `nca_only` internally via the Splitz check on the NCA side.

```php
// Remove this block entirely:
if ($this->core->isPaymentHandleNCAEnabled($merchantId) === false)
{
    ...
    $modifiedResponse = $this->createPaymentHandleV2();
}
```

The function becomes: always call `$ncaService->createPaymentHandle()`, then upsert merchant_settings.

> **Keep `isPaymentHandleNCAEnabled` for reads** (`getPaymentHandleByMerchantNCA`) — still useful during transition since NCA reads are not yet fully live.

---

## Test Cases

### Verification Columns

| Column | Meaning |
|--------|---------|
| **Deployed** | Devstack running with updated NCA + API commits |
| **TC1** | `POST /v1/payment_handle` (nca_only) → entity created in NCA DB natively (no monolith proxy) |
| **TC2** | `POST /v1/payment_handle` (nca_only) → monolith `merchant_settings` updated after NCA create |
| **TC3** | `PATCH /v1/payment_handle` (nca_only) → entity updated in NCA DB |
| **TC4** | `POST /v1/payment_handle` (monolith_only) → NCA proxies to monolith, no NCA DB write |
| **TC5** | Monolith activation flow (`createPaymentHandleNCA`) → NCA creates handle directly → merchant_settings synced |
| **TC6** | `PATCH /v1/payment_handle` (nca_only) for old merchant (not in NCA DB) → falls back to monolith proxy |
| **DBCheck** | NCA `payment_handles` table has correct entity with NCA-generated ID |
| **SettingsCheck** | Monolith `merchant_settings` has correct `default_payment_handle.*` after TC2/TC5 |

| # | Test | Deployed | TC1 | TC2 | TC3 | TC4 | TC5 | TC6 | DBCheck | SettingsCheck | Status |
|---|------|----------|-----|-----|-----|-----|-----|-----|---------|---------------|--------|
| 1 | nca_only: create writes to NCA DB directly | ⬜ | ⬜ | - | - | - | - | - | ⬜ | - | ⬜ |
| 2 | nca_only: monolith merchant_settings synced | ⬜ | - | ⬜ | - | - | - | - | - | ⬜ | ⬜ |
| 3 | nca_only: update modifies NCA entity | ⬜ | - | - | ⬜ | - | - | - | ⬜ | - | ⬜ |
| 4 | monolith_only: proxy, no NCA write | ⬜ | - | - | - | ⬜ | - | - | ⬜ | - | ⬜ |
| 5 | Activation flow: NCA create + settings sync | ⬜ | - | - | - | - | ⬜ | - | ⬜ | ⬜ | ⬜ |
| 6 | Update: old merchant not in NCA → monolith fallback | ⬜ | - | - | - | - | - | ⬜ | - | - | ⬜ |

---

## Step 1: NCA Code Changes

### 1a. Refactor `payment_handle/core.go`

```bash
cd ~/rzp/no-code-apps-ph-decomp
git checkout -b ph-decomp/nca-direct-writes origin/pp-fixes-2
```

Key changes:
1. Change `CreatePaymentHandle(ctx, monolithResponse)` → `CreatePaymentHandle(ctx, req)` using `CreatePaymentPage` internally
2. Change `UpdatePaymentHandle(ctx, id, monolithResponse)` → `UpdatePaymentHandle(ctx, req)` with direct DB update
3. Remove `parseHandleMonolithResponse`, `plSign`, `handleMonolithResponse` struct

### 1b. Refactor `controllers/payment_handle.go`

1. Replace `handleDualWriteHandler.Handle(req, ncaCreate)` with direct `handleCore.CreatePaymentHandle(req.Ctx(), req)`
2. Remove `ncaCreate` and `ncaUpdate` callback functions
3. Remove `handleDualWriteHandler` field from `PaymentHandleController` struct
4. Add `monolith_only` guard: if proxy state is `monolith_only`, proxy to monolith

---

## Step 2: Monolith Code Changes

```bash
cd ~/rzp/api-ph-decomp
git checkout ph-decomp/monolith-fn-replace
```

Key changes in `app/Models/PaymentLink/Service.php`:
1. In `createPaymentHandleNCA`: add `upsertDefaultPaymentHandleForMerchant` call after NCA response
2. Remove `isPaymentHandleNCAEnabled` gate from `createPaymentHandleNCA` (keep it in `getPaymentHandleByMerchantNCA`)

---

## Step 3: Deploy Devstack

```bash
cd ~/rzp/kube-manifests/helmfile
# Update NCA image to new commit
# Update API image to new commit
helmfile sync -l name=no-code-apps-ph-decomp
helmfile sync -l name=api-ph-decomp
kubectl get pods -A -l devstack_label=ph-decomp
```

---

## Step 4: Test Cases

### TC1: NCA Direct Create (no monolith proxy)

```bash
curl --location 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
  --header 'X-Razorpay-Mode: live' \
  --header 'X-Proxy-State: nca_only' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  --header 'Content-Type: application/json' \
  --data-raw '{"slug": "testhandle2026"}'
```

**Expected:**
- NCA logs: `PH_NCA_CREATE_SUCCESS` (or `PAYMENT_PAGE_CREATE_REQUEST` with `view_type=PAYMENT_HANDLE`)
- **No** `MONOLITH_PROXYING_REQUEST` log
- Response contains `id` (NCA-generated), `slug`, `short_url`, `title`
- NCA DB: entity in `payment_handles` table with NCA-generated ID

**NCA log check:**
```bash
kubectl logs -n no-code-apps deployment/no-code-apps-ph-decomp --tail=50 | grep -E "PH_NCA|PAYMENT_PAGE_CREATE|MONOLITH_PROXYING"
```

### TC2: Monolith merchant_settings Synced After NCA Create

After TC5 (activation flow), verify monolith merchant_settings:

```bash
# Check merchant settings in monolith DB
kubectl exec -n api <api-pod> -- php artisan tinker
# >>> \RZP\Models\Settings\Accessor::for(\App\Models\Merchant\Entity::find('LJ3P0FyFtOULha'), 'payment_link')->all()
```

**Expected:**
```php
[
    'default_payment_handle' => [
        'default_payment_handle' => 'testhandle2026',
        'default_payment_handle_page_id' => '<nca-generated-id>',
    ]
]
```

### TC4: monolith_only → Proxy, No NCA Write

```bash
curl --location 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Proxy-State: monolith_only' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  ...
```

**Expected:**
- NCA logs: `MONOLITH_PROXYING_REQUEST` / `MONOLITH_PROXYING_RESPONSE`
- **No** `PH_NCA_CREATE_*` logs
- No entity in NCA DB

### TC5: Monolith Activation Flow

Use the test endpoint from Task 003 (tc=1) or trigger activation directly:

```bash
curl -s "https://api.dev.razorpay.in/v1/payment_handle_test_nca?merchant_id=LJ3P0FyFtOULha&tc=1" \
  --header 'rzpctx-dev-serve-user: ph-decomp'
```

**Expected:**
- API logs: `PAYMENT_HANDLE_CREATE_L1_ACTIVATION_START` → `NOCODE_SERVICE_REQUEST` → `PAYMENT_HANDLE_UPSERT_MERCHANT_SETTING`
- NCA creates handle in its own DB
- Monolith `merchant_settings` updated with new slug + ID

---

## Log Patterns

**NCA logs:**
```bash
kubectl logs -n no-code-apps deployment/no-code-apps-ph-decomp --tail=100 | grep -E "PH_NCA|PAYMENT_PAGE_CREATE|MONOLITH_PROXYING"
```

| Log | Meaning |
|-----|---------|
| `PAYMENT_PAGE_CREATE_REQUEST` with `view_type=PAYMENT_HANDLE` | NCA create started ✅ |
| `PH_NCA_CREATE_SUCCESS` | Entity saved to NCA DB ✅ |
| `MONOLITH_PROXYING_REQUEST` | Proxied to monolith (monolith_only state) |

**API logs:**
```bash
kubectl logs -n api deployment/api-web-ph-decomp --tail=100 | grep -E "PAYMENT_HANDLE|UPSERT"
```

| Log | Meaning |
|-----|---------|
| `PAYMENT_HANDLE_UPSERT_MERCHANT_SETTING` | merchant_settings synced ✅ |
| `PAYMENT_HANDLE_NCA_PROXY_STATE_RESULT` | Splitz gate decision logged |

---

## Open Questions / Decisions

- [ ] Does `CreatePaymentPage` in NCA handle slug validation (uniqueness check)? If not, NCA needs to call the `payment_handle_availability` equivalent before creating.
- [ ] What is the `paymentHandleHostedBaseUrl` value in NCA config? Ensure it matches monolith's value.
- [ ] Should the response from NCA `CreatePaymentHandle` include the `pl_`-prefixed ID or the raw ID? Monolith returns `pl_XXXXX` — NCA should match this format so `upsertDefaultPaymentHandleForMerchant` gets a consistent ID.
