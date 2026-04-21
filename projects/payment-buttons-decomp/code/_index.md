# Payment Buttons Decomp — Code Navigation

This folder documents the code structure for the payment buttons decomposition project.
Payment buttons share the same NCA infrastructure as payment pages.

> **Note:** Payment buttons decomp is in early planning. The code structure will mirror payment pages decomp closely. This file will be updated as implementation progresses.

## Structure (planned)

| File | What it covers |
|------|---------------|
| `_index.md` | This file — overview |
| `guide-to-navigate-nca-code.md` | How to navigate NCA Go codebase — patterns, pitfalls, datatypes |
| `monolith-navigation-guide.md` | How to navigate the PHP monolith for payment link / button code |
| `proxying.md` | Proxy states, dual-write handler, diff calculation |

## Key Differences from Payment Pages

Payment buttons (`view_type = "button"`) differ from pages in:
- They use `TypePaymentButton` / `NocodeType("button")` as view type
- Some button-specific APIs exist (e.g., `payment_button_create`, `payment_button_get`)
- Buttons can also be `subscription_button` subtype

## Shared Infrastructure

All the proxy state, dual-write, and diff infrastructure is shared with payment pages:
- Same `GenericDualWriteHandler` base
- Same `IPaymentPageCore` for proxy operations
- Same `NCASupportedViewTypes` (add `"button"` when decomp starts)
- Separate splitz experiment needed: `payment_button_proxy_state`

## Key Constants

```go
nocode.TypePaymentButton   = NocodeType("button")
nocode.ButtonViewType      = "button"
```

## Reference

For the full pattern, see `/projects/payment-pages-decomp/code/_index.md` and `/projects/payment-handles-decomp/code/_index.md`.
