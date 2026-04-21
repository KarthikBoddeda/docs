# Topic: Argo Auth Model and Port-Forward Access

## Two layers of auth around Argo's HTTP API

```
Browser path:
  You → SSO/OAuth proxy (Pomerium) → Ingress → argo-server pod
        ↑ requires Razorpay SSO login

Port-forward path:
  kubectl port-forward svc/argo-server -n argo 2746:2746
  curl http://localhost:2746/api/v1/...
        ↑ bypasses ingress and SSO entirely
```

## Argo server auth modes

Argo server supports three auth modes:

| Mode | Behavior |
|---|---|
| `server` | No token required. Uses the Argo server's own service account for all operations. Any request is accepted. |
| `client` | Caller must provide a Kubernetes service account token. Argo uses the caller's token for API operations. |
| `sso` | Integrates with an SSO provider. Argo server mints its own tokens after SSO login. |

Razorpay's `dev-serve` Argo runs in **`server` mode**. This means once you can reach the Argo server's port 2746, you get full access — no token needed.

## Why port-forward gives unauthenticated access

The SSO proxy (what you see in the browser) is an **ingress-level** component. It intercepts HTTP requests to the Argo domain before they reach the Argo pod. But `kubectl port-forward` doesn't go through the ingress — it connects directly to the pod's port via kubelet.

The port-forward itself requires:
- Valid kubeconfig credentials (JWT or client cert) to authenticate to the Kubernetes API server
- RBAC permission: the `pods/portforward` verb in the `argo` namespace

These are the real security gates. Once inside, Argo server in `server` mode asks for nothing more.

## How this was used to debug e2e failures

With an existing port-forward on port 2746 (left running from a previous session):

```bash
# List archived workflows — no auth header needed
curl http://localhost:2746/api/v1/archived-workflows?listOptions.limit=10

# Get full workflow details
curl http://localhost:2746/api/v1/archived-workflows/{uid}

# Stream pod logs for a specific step
curl http://localhost:2746/api/v1/workflows/argo-workflows/{name}/log \
  ?podName={step-pod}&container=main&follow=false
```

This gave access to full `go test` output from the `wait-for-test-completion` pod, which revealed all 5 failing test stack traces — all pointing to `create_test.go:373`, the gimli short URL assertion.

## Key takeaway

The "auth" you see as a user (SSO login in browser) is not Argo's auth — it's a proxy in front of it. Argo itself in server mode has no auth. The actual access control is at the network layer: VPN + kubeconfig + RBAC on `pods/portforward`.

## Related questions

- [What is Argo and how does it run on Kubernetes?](../questions/what_is_argo_and_how_does_it_run_on_kubernetes.md)

## Related topics

- [kubectl_port_forward](../../networking/topics/kubectl_port_forward.md)
- [tls_certificates_and_certificate_authority](../../../infrastructure/tls-and-auth/topics/tls_certificates_and_certificate_authority.md)
