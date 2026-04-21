# NaCl Box Service Identity Tokens

## What Is It

A pattern where a backend service proves its identity to an API gateway by generating short-lived encrypted tokens using **NaCl box** (asymmetric encryption). The gateway decrypts the token and trusts the embedded claims.

## How NaCl Box Works Here

NaCl box is asymmetric encryption using two key pairs:

```
Service (NCA)                        Gateway (Kong)
─────────────                        ─────────────
private_key (secret, never shared)   private_key (secret)
public_key  (known to Kong)          public_key  (known to NCA)
```

To encrypt:
```
ciphertext = NaCl.box.seal(
    plaintext,
    recipient_public_key = Kong's public key,
    sender_private_key   = NCA's private key
)
```

Only Kong can decrypt (holds its own private key). And decryption also proves origin — it only succeeds if the sender used NCA's private key (which Kong knows the public counterpart of).

## Token Structure

```
plaintext = "merchant_id:mode:unix_timestamp:domain"
         e.g. "DBeZ7DIU7L8wae:live:1741850432:razorpay"

token = "kid:base64(ciphertext)"
      e.g. "nocodeapps_10000:8h8z55Vshvgq..."
```

The `kid` (key ID) tells the gateway which key pair to use for decryption.

## Security Properties

| Property | Mechanism |
|---|---|
| Only the service can generate tokens | Private key never leaves the service |
| Only the gateway can decrypt | Gateway's private key never exposed |
| Tokens expire | Timestamp in plaintext; gateway rejects stale tokens |
| Replay attack prevention | Short expiry window (typically ~5 min) |
| Merchant binding | Merchant ID embedded in plaintext |

## Honest Limitation: Tokens Are "Fetchable" From Public Pages

If the token is embedded in a public page (e.g. a hosted checkout page), anyone can:
1. Fetch the page → extract a valid token
2. Use it within the expiry window

The security model does **not** prevent this. What it prevents:
- **Forged service identity**: You can't generate a valid token without the private key
- **Replay of old tokens**: Expired tokens are rejected

For public-facing flows, this is an acceptable tradeoff — the protected APIs are typically read-only or low-risk.

## Comparison to JWT

| | JWT (HS256/RS256) | NaCl Box Token |
|---|---|---|
| Algorithm | HMAC or RSA signing | Asymmetric box encryption |
| Verification | Signature check | Decryption succeeds = verified |
| Confidentiality | Claims are visible (base64) | Claims are encrypted |
| Use case | Standard web auth | Service-to-gateway identity |

NaCl box tokens hide the plaintext (merchant ID, mode) from intermediaries — JWTs do not.

## When to Use This Pattern

- A backend service needs to call a gateway-protected API on behalf of many different merchants, without storing each merchant's API key.
- Short-lived proofs of "I am service X acting for merchant Y" are sufficient.
- You want the gateway to do auth, not the downstream application.
