# Deploy to Devstack

## Overview

Devstack enables developers to deploy their custom commits on a Kubernetes cluster. It is an easy replacement for local development for developers who want to:
- Deploy applications on a Kubernetes cluster
- Access services via HTTP/GRPC endpoints
- Communicate with upstream or downstream dependency microservices

This document outlines the steps to deploy applications on devstack using Helm.

---

## Prerequisites

- Access to the `kube-manifests` repository
- `helmfile` CLI installed
- `kubectl` configured with cluster access

---

## Steps to Deploy

### 1. Navigate to kube-manifests

```bash
cd ~/rzp/kube-manifests
```

### 2. Modify helmfile.yaml

Open `helmfile/helmfile.yaml` in the checked-out `kube-manifests` repository (master branch or the required branch).

In the `environments.defaults.values` block, update the following:

| Parameter | Description |
|-----------|-------------|
| `devstack_label` | Unique identifier for your deployment (e.g., your name, project name, JIRA ID, PR number) |
| `ttl` | Time duration for which services will be up. Max: 72h. Format: `60m`, `1h`, `24h`, `2d` |

> **⚠️ IMPORTANT:** If you don't know the exact services to deploy - **ABORT**. Deploying a subset of services is a waste of time.

In the `releases` block:
1. Uncomment the services you want to deploy
2. Update the commit hash for each service

> **⚠️ IMPORTANT:** If you don't know what commit to use - **ABORT** and ask the user. Everything is wasted with a wrong commit.

### 3. Folder Structure Reference

If you need to debug helmfile configurations:

| Path | Description |
|------|-------------|
| `kube-manifests/helmfile/charts/<service-folder>` | Devstack charts (service folder specified in helmfile.yaml) |
| `kube-manifests/templates/<service-folder>` | Chart templates for prod/stage environments. **Different from devstack** - don't confuse them. |

### 4. Deploy the Applications

Validate the helmfile:

```bash
cd ~/rzp/kube-manifests/helmfile
helmfile lint
```

Deploy to devstack:

```bash
helmfile sync
```

On successful completion, the ephemeral service cluster will be running with desired replicas and can be accessed via the unique header in requests.

---

## Verify Deployment

### Check Pods

```bash
# Get pods in a specific namespace (namespace found in helmfile under your service)
kubectl get pods -n <namespace>

# Example
kubectl get pods -n api

# List pods for all services across namespaces
kubectl get pods -A -l name=<your-devstack-label>

# Example
kubectl get pods -A -l name=label123
```

### View Logs

```bash
kubectl logs <pod-name> -n <namespace> -f

# Example
kubectl logs api-web-546554-4-sad34 -n api -f
```

---

## Accessing the Provisioned Fleet

### Preview URL

Every fleet created by devstack has a unique URL:

```
https://<service>-<devstack-label>.dev.razorpay.in
```

Example: `https://dashboard-awesomedevstack.dev.razorpay.in`

The preview URL is printed when `helmfile sync` completes successfully.

To find the preview URL later:

```bash
kubectl get ingressroute <app>-<devstack-label> -n <namespace> -o yaml

# Example
kubectl get ingressroute api-web-awesomedevstack -n api -o yaml
```

### Using Headers

Access services using the application URL + header:

| Component | Value |
|-----------|-------|
| Service URL | `<service-name>.dev.razorpay.in` |
| Header Key | `rzpctx-dev-serve-user` |
| Header Value | `<devstack_label>` |

**cURL Example:**

```bash
curl -H "rzpctx-dev-serve-user: <devstack_label>" https://<service>.dev.razorpay.in/endpoint
```

---

## Termination

Clean up resources:

```bash
helmfile delete
```

> **Note:** A janitor is installed on the cluster that auto-cleans provisioned fleets after the TTL expires.

If using devspace for local code sync, run `devspace purge` before `helmfile delete` to ensure proper cleanup.
