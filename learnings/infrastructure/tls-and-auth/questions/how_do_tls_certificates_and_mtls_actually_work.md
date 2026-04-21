---
tags: [tls, mtls, certificates, authentication, kubernetes, security, s2s]
status: Answered
topics:
  - [tls_certificates_and_certificate_authority](../topics/tls_certificates_and_certificate_authority.md)
  - [mtls_mutual_authentication](../topics/mtls_mutual_authentication.md)
  - [bearer_tokens_and_jwts](../topics/bearer_tokens_and_jwts.md)
---

# How do TLS certificates and mTLS actually work?

## ❓ The Core Question

When kubectl connects to the Kubernetes API server, it uses a client certificate. How does the API server actually verify it? What's a CA, what's a signature, and why can't someone just fake a certificate?

## 🧠 The Learning Log

### Initial Understanding

Knew TLS exists and that certificates are involved, but not what they actually contain or how the math works.

### What a certificate actually is

A certificate is a file containing three things:
- Your **public key** (derived from your private key via one-way math — RSA uses p×q, ECDSA uses elliptic curve scalar multiplication)
- Your **identity** (e.g. `CN=boddedakarthik.s, O=razorpay-devs`)
- A **CA signature** (the CA hashed all the above and encrypted that hash with its private key)

### How the API server verifies a certificate

```
expected_hash = decrypt(CA_signature_in_cert, CA_public_key)
actual_hash   = hash(certificate_contents)

if expected_hash == actual_hash → certificate is genuine
```

This proves: the CA signed this exact certificate with this exact identity and public key. Any tampering changes `actual_hash`, breaking the match.

### 🔄 Refinement: A certificate alone proves nothing — you also need the private key

**My Misconception:** If someone has your certificate, they can impersonate you.

**The Correction:** The certificate contains only your public key. To complete the TLS handshake, you must sign a random server-issued challenge with your private key. Without the private key, you can't produce a valid signature.

**Key Insight:** Certificate = claim. Challenge-response = proof. The private key never travels over the network — only the signature does.

### 🔄 Refinement: Why the CA signature is needed

**My Misconception:** The CA signature is some kind of format requirement.

**The Correction:** Without a CA signature, a certificate is just a self-written text file. Anyone could claim any identity. The CA signature makes the certificate unforgeable: only the CA's private key can produce a signature that verifies against the CA's public key, which every cluster component already trusts.

**Key Insight:** The CA is the shared ground truth both sides agree on before connecting. The API server doesn't need a database of allowed users — it just needs the CA public key, and trusts any certificate that CA signed.

### Two auth mechanisms in Kubernetes

**Bearer token (JWT):** A signed JSON payload. The API server verifies the signature with its public key — no storage needed. Contains identity claims like `sub: system:serviceaccount:argo:argo-server`.

**Client certificate (mTLS):** Two-way TLS. Server and client each present a certificate. Client also proves private key possession via challenge-response. Stronger — private key never leaves the machine.

### Why most companies still use basic auth / API keys for S2S

mTLS is technically superior but operationally painful:
- Certificate lifecycle management (issuance, rotation, expiry, revocation) requires dedicated tooling
- TLS termination at load balancers kills client identity before it reaches the service
- Developer experience during local development is poor
- Migrating existing services requires touching every service simultaneously

Service meshes (Istio, Linkerd) solve this by injecting sidecar proxies that handle mTLS transparently. Without a mesh, the migration cost is prohibitive and basic auth persists.
