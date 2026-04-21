# Task 007: NCA-First Reads with Monolith Fallback

**Created:** 2026-02-23
**Status:** ⬜ Not Started
**Priority:** P0
**Repo:** `no-code-apps` (PR #1008 update)
**Spec:** [PaymentHandleDecomp_v2.md](/projects/payment-handles-decomp/PaymentHandleDecomp_v2.md) — Sections 5.3, 5.4, 6.3

---

## Context

Currently all read APIs in NCA use `ncaReadNotImplemented` — every request is proxied to monolith regardless of proxy state. This task implements actual NCA-side read logic.

The pattern is **NCA-first with monolith fallback**:
1. NCA checks its own `payment_handles` DB for the merchant's handle.
2. If found (new merchant, or migrated old merchant) → serve from NCA.
3. If not found (old merchant, pre-migration) → proxy to monolith as fallback.

`suggestion` and `amount_encryption` are stateless and can be implemented natively in NCA without any fallback.

**Dependency:** Task 006 must be merged first so that new merchant handles exist in NCA DB.

---

## How-To References

| What | Where |
|------|-------|
| **Spec (v2)** — strategy, read flow diagram, PR impact | [/projects/payment-handles-decomp/PaymentHandleDecomp_v2.md](/projects/payment-handles-decomp/PaymentHandleDecomp_v2.md) |
| **NCA code navigation** — controller, core, repo locations | [/projects/payment-handles-decomp/code/_index.md](/projects/payment-handles-decomp/code/_index.md) |
| **NCA navigation guide** — how to navigate Go code patterns | [/projects/payment-handles-decomp/code/guide-to-navigate-nca-code.md](/projects/payment-handles-decomp/code/guide-to-navigate-nca-code.md) |
| **Proxy states** — `monolith_only`, `nca_only`, fallback logic | [/projects/payment-handles-decomp/code/proxying.md](/projects/payment-handles-decomp/code/proxying.md) |
| **Monolith navigation** — finding `getPaymentHandleByMerchant`, `encryptAmountForPaymentHandle` | [/projects/payment-handles-decomp/code/monolith-navigation-guide.md](/projects/payment-handles-decomp/code/monolith-navigation-guide.md) |
| **Task 006** — must be done first; provides NCA DB writes + upsert merchant_settings | [/projects/payment-handles-decomp/tasks/006-nca-direct-writes.md](/projects/payment-handles-decomp/tasks/006-nca-direct-writes.md) |
| **Task 004** — previous read API task being superseded | [/projects/payment-handles-decomp/tasks/004-ph-read-apis.md](/projects/payment-handles-decomp/tasks/004-ph-read-apis.md) |
| **Deploy devstack** | [/docs/agent-actions/deploy-to-devstack.md](/docs/agent-actions/deploy-to-devstack.md) |
| **Hot reload** | [/docs/agent-actions/hot-reload-devspace.md](/docs/agent-actions/hot-reload-devspace.md) |

---

## Changes Required

### 1. `payment_handle_get` — NCA-first with monolith fallback

**File:** `internal/controllers/payment_handle.go`

Current:
```go
func (controller *PaymentHandleController) Get(req request.IRequest) response.IResponse {
    return controller.handleReadDualHandler.Handle(req, ncaReadNotImplemented)
}
```

New:
```go
func (controller *PaymentHandleController) Get(req request.IRequest) response.IResponse {
    proxyState := app.GetProxyStateFromContext(req.Ctx())
    if proxyState == constants.ProxyStateMonolithOnly {
        return controller.monolithProxy.Handle(req)
    }
    return controller.handleCore.GetPaymentHandle(req.Ctx(), req)
}
```

**File:** `internal/modules/payment_handle/core.go` — add `GetPaymentHandle`:

```go
func (c *Core) GetPaymentHandle(ctx context.Context, req IGetRequest) (*GetResponse, errors.IError) {
    merchantId := app.GetMerchantId(ctx)
    mode := app.GetMode(ctx)

    entity := GetEmptyEntity()
    findErr := c.repo.FindByMerchantIdAndMode(ctx, &entity, merchantId, mode)

    if findErr == nil {
        // Found in NCA DB — serve from NCA
        logger.CtxLog(ctx).Infow("PH_NCA_GET_FROM_NCA_DB", map[string]interface{}{
            "merchant_id":       merchantId,
            "payment_handle_id": entity.GetId(),
        })
        return buildGetResponse(entity), nil
    }

    if !isNotFoundError(findErr) {
        // Unexpected DB error
        return nil, findErr
    }

    // Not in NCA DB — fall back to monolith
    logger.CtxLog(ctx).Infow("PH_NCA_GET_FALLBACK_TO_MONOLITH", map[string]interface{}{
        "merchant_id": merchantId,
    })
    return nil, findErr // controller will proxy to monolith on nil response
}
```

**Controller fallback logic:**
```go
func (controller *PaymentHandleController) Get(req request.IRequest) response.IResponse {
    proxyState := app.GetProxyStateFromContext(req.Ctx())
    if proxyState == constants.ProxyStateMonolithOnly {
        return controller.monolithProxy.Handle(req)
    }

    resp, err := controller.handleCore.GetPaymentHandle(req.Ctx(), req)
    if err != nil || resp == nil {
        // Fallback to monolith (entity not in NCA DB — old merchant)
        logger.CtxLog(req.Ctx()).Infow("PH_GET_FALLBACK_TO_MONOLITH")
        return controller.monolithProxy.Handle(req)
    }

    return response.Json(req.GetContext(), resp, nil)
}
```

**`GetResponse` struct:**
```go
type GetResponse struct {
    Id       string `json:"id"`
    Slug     string `json:"slug"`
    ShortUrl string `json:"short_url"`
    Title    string `json:"title"`
    Url      string `json:"url"` // same as short_url
}
```

> **Note:** Verify the exact response shape against what monolith returns from `getPaymentHandleByMerchant`. Fields: `id`, `slug`, `url`, `title`. Match field names exactly.

---

### 2. Add `FindByMerchantIdAndMode` to repo

**File:** `internal/modules/payment_handle/repo.go`

```go
type IRepo interface {
    Create(ctx context.Context, entity *Entity) errors.IError
    Update(ctx context.Context, entity *Entity, fields ...string) errors.IError
    FindByIdAndMerchantIdAndMode(ctx context.Context, entity *Entity, id, merchantId, mode string) errors.IError
    FindByMerchantIdAndMode(ctx context.Context, entity *Entity, merchantId, mode string) errors.IError  // NEW
}
```

SQL:
```sql
SELECT * FROM payment_handles
WHERE merchant_id = ? AND mode = ? AND status = 'active'
LIMIT 1
```

> **Note:** If multiple handles exist for a merchant (shouldn't happen normally, but could during testing), return the most recent (`ORDER BY created_at DESC LIMIT 1`).

---

### 3. `payment_handle_availability` — Slug uniqueness check

**File:** `internal/controllers/payment_handle.go`

Current: `ncaReadNotImplemented` (always proxies to monolith)

The availability check (`GET /payment_handle/{slug}/exists`) answers: "is this slug already taken?"

**Strategy during migration transition:**
- A slug could be taken by a new merchant (in NCA DB) OR by an old merchant (in monolith custom URLs table, not yet migrated).
- Safest approach: **check NCA DB first, then also check monolith** for the full picture.
- Since availability must be globally accurate, proxy to monolith always for now (until data migration is complete). After full migration, NCA can own this entirely.

```go
func (controller *PaymentHandleController) CheckAvailability(req request.IRequest) response.IResponse {
    // During migration: always check monolith (which has the full slug universe).
    // After migration: implement NCA-native check.
    return controller.monolithProxy.Handle(req)
}
```

**Post-migration (future):**
```go
func (controller *PaymentHandleController) CheckAvailability(req request.IRequest) response.IResponse {
    slug := req.GetPathParam("slug")
    exists, err := controller.handleCore.SlugExists(req.Ctx(), slug)
    if err != nil {
        return controller.monolithProxy.Handle(req) // fallback
    }
    return response.Json(req.GetContext(), map[string]bool{"exists": exists}, nil)
}
```

---

### 4. `payment_handle_suggestion` — NCA-native implementation

**File:** `internal/controllers/payment_handle.go`

Suggestions are generated from the merchant's billing label — no stored data needed.

Current: `ncaReadNotImplemented`

New:
```go
func (controller *PaymentHandleController) Suggestion(req request.IRequest) response.IResponse {
    return controller.handleCore.SuggestPaymentHandles(req.Ctx(), req)
}
```

**File:** `internal/modules/payment_handle/core.go` — add `SuggestPaymentHandles`:

Algorithm (mirrors monolith):
1. Get merchant billing label from `merchantModule.GetMerchantDetails(ctx)`
2. Sanitize to slug format (lowercase, alphanumeric + hyphens, max 20 chars)
3. If slug not taken → add to suggestions
4. Generate up to `count` variants by appending random numbers (1-10000)
5. For each candidate, check `c.repo.SlugExists(ctx, candidate)` and skip if taken

```go
func (c *Core) SuggestPaymentHandles(ctx context.Context, req ISuggestionRequest) (*SuggestionResponse, errors.IError) {
    merchantId := app.GetMerchantId(ctx)
    mode := app.GetMode(ctx)

    count := req.GetCount() // default 3, max 10
    merchantDetails, err := c.merchantModule.GetCore().GetMerchantDetails(ctx, merchantId, mode)
    if err != nil {
        return nil, err
    }

    base := slugify(merchantDetails.BillingLabel)
    suggestions := []string{}

    if !c.repo.SlugExists(ctx, base) {
        suggestions = append(suggestions, base)
        count--
    }

    for count > 0 {
        candidate := fmt.Sprintf("%s%d", base, rand.Intn(10000)+1)
        if len(candidate) > 20 {
            candidate = candidate[:20]
        }
        if !c.repo.SlugExists(ctx, candidate) {
            suggestions = append(suggestions, candidate)
            count--
        }
    }

    return &SuggestionResponse{Suggestions: suggestions}, nil
}
```

> **Note:** `SlugExists` must check both NCA DB and monolith (during migration) OR just NCA DB (post-migration). During transition, proxy suggestion calls to monolith to be safe — slug universe is split.

**Revised strategy:** During migration, keep proxying suggestion to monolith. Mark as NCA-native for after full migration. Avoids suggesting a slug that's taken on monolith side.

---

### 5. `payment_handle_amount_encryption` — NCA-native implementation

**File:** `internal/controllers/payment_handle.go`

Encrypts a custom amount value. Stateless — no DB lookup needed.

Current: `ncaReadNotImplemented`

New:
```go
func (controller *PaymentHandleController) AmountEncryption(req request.IRequest) response.IResponse {
    return controller.handleCore.EncryptAmount(req.Ctx(), req)
}
```

**File:** `internal/modules/payment_handle/core.go`:

```go
func (c *Core) EncryptAmount(ctx context.Context, req IAmountEncryptionRequest) (*AmountEncryptionResponse, errors.IError) {
    amount := req.GetAmount()
    encrypted, err := c.encryptor.EncryptAmount(ctx, amount)
    if err != nil {
        return nil, err
    }
    return &AmountEncryptionResponse{EncryptedAmount: encrypted}, nil
}
```

> **Note:** Check how monolith encrypts amounts in `encryptAmountForPaymentHandle` and use the same algorithm/key. This is critical for correctness — wrong encryption breaks the payment flow.

**File to check:** `app/Models/PaymentLink/Core.php::encryptAmountForPaymentHandle` — understand the encryption key and algorithm, replicate in NCA.

---

### 6. Update `ICore` interface

```go
type ICore interface {
    CreatePaymentHandle(ctx context.Context, req ICreateRequest) (*CreateResponse, errors.IError)
    UpdatePaymentHandle(ctx context.Context, req IUpdateRequest) (*UpdateResponse, errors.IError)
    GetPaymentHandle(ctx context.Context, req IGetRequest) (*GetResponse, errors.IError)          // NEW
    SuggestPaymentHandles(ctx context.Context, req ISuggestionRequest) (*SuggestionResponse, errors.IError) // future
    EncryptAmount(ctx context.Context, req IAmountEncryptionRequest) (*AmountEncryptionResponse, errors.IError) // future
}
```

---

## Test Cases

### Verification Columns

| Column | Meaning |
|--------|---------|
| **Deployed** | Devstack running with updated NCA commit (post Task 006) |
| **TC1** | `GET /v1/payment_handle` for **new merchant** (data in NCA DB) → returns NCA data, no monolith call |
| **TC2** | `GET /v1/payment_handle` for **old merchant** (data NOT in NCA DB) → falls back to monolith |
| **TC3** | `GET /v1/payment_handle` in `monolith_only` state → always proxies to monolith |
| **TC4** | `GET /v1/payment_handle/{slug}/exists` → proxies to monolith (correct during migration) |
| **TC5** | `GET /v1/payment_handle/suggestion` → proxies to monolith (correct during migration) |
| **TC6** | `POST /v1/payment_handle/custom_amount` → NCA encrypts natively, result matches monolith |
| **TC7** | Monolith activation flow reads via NCA (`getPaymentHandleByMerchantNCA`) → NCA reads from DB for new merchant |
| **LogCheck** | `PH_NCA_GET_FROM_NCA_DB` vs `PH_NCA_GET_FALLBACK_TO_MONOLITH` logs |

| # | Test | Deployed | TC1 | TC2 | TC3 | TC4 | TC5 | TC6 | TC7 | LogCheck | Status |
|---|------|----------|-----|-----|-----|-----|-----|-----|-----|----------|--------|
| 1 | Get: new merchant served from NCA | ⬜ | ⬜ | - | - | - | - | - | - | ⬜ | ⬜ |
| 2 | Get: old merchant falls back to monolith | ⬜ | - | ⬜ | - | - | - | - | - | ⬜ | ⬜ |
| 3 | Get: monolith_only always proxies | ⬜ | - | - | ⬜ | - | - | - | - | ⬜ | ⬜ |
| 4 | Availability proxies to monolith | ⬜ | - | - | - | ⬜ | - | - | - | ⬜ | ⬜ |
| 5 | Suggestion proxies to monolith | ⬜ | - | - | - | - | ⬜ | - | - | ⬜ | ⬜ |
| 6 | Encryption: NCA result matches monolith | ⬜ | - | - | - | - | - | ⬜ | - | ⬜ | ⬜ |
| 7 | Activation read path: NCA serves new merchant | ⬜ | - | - | - | - | - | - | ⬜ | ⬜ | ⬜ |

---

## Step 1: Pre-requisite

**Task 006 must be deployed first** — need at least one merchant with a handle created directly in NCA DB to test TC1.

Create a test merchant handle via NCA:
```bash
curl --location 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
  --header 'X-Razorpay-Mode: live' \
  --header 'X-Proxy-State: nca_only' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  --data-raw '{"slug": "nca-test-handle"}'
```

Note the returned `id` for DB verification.

---

## Step 2: Deploy Updated NCA

```bash
cd ~/rzp/kube-manifests/helmfile
helmfile sync -l name=no-code-apps-ph-decomp
kubectl get pods -n no-code-apps -l devstack_label=ph-decomp
```

---

## Step 3: Test Cases

### TC1: GET for New Merchant (NCA DB)

```bash
# Merchant LJ3P0FyFtOULha created handle in Task 006 via NCA
curl --location 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
  --header 'X-Razorpay-Mode: live' \
  --header 'X-Proxy-State: nca_only' \
  --header 'rzpctx-dev-serve-user: ph-decomp'
```

**Expected:**
- Response: `{id, slug: "nca-test-handle", short_url, title}`
- NCA logs: `PH_NCA_GET_FROM_NCA_DB`
- **No** `MONOLITH_PROXYING_REQUEST` log

### TC2: GET for Old Merchant (Not in NCA DB)

```bash
# Use a different merchant ID that has NO handle in NCA DB
curl --location 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Razorpay-Merchant-Id: <old-merchant-id>' \
  --header 'X-Proxy-State: nca_only' \
  --header 'rzpctx-dev-serve-user: ph-decomp'
```

**Expected:**
- NCA logs: `PH_NCA_GET_FALLBACK_TO_MONOLITH` then `MONOLITH_PROXYING_REQUEST`
- Response comes from monolith merchant_settings

### TC6: Amount Encryption Matches Monolith

```bash
# Call NCA
NCA_RESULT=$(curl -s --location 'https://nca.dev.razorpay.in/v1/payment_handle/custom_amount' \
  --header 'X-Proxy-State: nca_only' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  --data-raw '{"amount": 50000}')

# Call monolith directly for same amount
MONO_RESULT=$(curl -s --location 'https://api.dev.razorpay.in/v1/payment_handle/custom_amount' \
  --data-raw '{"amount": 50000}')

echo "NCA: $NCA_RESULT"
echo "Monolith: $MONO_RESULT"
```

**Expected:** `encrypted_amount` field matches between NCA and monolith responses.

### TC7: Monolith Activation Flow Reads via NCA

```bash
curl -s "https://api.dev.razorpay.in/v1/payment_handle_test_nca?merchant_id=LJ3P0FyFtOULha&tc=2" \
  --header 'rzpctx-dev-serve-user: ph-decomp'
```

**Expected (with Splitz returning nca_only for this merchant):**
- API logs: `PAYMENT_HANDLE_GET_REQUEST_INITIATED`, `NOCODE_SERVICE_REQUEST` to NCA
- NCA logs: `PH_NCA_GET_FROM_NCA_DB` (merchant has handle in NCA DB)
- Response contains correct handle data

---

## Log Patterns

**NCA logs:**
```bash
kubectl logs -n no-code-apps deployment/no-code-apps-ph-decomp --tail=100 | grep -E "PH_NCA_GET|MONOLITH_PROXYING"
```

| Log | Meaning |
|-----|---------|
| `PH_NCA_GET_FROM_NCA_DB` | Served from NCA DB ✅ |
| `PH_NCA_GET_FALLBACK_TO_MONOLITH` | Entity not found in NCA, falling back ✅ |
| `MONOLITH_PROXYING_REQUEST` on GET /payment_handle | Fallback proxy to monolith |

**API logs:**
```bash
kubectl logs -n api deployment/api-web-ph-decomp --tail=100 | grep -E "PAYMENT_HANDLE_GET|NOCODE_SERVICE"
```

---

## Parity Check: NCA Response vs Monolith Response

Before enabling reads from NCA, verify response shape parity:

| Field | Monolith `getPaymentHandleByMerchant` | NCA `GetPaymentHandle` |
|-------|--------------------------------------|------------------------|
| `id` | `pl_XXXXX` (public page ID) | `pl_XXXXX` (same format) |
| `slug` | handle slug string | handle slug string |
| `url` | `https://rzp.io/i/<slug>` | `https://rzp.io/i/<slug>` |
| `title` | merchant billing label | merchant billing label |

Any field mismatch will cause diff checker failures during read shadowing (Task 008).

---

## Future: Read Shadowing (Task 008)

Once this task is complete and NCA is serving reads for new merchants:

1. Enable read shadowing: NCA calls both its DB AND monolith, compares responses, returns monolith response.
2. Run for 2-4 days, monitor `DIFF_CHECKER_*` logs for any mismatches.
3. Fix parity issues found during shadowing.
4. Cut over: return NCA response for all merchants (post-migration).

Shadowing is not in scope for this task — just implement the NCA-first read with fallback.
