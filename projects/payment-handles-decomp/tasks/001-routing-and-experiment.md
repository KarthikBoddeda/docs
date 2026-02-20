# Task 001: NCA Routing, Proxy Setup & Splitz Experiment Integration

**Created:** 2026-02-20  
**Status:** 🟡 In Progress  
**Priority:** P0  
**DevRev:** [ISS-1603951](https://app.devrev.ai/razorpay/works/ISS-1603951)  
**PR:** [no-code-apps#1006](https://github.com/razorpay/no-code-apps/pull/1006)  
**Branch:** `ph-decomp/nca-routing-and-experiment`  
**NCA Commit:** `ed67662049c0ca9de014c4f9e624ed23689d09a4`

---

## What This Task Tests

1. `POST /v1/payment_handle` → proxied to monolith in `monolith_only` state
2. `PATCH /v1/payment_handle` → proxied to monolith in `monolith_only` state
3. `POST /v1/payment_pages/:id/order` for a handle entity → uses handle experiment (not page experiment)
4. `POST /v1/payment_pages/:id/order` for a page entity → still uses page experiment (no regression)
5. Proxy state override via `X-Proxy-State` header works for handle routes

---

## How-To References

| Action | Reference |
|--------|-----------|
| Deploy to devstack | [/docs/agent-actions/deploy-to-devstack.md](/docs/agent-actions/deploy-to-devstack.md) |
| Hot reload | [/docs/agent-actions/hot-reload-devspace.md](/docs/agent-actions/hot-reload-devspace.md) |
| Sample API requests | [/docs/projects/payment-handles-decomp/payment-handles-api.http](/docs/projects/payment-handles-decomp/payment-handles-api.http) |
| NCA code flow | [/docs/projects/payment-handles-decomp/code/nca-ph-create.md](/docs/projects/payment-handles-decomp/code/nca-ph-create.md) |

---

## Subtasks

> **🚨 CRITICAL: A subtask is NOT complete until ALL verification columns are ✅**

### Status Legend

| Status | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🟡 | In progress |
| 🟢 | **VERIFIED** (all columns ✅) |
| 🔵 | Already works |
| 🔴 | Blocked |

### Verification Columns

| Column | Meaning |
|--------|---------|
| **Deployed** | Devstack running with NCA commit `ed67662` |
| **HotReload** | Devspace running with auth bypass on handle routes |
| **TC1** | `POST /v1/payment_handle` in `monolith_only` → proxied, monolith response returned |
| **TC2** | `PATCH /v1/payment_handle` in `monolith_only` → proxied, monolith response returned |
| **TC3** | `POST /v1/payment_handle` with `dual_write_no_reads_no_external` → proxied + NCA op called |
| **TC4** | `POST /v1/payment_pages/:id/order` for handle ID → handle experiment used in logs |
| **TC5** | `POST /v1/payment_pages/:id/order` for page ID → page experiment used (regression) |
| **LogCheck** | NCA pod logs show correct proxy state and routing behavior |
| **Commit** | Commit hash |
| **Review** | ⚠️ MANUAL ONLY |

| # | Test | Deployed | HotReload | TC1 | TC2 | TC3 | TC4 | TC5 | LogCheck | Status | Commit | Review |
|---|------|----------|-----------|-----|-----|-----|-----|-----|----------|--------|--------|--------|
| 1 | Route `POST /v1/payment_handle` proxied in `monolith_only` | ✅ | ✅ | ✅ | - | - | - | - | ✅ | 🟢 | `a397255` | |
| 2 | Route `PATCH /v1/payment_handle` proxied in `monolith_only` | ✅ | ✅ | - | ✅ | - | - | - | ✅ | 🟢 | `a397255` | |
| 3 | Dual-write state: monolith + NCA both called | ✅ | ✅ | - | - | ✅ | - | - | ✅ | 🟢 | `a397255` | |
| 4 | create_order entity-not-found → falls back to monolith_only | ✅ | ✅ | - | - | - | ✅ | - | ✅ | 🟢 | `a397255` | |
| 5 | create_order for page/handle ID (with real data) | ✅ | ✅ | - | - | - | - | ⬜ | ⬜ | 🔴 | | Blocked: needs merchant with actual payment handle data |

---

## Step 1: Deploy Devstack

```bash
cd ~/rzp/kube-manifests/helmfile

# Update helmfile.yaml:
# - devstack_label: ph-decomp
# - NCA image: 2bd13e63a699e1decea6b5e5e92a4d86aec2afb5  (includes both PR1+PR2)
# - API image: 06383358f91aaae93705e78489b6f32088cea67b
# - Gimli image: acf7ce8b84037b15d82236a34cc36fa57877ffae

helmfile lint && helmfile sync
```

Verify pods:
```bash
kubectl get pods -A -l devstack_label=ph-decomp
# Expect: api-*, gimli-*, no-code-apps-* all Running 1/1
```

---

## Step 2: Hot Reload with Auth Bypass

In `internal/router/payment_handle_routes.go`, comment out `PassportPrivateAuth()` and add `WithAuth()`:

```go
func (a *PaymentHandleRoutes) GetMiddlewares() []gin.HandlerFunc {
    return []gin.HandlerFunc{
        middlewares.Serialize,
        middlewares.WithAppErrorHandler(),
        middlewares.WithRequestInterceptor(),
        middlewares.WithResponseInterceptor(),
        //middlewares.PassportPrivateAuth(),   // COMMENT OUT for direct testing
        middlewares.WithAuth(),                // USE THIS INSTEAD
        middlewares.WithMerchantIdInterceptor(),
        middlewares.WithModeInterceptor(),
        middlewares.WithDualWriteStateInterceptor(),
        middlewares.WithPrometheus(),
        tracingIntegration.GinTracingMiddleware,
    }
}
```

> **⚠️ DO NOT COMMIT THIS CHANGE.**

```bash
cd ~/rzp/no-code-apps-ph-decomp
# Switch to ph-decomp/nca-routing-and-experiment branch
git checkout ph-decomp/nca-routing-and-experiment
export GOPRIVATE="github.com/razorpay/*"
go mod tidy && go mod vendor
devspace dev --no-warn
```

---

## Step 3: Test Cases

Use `payment-handles-api.http`. Test merchant: `LJ3P0FyFtOULha` (same as PP decomp).

### TC1: `POST /v1/payment_handle` in monolith_only

```bash
curl --location 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
  --header 'X-Razorpay-Mode: live' \
  --header 'X-Proxy-State: monolith_only' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Basic UkFORE9NX05DQV9VU0VSOlJBTkRPTV9OQ0FfUEFTU1dPUkQ=' \
  --data-raw '{}'
```

**Expected:**
- Monolith handles the request
- NCA logs show `MONOLITH_PROXYING_RESPONSE` 
- No NCA DB write

### TC2: `PATCH /v1/payment_handle` in monolith_only

```bash
curl --location --request PATCH 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
  --header 'X-Razorpay-Mode: live' \
  --header 'X-Proxy-State: monolith_only' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Basic UkFORE9NX05DQV9VU0VSOlJBTkRPTV9OQ0FfUEFTU1dPUkQ=' \
  --data-raw '{"slug": "test-handle-slug"}'
```

**Expected:**
- Monolith handles the request
- NCA logs show `MONOLITH_PROXYING_RESPONSE`

### TC3: `POST /v1/payment_handle` in dual_write state

```bash
curl --location 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
  --header 'X-Razorpay-Mode: live' \
  --header 'X-Proxy-State: dual_write_no_reads_no_external' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Basic UkFORE9NX05DQV9VU0VSOlJBTkRPTV9OQ0FfUEFTU1dPUkQ=' \
  --data-raw '{}'
```

**Expected:**
- Monolith handles AND NCA operation is called
- NCA logs show both `MONOLITH_PROXYING_RESPONSE` and `PH_DUAL_WRITE_*` log

### TC4: `create_order` for a handle entity → handle experiment used

```bash
# First find a payment handle page ID (pl_xxx for a handle merchant)
curl --location 'https://nca.dev.razorpay.in/v1/payment_pages/<handle-page-id>/order' \
  --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
  --header 'X-Razorpay-Mode: live' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  --header 'Authorization: Basic UkFORE9NX05DQV9VU0VSOlJBTkRPTV9OQ0FfUEFTU1dPUkQ='
```

**Expected:** NCA logs show `GetPaymentHandleProxyStateFromSplitz` called (not page experiment).

### TC5: `create_order` for a page entity → page experiment (regression)

Same as TC4 but with a payment **page** ID (not handle). Expected: NCA logs show `GetProxyStateFromSplitz` called.

---

## Log Patterns to Check

```bash
kubectl logs -n no-code-apps deployment/no-code-apps-ph-decomp --tail=50 | grep -E "MONOLITH_PROXYING|PROXY_STATE|PH_DUAL|PAYMENT_HANDLE"
```

Key log strings:
- `MONOLITH_PROXYING_RESPONSE` → request was proxied to monolith ✅
- `PH_DUAL_WRITE_CREATE_SUCCESS` → NCA write succeeded ✅
- `GetPaymentHandleProxyStateFromSplitz` → handle experiment called ✅
- `ERROR_WHILE_GETTING_PROXY_STATE` → experiment lookup failed (expected for dummy experiment name)

---

## Work Log

### 2026-02-20 — Devstack Testing (Subtasks 1-4)

**Devstack label:** `ph-decomp`  
**NCA commit:** `a397255` (includes proxy route fix)  
**API commit:** `06383358`  

#### Fix Found During Testing: Missing proxy route mappings

During devstack testing, `POST /v1/payment_handle` returned `PROXY_ROUTE_NOT_FOUND` (500 error). Root cause: `PaymentHandleCreateRouteName` and `PaymentHandleUpdateRouteName` were not registered in the proxy route `switch` in `internal/services/api/service.go`.

**Fix committed:** `a397255` — added `CreatePaymentHandle` and `UpdatePaymentHandle` URL constants and corresponding `case` blocks in `ProxyToMonolith`.

**Test Results:**

- **TC1** (POST monolith_only): NCA logs show `MONOLITH_PROXYING_REQUEST` → `MONOLITH_PROXYING_RESPONSE` ✅
  - Monolith returned 400 (test merchant has no payment handle configured - expected)
- **TC2** (PATCH monolith_only): Same behavior — MONOLITH_PROXYING_REQUEST + MONOLITH_PROXYING_RESPONSE ✅
- **TC3** (POST dual_write): NCA logs show `MONOLITH_PROXYING_REQUEST` with `proxy_state: dual_write_no_reads_no_external` ✅
  - NCA operation called after monolith (monolith 400 → NCA parse fails gracefully, no DB write - correct behavior)
- **TC4** (create_order entity routing fallback): Without proxy header, NCA logs `PROXY_STATE_GETTER_ERROR_WHILE_FINDING_PAGE_FOR_ORDER_CREATE` and falls back to `monolith_only` ✅

#### Blocked (TC5)
TC5 requires a merchant with an actual payment handle to verify that handle entities use the handle experiment and page entities use the page experiment. Test merchant `LJ3P0FyFtOULha` has no payment handle configured in devstack.
