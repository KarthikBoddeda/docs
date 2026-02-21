# Task 004: NCA Payment Handle Read APIs

**Created:** 2026-02-21  
**Status:** 🟢 Completed  
**Priority:** P0  
**DevRev:** [ISS-1604277](https://app.devrev.ai/razorpay/works/ISS-1604277)  
**PR:** [no-code-apps#1008](https://github.com/razorpay/no-code-apps/pull/1008)  
**Branch:** `ph-decomp/nca-handle-read-apis`  

---

## What This Task Does

Adds NCA routing + handlers for all 4 payment handle read APIs, wired to use the **payment_handle_proxy_state experiment** (not the page experiment).

| Route | Method | Path | Route Name |
|-------|--------|------|------------|
| Get handle | GET | `/v1/payment_handle` | `payment_handle_get` |
| Check availability | GET | `/v1/payment_handle/:slug/exists` | `payment_handle_availability` |
| Suggestion | GET | `/v1/payment_handle/suggestion` | `payment_handle_suggestion` |
| Amount encryption | POST | `/v1/payment_handle/custom_amount` | `payment_handle_amount_encryption` |

---

## Changes

### `internal/constants/route_constants.go`
Added 4 new route name constants for the read APIs.

### `internal/monolith_decomp/dual_write_handlers/payment_handle_read_handler.go` (new)
`DualWriteHandlerForHandleReads` — uses `HandleReadProxyStateGetter` which calls `GetPaymentHandleProxyStateFromSplitzAndSetToRequestContext` (handle experiment, not page experiment).

### `internal/controllers/payment_handle.go`
Added `Get`, `CheckAvailability`, `Suggestion`, `AmountEncryption` controller methods. All currently use `ncaReadNotImplemented` as the NCA operation (proxy to monolith in all states).

### `internal/router/payment_handle_routes.go`
Added route configs for all 4 read APIs. Routes are ordered to avoid Gin conflicts:
- `/suggestion` and `/:slug/exists` registered BEFORE the generic `""` GET route.

### `internal/services/api/service.go`
Added proxy switch cases and URL constants for all 4 routes.

### `internal/monolith_decomp/diffs/configs.go`
Added `paymentHandleResponseComparator` entries for all 4 new routes.

### `internal/database/migrations/20260221000000_create_payment_handles_table.go`
DB migration for `payment_handles` table (for non-devstack environments).

---

## Notes

- **pages_view_by_slug** and **merchant_details** APIs already existed in NCA and already handle payment handle entities — no changes needed.
- All 4 read APIs currently return monolith response in all proxy states. NCA-side read implementation is a future task.
- No behaviour change until Kong upstream-override rollout is enabled (see Task 005).
