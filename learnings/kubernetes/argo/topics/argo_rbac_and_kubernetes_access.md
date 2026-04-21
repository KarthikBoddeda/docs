# Topic: Argo RBAC and Kubernetes Access

## How Argo gets permission to create pods

Argo's controller runs as a Kubernetes **service account** (e.g. `argo-workflow-controller`) in the `argo` namespace. Kubernetes automatically mounts a JWT token for this service account inside the controller pod at:

```
/var/run/secrets/kubernetes.io/serviceaccount/token
```

The controller uses this token to authenticate every call it makes to the Kubernetes API server.

## What permissions Argo has (RBAC)

Razorpay defines a `ClusterRole` (or namespace-scoped `Role`) granting Argo's service account permissions like:

```yaml
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log", "configmaps", "secrets"]
    verbs: ["create", "get", "list", "watch", "delete", "patch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["argoproj.io"]
    resources: ["workflows", "workflowtemplates"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

With these permissions, when Argo executes a step it literally calls:

```
POST /api/v1/namespaces/argo-workflows/pods
Authorization: Bearer <service-account-token>
Body: { pod spec for this workflow step }
```

The API server verifies the JWT, checks the RBAC rules for that service account, and if permitted, creates the pod.

## What Argo can do in the e2e pipeline

For the `payment-links-e2e` pipeline, Argo needs to:

1. **Create pods** in `argo-workflows` namespace — for each workflow step
2. **Create/update Deployments, Services** in the devstack namespace — the `deploy-to-devstack` step runs `helmfile apply` which creates all the payment-links resources
3. **Read pod logs** — to stream test output and post results

All of these are standard Kubernetes API calls, authenticated using the service account JWT.

## Why this matters for security

Argo's service account scope determines blast radius. If scoped narrowly (only `argo-workflows` namespace), a rogue workflow can only affect that namespace. If given cluster-wide permissions (as is common in dev clusters for convenience), it can create resources anywhere.

In `dev-serve`, Argo likely has broad permissions so e2e workflows can freely create devstack namespaces. In production clusters, this would be locked down.

## Related questions

- [What is Argo and how does it run on Kubernetes?](../questions/what_is_argo_and_how_does_it_run_on_kubernetes.md)
