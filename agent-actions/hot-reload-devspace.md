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

### Step 2: Prepare Dependencies (Go services)

Before running devspace, ensure dependencies are up to date:

```bash
cd ~/rzp/<service-repo>
go mod tidy
go mod vendor
```

> **Why?** Devspace syncs your local `vendor/` directory to the pod. If vendor is outdated, the pod build may fail or use stale dependencies.

### Step 3: Run Devspace Dev

```bash
devspace dev --no-warn
```

**What this does:**
1. Terminates the old pod
2. Spins up a new pod with the specified image
3. Syncs your local files into the remote container
4. Streams logs to your terminal

### Step 4: Verify and Test

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
| Added/changed dependency in `go.mod` | Run `go mod tidy && go mod vendor` before devspace |
| First time running devspace | Run `go mod tidy && go mod vendor` to ensure vendor is up to date |
| Syncing vendor files | No action - vendor files sync automatically after initial setup |

### Pod Sync Behavior

- By default, devspace syncs to the **web pod**, not worker pods

---

## Stopping and Cleanup

### Between Tasks (Same Devstack)

**You do NOT need to run `devspace purge` between tasks.** Just keep `devspace dev` running:

- **Hot reload only works while `devspace dev` is running**
- If you closed the terminal, just run `devspace dev --no-warn` again
- No need to purge - the pod continues running and you can reconnect

### Full Cleanup (Tearing Down Devstack)

Only run `devspace purge` when you're completely done and want to tear down the devstack:

```bash
# Stop devspace first
devspace purge

# Then delete the devstack
cd ~/rzp/kube-manifests/helmfile
helmfile delete
```

> **Important:** Run `devspace purge` before `helmfile delete` to ensure clean removal.
