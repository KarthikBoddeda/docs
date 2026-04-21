# Topic: mTLS — Mutual TLS Authentication

## What mTLS is

Normal TLS: **server** proves identity to the client (your browser verifies Google's cert).

mTLS: **both sides** prove identity. Server presents a cert, client presents a cert. Both verify each other.

## The handshake step by step

1. Client connects to server
2. Server sends its certificate → client verifies via CA public key
3. Server says "send me your certificate too"
4. Client sends its certificate → server verifies via CA public key
5. Server sends a random challenge (random bytes)
6. Client signs challenge: `signature = encrypt(hash(challenge), client_private_key)`
7. Server verifies: `decrypt(signature, client_public_key) == hash(challenge)`
8. If valid: server reads identity from cert (`CN=boddedakarthik.s`), grants access per RBAC

Step 6-7 is what prevents certificate theft. Without the private key, the client can't produce a valid signature for the random challenge.

## Why mTLS is elegant

- Server never stores credentials — only needs the CA public key
- Private key never leaves the client machine — only signatures travel over the wire
- Revocation is clean — no passwords to rotate, just revoke the certificate
- The same mechanism works for all cluster-internal communication (API server ↔ etcd, API server ↔ kubelet, etc.)

## Why it's not universal for S2S APIs

| Problem | Detail |
|---|---|
| Certificate lifecycle | Issuance, rotation, expiry, revocation requires tooling (cert-manager, Vault) |
| TLS termination | Load balancers terminate TLS — client cert identity is lost before reaching the service |
| Dev experience | Local setup requires a local CA, per-service certs, proper SANs |
| Migration cost | Touching every service simultaneously, can't be done incrementally easily |
| Framework support | Inconsistent across languages — Go is fine, Python/Ruby are clunky |

## The service mesh solution

Istio / Linkerd inject a sidecar proxy next to every pod. The mesh handles:
- Certificate issuance (via its own CA, e.g. Istio's Citadel)
- Automatic rotation before expiry
- mTLS enforcement between all services by default

Application code changes nothing. mTLS becomes invisible plumbing.

## Related questions

- [How do TLS certificates and mTLS actually work?](../questions/how_do_tls_certificates_and_mtls_actually_work.md)
