---
tags: [web-auth, checkout, merchant-identity, service-identity, keyless]
status: Answered
related:
  - ../topics/service_vs_merchant_identity_in_public_apis.md
  - ../topics/entity_based_auth_without_api_keys.md
  - ../topics/nacl_box_service_identity_tokens.md
---

# Why Is Public Checkout Auth So Convoluted Just to Get a Merchant ID?

## ❓ The Core Question

A public checkout API (e.g. `checkout/order`) ultimately just needs to know which merchant the request is for. Why are there two separate auth mechanisms — an encrypted service token and an entity ID lookup — instead of just passing `merchant_id` directly?

## 🧠 The Learning Log

### Initial Assumption
The `keyless_header` (encrypted blob) and `x_entity_id` (order ID) are both about identifying the merchant. Feels over-engineered.

### 🔄 Refinement: They Solve Different Problems at Different Layers

**My Misconception:** Both tokens are redundant ways to identify the merchant.

**The Correction:** They answer two completely different questions:

```
keyless_header  →  WHO is making the request (service/actor identity)
                   Verified at: Edge/API Gateway
                   "This came from the trusted checkout service"

x_entity_id     →  FOR WHOM is the request (merchant identity)
                   Verified at: Application layer
                   "This order belongs to merchant X"
```

**Key Insight:** In a microservice architecture, the gateway and the application have separate concerns. The gateway needs to know which *service* to trust; the application needs to know which *merchant* to charge. Neither alone is sufficient.

See: [service_vs_merchant_identity_in_public_apis.md](../topics/service_vs_merchant_identity_in_public_apis.md)

---

### 🔄 Refinement: Why Not Just Pass merchant_id Directly?

**My Misconception:** `merchant_id` is visible in the page anyway, so why not just pass it?

**The Correction:** You can't trust a raw `merchant_id` sent from the browser — anyone can forge it. The auth mechanisms provide *unforgeable proof of association*:

- `key_id` → a real DB record that can be active, expired, or revoked. Validated against a key store.
- `x_entity_id` → an order/invoice that exists in the DB, tied to a specific merchant. You can't reference an entity belonging to a different merchant.

A raw `merchant_id` string is just a string. There's no way to verify "did this merchant authorize this checkout?" without a proof mechanism.

**Key Insight:** Auth in public APIs isn't always about keeping secrets — it's about having *verifiable, revocable identifiers*. See: [entity_based_auth_without_api_keys.md](../topics/entity_based_auth_without_api_keys.md)

---

### 🔄 Refinement: Is keyless_header Actually Secure if the Page Is Public?

**My Misconception:** The encrypted keyless_header prevents unauthorized access.

**The Correction:** Since the hosted page is public, anyone can fetch a fresh `keyless_header` from it. The actual protections are:

1. **Replay prevention**: Tokens contain a timestamp and expire in minutes.
2. **Forged service identity prevention**: Only the trusted service (holding the private key) can generate valid tokens. Random scripts can't produce them.

The security model is: *"I can't pretend to be the checkout service, and I can't reuse an old token."* Not: *"I can't get a valid token at all."*

**Key Insight:** For public-facing flows, the value of service identity tokens is primarily for routing/rate-limiting/auditability and to prevent *impersonation of the service*, not to gate access to the API entirely.

See: [nacl_box_service_identity_tokens.md](../topics/nacl_box_service_identity_tokens.md)
