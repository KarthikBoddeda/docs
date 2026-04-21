# Topic: Bearer Tokens and JWTs

## Bearer token

A bearer token is a string sent in the HTTP `Authorization` header:
```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk3...
```

"Bearer" means: whoever bears (presents) this token gets access. No additional proof required — unlike mTLS which requires proving private key possession.

## What a JWT is

A JWT (JSON Web Token) is a bearer token with structure. It has three base64-encoded parts separated by dots:

```
header.payload.signature
```

**Header:** algorithm used (e.g. `RS256`)

**Payload (claims):**
```json
{
  "sub": "system:serviceaccount:argo:argo-server",
  "iss": "kubernetes/serviceaccount",
  "exp": 1741962000
}
```

**Signature:** `encrypt(hash(header + "." + payload), issuer_private_key)`

## How the API server verifies a JWT

```
expected_hash = decrypt(signature, issuer_public_key)
actual_hash   = hash(header + "." + payload)

valid = (expected_hash == actual_hash) AND (exp > now)
```

No database lookup. The API server only needs the issuer's public key. The identity claims are trusted if the signature verifies.

## JWT vs client certificate

| | JWT (bearer) | Client certificate (mTLS) |
|---|---|---|
| Travels over network | Yes, the token itself | No, only a signature over a challenge |
| Proof of possession | None — bearer token | Yes — private key challenge-response |
| If stolen | Attacker can use until expiry | Useless without private key |
| Storage | API server needs issuer public key | API server needs CA public key |
| Revocation | Hard (stateless — must use short TTL or revocation list) | Certificate revocation (CRL/OCSP) |

## In Kubernetes

Service accounts get JWTs automatically — mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token` inside every pod. Pods use this to authenticate to the API server.

User authentication (for kubectl) typically uses client certificates, not JWTs, because certs are more secure for interactive use.

## Related questions

- [How do TLS certificates and mTLS actually work?](../questions/how_do_tls_certificates_and_mtls_actually_work.md)
