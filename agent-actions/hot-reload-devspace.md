# Hot Reload with Devspace

## Overview

Devspace enables syncing local code changes to a pod running on devstack without redeploying. This allows rapid iteration when testing fixes.

**Use Case:** You've made code changes locally and want to test them on devstack without a full redeploy.

---

## Prerequisites

1. **Devstack is already deployed** with your services running (see [deploy-to-devstack.md](./deploy-to-devstack.md))
2. **Devspace binary is installed** (installed via Devstack Onboarding script)
3. **You know your devstack label** (the unique identifier used during deployment)

---

## Steps

### Step 1: Update devspace.yaml

The `devspace.yaml` file is in the root directory of the service repo. Update the `vars` section:

| Variable | Description |
|----------|-------------|
| `DEVSTACK_LABEL` | Your devstack label |
| `NAMESPACE` | Kubernetes namespace for the service |
| `APP_NAME` | Application name |

#### Special Case: Updating the Base Image

For some services (e.g., no-code-apps), update the `replaceImage` to use your commit's build instead of the generic tag:

**Before:**
```yaml
dev:
  replacePods:
    - labelSelector:
        name: ${APP_NAME}-${DEVSTACK_LABEL}
      replaceImage: c.rzp.io/razorpay/<service>:api_devstack
      namespace: ${NAMESPACE}
```

**After (with your commit):**
```yaml
dev:
  replacePods:
    - labelSelector:
        name: ${APP_NAME}-${DEVSTACK_LABEL}
      replaceImage: c.rzp.io/razorpay/<service>:api_devstack-<your-commit-id>
      namespace: ${NAMESPACE}
```

> **Why?** The generic `api_devstack` tag is only updated on merges to master. Using your commit's build ensures the base image is close to your local branch.

### Step 2: Run Devspace Dev

```bash
cd ~/rzp/<service-repo>
devspace dev --no-warn
```

**What this does:**
1. Terminates the old pod
2. Spins up a new pod with the specified image
3. Syncs your local files into the remote container
4. Streams logs to your terminal

### Step 3: Verify and Test

```bash
# Check pod status (in another terminal)
kubectl get pods -n <namespace> -l name=<devstack-label>

# Wait until STATUS is Running and READY is 1/1
```

Once ready, test your changes by hitting your endpoints.

---

## Checking Logs

**Option 1:** Logs stream automatically in the devspace terminal

**Option 2 (Recommended for Agents):** Use kubectl for more control
```bash
kubectl logs <pod-name> -n <namespace> -f
```

---

## Important Notes

### For Go Services

| Scenario | Action Required |
|----------|-----------------|
| Changed existing code | No action - auto syncs and rebuilds |
| Added new dependency in `go.mod` | Push commit to GitHub to rebuild vendor packages |
| Syncing vendor files | No action - vendor files sync automatically |

### Pod Sync Behavior

- By default, devspace syncs to the **web pod**, not worker pods

---

## Cleanup

```bash
# Stop devspace (Ctrl+C in the terminal)
devspace purge
```

> **Important:** Run `devspace purge` before `helmfile delete` to ensure clean removal.
