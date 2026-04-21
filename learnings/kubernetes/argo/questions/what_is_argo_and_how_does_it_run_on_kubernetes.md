---
tags: [argo, kubernetes, workflows, ci-cd, rbac, auth, port-forward, e2e]
status: Answered
topics:
  - [argo_workflows_architecture](../topics/argo_workflows_architecture.md)
  - [argo_rbac_and_kubernetes_access](../topics/argo_rbac_and_kubernetes_access.md)
  - [argo_auth_model_and_port_forward_access](../topics/argo_auth_model_and_port_forward_access.md)
---

# What is Argo Workflows and how does it run on Kubernetes?

## ❓ The Core Question

When debugging payment-links e2e failures, Argo Workflows came up as the CI system running the tests. What exactly is Argo? Why is it always running? How does it have permission to create pods and deployments? And why could we access its API without a password via port-forward?

## 🧠 The Learning Log

### Initial Understanding

Assumed Argo was a central hosted CI service (like GitHub Actions) external to our cluster.

### 🔄 Refinement: Argo is software Razorpay runs on their own Kubernetes cluster

**My Misconception:** Argo is a SaaS or external CI platform.

**The Correction:** Argo Workflows is a Go program that Razorpay deployed as pods in the `argo` namespace on the `dev-serve` Kubernetes cluster. It runs on Razorpay's own EC2 instances. There is no "central Argo" — every cluster that runs it has its own instance.

**Key Insight:** Same as how kube-apiserver is a Go binary on an EC2 instance, Argo is just another set of pods. The difference is it's a higher-level abstraction built on top of Kubernetes primitives.

### How a workflow becomes running pods

When a PR is opened on `payment-links`, the CI pipeline submits an Argo workflow definition (a YAML file describing steps). Argo's **workflow controller** watches for new Workflow CRDs and for each step:

1. Reads the step's container spec from the workflow YAML
2. Calls `POST /api/v1/namespaces/argo-workflows/pods` on the Kubernetes API server
3. A pod starts running that step (build image, deploy to devstack, run tests)
4. Argo watches the pod's status and moves to the next step when it completes

For the payment-links e2e pipeline, the steps are:
1. Build e2e Docker image
2. Deploy payment-links to a devstack via helmfile
3. Run `go test ./tests/e2e/...` inside the test container
4. Post results to GitHub PR as `rundeck/e2e-test` status check

### 🔄 Refinement: Argo is always running because it's a platform service, not a one-shot job

**My Misconception:** Argo starts up when a workflow is triggered and shuts down after.

**The Correction:** Argo is deployed as a Deployment (and thus kept alive permanently by Kubernetes) with multiple pods: the workflow controller, the Argo server (HTTP API + UI), a database (Postgres for workflow history), and MinIO (for artifact storage). These run 24/7 waiting for workflow submissions.

**Key Insight:** Argo is infrastructure, like a database or message queue. It's not triggered by CI — it receives trigger submissions and runs them.

### Why Argo could access the Kubernetes API without extra credentials

Argo's controller pod runs with a **Kubernetes service account** that has RBAC permissions to create/delete/watch pods and other resources in specific namespaces. When Argo creates a pod for a workflow step, it's just making an authenticated HTTP call to the Kubernetes API server using the service account's JWT token (auto-mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`).

### How we accessed the Argo HTTP API without a password

The Argo HTTP API (port 2746) sits behind two auth layers in production:
- **Browser path:** Argo web UI at `argo.dev-serve.razorpay.in` is behind an SSO/OAuth proxy (Pomerium) that enforces Razorpay SSO login
- **Port-forward path:** `kubectl port-forward svc/argo-server -n argo 2746:2746` bypasses the ingress/SSO entirely, connecting directly to the Argo server pod

Once the port-forward is open, the Argo server itself runs in **server auth mode** — it uses its own Kubernetes service account for all operations and doesn't challenge incoming HTTP requests for credentials. Any request to `localhost:2746` goes straight through.

**Key Insight:** The "auth" you see in the browser is the SSO proxy sitting in front, not Argo itself. Port-forward bypasses the proxy by going directly to the pod. The actual security boundary is: you need valid kubeconfig credentials (and VPN) to even run `kubectl port-forward`.
