# Deploy Payment-Links to Devstack

## Overview

This guide provides step-by-step instructions for deploying the payment-links service to devstack. For general devstack concepts, see `/docs/agent-actions/deploy-to-devstack.md`.

---

## Prerequisites

- Access to the `kube-manifests` repository
- `helmfile` CLI installed
- `kubectl` configured with cluster access
- (Optional) `devspace` CLI installed for hot reloading

---

## Step 1: Get the Commit Hash

### Option A: Use Current Production Commit

Fetch the current production commit from:

```bash
curl https://paymentlinks-test.razorpay.com/commit.txt
```

If you are not sure what commit to use, you can use this. If you need to add changes on top of this, you can setup hotreload using devspace and then sync your local code.

### Option B: Use Custom Commit


---

## Step 2: Modify helmfile.yaml

### Navigate to kube-manifests

```bash
cd ~/rzp/kube-manifests/helmfile
```

### Edit helmfile.yaml

Open `helmfile.yaml` and make the following changes:

#### 2.1 Update Global Settings (environments.defaults.values block)

```yaml
environments:
  default:
    values:
      - devstack_label: "your-unique-label"   # e.g., "pl-decomp-test", "karthik-fix1"
        ttl: "24h"                             # How long the deployment lives (max: 72h)
```

| Parameter | Location | Description |
|-----------|----------|-------------|
| `devstack_label` | `environments.default.values` | Unique identifier for your deployment |
| `ttl` | `environments.default.values` | Duration for deployment (e.g., `1h`, `24h`, `72h`) |

#### 2.2 Uncomment and Configure Payment-Links Release (releases block)

Find the `payment-links` section in the `releases` block. Uncomment it and update the `image` attribute:

```yaml
releases:
  # ... other releases ...
  
  - name: payment-links
    namespace: payment-links
    chart: ./charts/payment-links
    values:
      - image: "9a5000553a5dd7a01f1336454d0735c6811dfc67"    # <-- Replace with your commit hash
      # ... other values ...
```

| Parameter | Location | Description |
|-----------|----------|-------------|
| `image` | `releases[name=payment-links].values` | Git commit hash to deploy |

> **⚠️ IMPORTANT:** The `image` value should be the **commit hash only**, not a full image tag. The chart constructs the full image path.

---

## Step 3: Deploy to Devstack

### Validate Configuration

```bash
cd ~/rzp/kube-manifests/helmfile
helmfile lint
```

### Deploy

```bash
helmfile sync
```

### Verify Deployment

```bash
# Check all pods for your devstack label
kubectl get pods -A -l name=<your-devstack-label>

# Example
kubectl get pods -A -l name=pl-decomp-test

# Check payment-links namespace specifically
kubectl get pods -n payment-links
```

---

## Step 4: Access the Service

### Preview URL

```
https://payment-links-<devstack-label>.dev.razorpay.in
```

Example: `https://payment-links-pl-decomp-test.dev.razorpay.in`

### Using Headers

For requests through the main dev gateway:

```bash
curl -H "rzpctx-dev-serve-user: <devstack-label>" https://payment-links.dev.razorpay.in/health
```

---

## Hot Reloading with Devspace (Optional)

If you want to sync local code changes to the running pod without redeploying, use devspace. For general devspace concepts, see `/docs/agent-actions/hot-reload-devspace.md`.

### Step A: Deploy with `devstack` Image Tag

**Before deploying**, update the helmfile to use the special `devstack` image tag:

```yaml
releases:
  - name: payment-links
    namespace: payment-links
    chart: ./charts/payment-links
    values:
      - image: "devstack"    # <-- Use "devstack" instead of commit hash
```

Then run `helmfile sync`.

> **Why `devstack` tag?** This is a special Docker image built with hot-reload support. It automatically rebuilds and restarts the application when files change.

### Step B: Configure devspace.yaml

Navigate to the payment-links repo and update `devspace.yaml`:

```bash
cd ~/rzp/payment-links
```

Edit the `vars` section in `devspace.yaml`:

```yaml
vars:
  - name: DEVSTACK_LABEL
    value: "your-devstack-label"    # Must match helmfile devstack_label
  - name: NAMESPACE
    value: "payment-links"
  - name: APP_NAME
    value: "payment-links"
```

| Variable | Description |
|----------|-------------|
| `DEVSTACK_LABEL` | Must match the `devstack_label` you used in helmfile |
| `NAMESPACE` | Kubernetes namespace (usually `payment-links`) |
| `APP_NAME` | Application name (usually `payment-links`) |

### Step C: Prepare Dependencies

```bash
cd ~/rzp/payment-links
export GOPRIVATE="github.com/razorpay/*"
go mod tidy
go mod vendor
```

### Step D: Start Devspace

```bash
devspace dev --no-warn
```

This will:
1. Terminate the existing pod
2. Spin up a new pod with file sync enabled
3. Sync your local files to the remote container
4. Stream logs to your terminal

### Step E: Make Changes and Test

Any local file changes will automatically sync to the pod. The application rebuilds automatically inside the container.

Test your changes:

```bash
curl https://payment-links-<devstack-label>.dev.razorpay.in/health
```

---

## Cleanup

### Stop Devspace (if running)

```bash
# Press Ctrl+C in the devspace terminal, or:
devspace purge
```

### Delete Devstack Deployment

```bash
cd ~/rzp/kube-manifests/helmfile
helmfile delete
```

> **Note:** Always run `devspace purge` before `helmfile delete` if you used devspace.

---

## Quick Reference

| Task | Command/Location |
|------|------------------|
| Get prod commit | `curl https://paymentlinks-test.razorpay.com/commit.txt` |
| Helmfile location | `~/rzp/kube-manifests/helmfile/helmfile.yaml` |
| Set devstack label | `environments.default.values.devstack_label` |
| Set TTL | `environments.default.values.ttl` |
| Set commit hash | `releases[name=payment-links].values.image` |
| Devspace config | `~/rzp/payment-links/devspace.yaml` |
| Deploy | `helmfile sync` |
| Hot reload | `devspace dev --no-warn` |
| Check pods | `kubectl get pods -A -l name=<label>` |
| Access URL | `https://payment-links-<label>.dev.razorpay.in` |

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n payment-links

# Check logs
kubectl logs <pod-name> -n payment-links -f
```

### Devspace Not Syncing

1. Ensure `DEVSTACK_LABEL` in `devspace.yaml` matches your helmfile label
2. Run `devspace purge` and try again
3. Check if the pod is running: `kubectl get pods -n payment-links`

### Wrong Commit Deployed

Verify the deployed commit:

```bash
kubectl get deployment -n payment-links -o yaml | grep image
```
