# Service Identity vs Merchant Identity in Public APIs

## The Two-Layer Auth Pattern

Public checkout and payment APIs often need to answer two separate questions on every request:

```
Layer 1 (Gateway/Edge):  WHO is calling?
                         → Service/actor identity
                         → "This request came from the checkout service"

Layer 2 (Application):   FOR WHOM is this request?
                         → Merchant identity
                         → "This payment is for merchant X"
```

These are distinct problems solved by different mechanisms at different layers.

## Why They're Separate

A monolithic "just pass merchant_id" approach fails because:

- The **gateway** (Kong, Nginx, etc.) is stateless infrastructure — it can validate tokens but doesn't know your business objects (orders, invoices).
- The **application** has DB access to resolve business objects but shouldn't need to re-validate service-level trust on every call.

Each layer does what it's good at.

## Example: Checkout Order Flow

```
Browser (checkout.js)
│
│  keyless_header: "svc_token:ENCRYPTED..."   ← service identity
│  x_entity_id:   "order_XXXXX"              ← merchant identity
│
▼
API Gateway (Kong)
│  Decrypts keyless_header → "trusted service, acting for merchant M"
│  Sets X-Merchant-Id / X-Passport-Jwt-V1
│
▼
Application (Monolith)
│  Looks up order_XXXXX → belongs to merchant M
│  Both layers agree → proceed
```

## Both Are Needed

| Token | Alone | Problem |
|---|---|---|
| Service token only | Gateway trusts the service but app doesn't know which merchant | ✗ |
| Entity ID only | App can find the merchant but gateway has no service-level context for routes requiring it | ✗ |
| Both | ✓ | Each layer has what it needs |

## Analogy

An employee badge (`keyless_header`) gets you through the building door — it proves who you work for. But once inside, you still need to show a specific work order (`x_entity_id`) to prove what job you're authorized to do.

## When Only One Is Needed

Not all routes require both:
- **Read-only public routes** (e.g. fetch payment methods): service token is enough — gateway knows who's calling, no sensitive merchant action needed.
- **Routes with direct merchant key auth**: `key_id` + `key_secret` in the request replaces both layers — the key itself proves both the caller and the merchant.
