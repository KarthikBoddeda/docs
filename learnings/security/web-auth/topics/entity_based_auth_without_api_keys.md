# Entity-Based Auth Without API Keys

## The Problem

Public-facing checkout pages need to make API calls that are scoped to a specific merchant — but they shouldn't expose the merchant's API key in the browser (where anyone can read it).

## The Solution: Use an Entity as Proof

Instead of authenticating with a key, pass a **reference to a business entity** (order, invoice, subscription) that was created server-side and is irrevocably tied to a specific merchant in the DB.

```
# Traditional key-based:
POST /checkout/order
  key_id=rzp_live_XXXX          ← merchant's key, visible in page source

# Entity-based:
POST /checkout/order
  x_entity_id=order_YYYY        ← order created server-side for this merchant
```

The server resolves `order_YYYY → merchant M` via a DB lookup. No key needed.

## Why This Is Secure

The entity ID is **not a secret**, but it's still an **unforgeable proof of merchant association**:

- You can't reference `order_YYYY` and claim it belongs to a different merchant — the DB has the ground truth.
- You can't make up an `order_ZZZZ` that doesn't exist.
- Even if an attacker has the entity ID, all they can do is make a payment *for that specific order* — which is the intended action anyway.

## Why a Public key_id Isn't Meaningless Either

`key_id` (e.g. `rzp_live_ABCDEF`) is visible in the page, so someone could copy it. But it's still useful because:

1. **Validation**: The server checks it's a real, non-expired, non-revoked key. A raw `merchant_id` string has no such check.
2. **Revocability**: A compromised key can be rotated. A merchant_id can't.
3. **For sensitive operations**: `key_id` alone isn't enough — you also need `key_secret` (never exposed). Public endpoints only accept `key_id` without secret because they're low-risk.

## The Hierarchy

```
Most secure:    key_id + key_secret (full API auth)   ← never expose to browser
Mid-tier:       key_id alone (public endpoint auth)   ← visible, but validated & revocable
Keyless:        x_entity_id (entity-based auth)       ← visible, no key needed at all
Weakest:        raw merchant_id                        ← forgeable, unverifiable
```

## When to Use Entity-Based Auth

Use `x_entity_id` when:
- The page is public (no place to hide a key)
- A server-side entity (order, invoice) was already created and scoped to the merchant
- The operation is inherently tied to that entity (paying for an order)

Don't use it when:
- No entity exists yet (no anchor to resolve the merchant from)
- The operation creates a new resource not tied to an existing entity
