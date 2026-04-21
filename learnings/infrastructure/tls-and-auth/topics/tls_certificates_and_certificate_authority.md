# Topic: TLS Certificates and Certificate Authority

## What a certificate is

A certificate (`.crt` / `.pem` file) contains:
- **Public key** — derived from the private key via one-way math (RSA: `n = p×q`; ECDSA: elliptic curve point multiplication)
- **Identity** — `CN=name, O=org`
- **CA signature** — `encrypt(hash(above_contents), CA_private_key)`
- Metadata — expiry date, serial number, allowed usages

## How verification works

When you present your certificate, the verifier does:

```
expected_hash = decrypt(signature_in_cert, CA_public_key)
actual_hash   = hash(certificate_contents)

valid = (expected_hash == actual_hash)
```

This proves the certificate was issued by the CA and has not been tampered with. Any modification to identity or public key changes `actual_hash`, breaking the match.

## Why the CA signature is necessary

Without it, certificates are self-written text files. Anyone can claim any identity. The CA signature is the unforgeable stamp — only the CA's private key can produce a signature that verifies against the CA's public key.

The CA public key is pre-distributed to every verifier (API server, browsers, etc.) as the shared ground truth.

## Certificate vs private key

The certificate is **public** — it can be shared freely. It contains your public key and identity. By itself it's useless for impersonation.

The private key is **secret** — it never leaves the machine that generated it. It's used to sign challenges during authentication.

Certificate without private key = a name badge. Private key is what proves the badge is yours.

## Certificate revocation

Certificates have a TTL (typically 1 year or 90 days). Before expiry, they can be revoked via a CRL (Certificate Revocation List) or OCSP. After revocation, the CA public key can no longer be used to trust that certificate — the CA marks it invalid.

## In Kubernetes

Razorpay generates one CA keypair per cluster during setup. The CA public key is baked into:
- The kube-apiserver (trusts certs signed by this CA)
- Every kubelet (to verify API server's cert)
- Every kubeconfig (to verify the API server)

The CA private key signs certificates for: kubectl users, service accounts, kubelets, the API server itself.

## Related questions

- [How do TLS certificates and mTLS actually work?](../questions/how_do_tls_certificates_and_mtls_actually_work.md)
