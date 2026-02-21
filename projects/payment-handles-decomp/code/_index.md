# Payment Handles Decomp — Code Navigation

This folder documents the code structure for the payment handle decomposition project.
Payment handles share the same NCA infrastructure as payment pages (same `PaymentPageCore`, same dual-write framework).

## Structure

| File | What it covers |
|------|---------------|
| `_index.md` | This file — overview |
| `guide-to-navigate-nca-code.md` | How to navigate NCA Go codebase — patterns, pitfalls, datatypes |
| `monolith-navigation-guide.md` | How to navigate the PHP monolith for payment link / handle code |
| `proxying.md` | Proxy states, dual-write handler, diff calculation |
| `api-ph-create.md` | Monolith code flow for `payment_handle_create` |
| `nca-ph-create.md` | NCA code flow for `payment_handle_create` |

## Key Code Locations

### NCA (`no-code-apps`)

| Concern | Location |
|---------|----------|
| Routes | `internal/router/payment_handle_routes.go` |
| Controller | `internal/controllers/payment_handle.go` |
| Handle-specific dual write handler | `internal/monolith_decomp/dual_write_handlers/payment_handle_write_handler.go` |
| Handle core (DB operations) | `internal/modules/payment_handle/core.go` |
| Handle entity / model | `internal/modules/payment_handle/model.go` |
| Handle repo | `internal/modules/payment_handle/repo.go` |
| Proxy state methods (handle experiment) | `internal/modules/payment_page/core.go` — `GetPaymentHandleProxyStateFromSplitz*` |
| Experiment config | `internal/config/config.go` — `PaymentHandleProxyStateExperimentName` |
| Route constants | `internal/constants/route_constants.go` — `PaymentHandleCreateRouteName`, `PaymentHandleUpdateRouteName` |

### Monolith (`api`)

| Concern | Location |
|---------|----------|
| HTTP calls to NCA | `app/Services/NoCodeAppsService.php` — `createPaymentHandle()`, `getPaymentHandle()` |
| NCA wrapper in service | `app/Models/PaymentLink/Service.php` — `createPaymentHandleNCA()`, `getPaymentHandleByMerchantNCA()` |
| NCA wrapper in core | `app/Models/PaymentLink/Core.php` — `getPaymentHandleByMerchantNCA()` |
| Merchant activation flow | `app/Models/Merchant/Activate.php` — calls `createPaymentHandleNCA` |
| Dashboard slug fetch | `app/Models/Merchant/Core.php` — calls `getPaymentHandleByMerchantNCA` |
| Segment analytics | `app/Models/Merchant/Detail/Core.php` — calls `getPaymentHandleByMerchantNCA` |

## Key Concepts

### Proxy States
Payment handles use a **separate** splitz experiment from payment pages:
- Payment pages: `PaymentPageProxyStateExperimentName` (already exists)
- Payment handles: `PaymentHandleProxyStateExperimentName` (TODO: create in Splitz)

The proxy state constants (`monolith_only`, `dual_write_no_reads_no_external`, etc.) are the same as for payment pages — defined in `internal/modules/payment_page/constants.go`.

### ID Reuse
During dual write, NCA stores the same entity ID as the monolith uses. The `pl_` prefix is stripped from the monolith response ID and stored as the raw ID in NCA DB. This ensures data consistency when switching proxy states.

### View Type
Payment handles have `view_type = "payment_handle"` (constant: `nocode.PaymentHandleViewType` = `"payment_handle"`).

### create_order routing
`payment_page_create_order` (shared between pages and handles) now routes to the correct experiment based on entity `view_type`:
- entity is `payment_handle` → uses handle experiment
- entity is `page` / `button` → uses page experiment

See `GetProxyStateForCreateOrderByEntityId` in `internal/modules/payment_page/core.go`.

## PRs

| PR | Scope |
|----|-------|
| [NCA PR 1 #1006](https://github.com/razorpay/no-code-apps/pull/1006) | Routing, proxy setup, splitz integration |
| [NCA PR 2 #1007](https://github.com/razorpay/no-code-apps/pull/1007) | create/update NCA implementation + ID reuse |
| [Monolith PR #64786](https://github.com/razorpay/api/pull/64786) | Replace monolith fn calls with NCA HTTP calls |

## Adding New Handle APIs

Follow the same pattern as payment pages:
1. Add route constant to `route_constants.go`
2. Add route to `payment_handle_routes.go`
3. Add handler method to `payment_handle.go` controller
4. Add NCA logic to `payment_handle/core.go`
5. Add diff config to `diffs/configs.go`

See `/projects/payment-pages-decomp/code/_index.md` for the payment pages equivalent guide.
