# Payment Pages Decomposition - Project Index

## One-liner

Migrating Payment Pages functionality from the API monolith to the NoCodeApp (NCA) microservice using dual-write and shadowing strategy.

---

## Quick Context

| Attribute | Value |
|-----------|-------|
| **Project** | Payment Pages Decomposition |
| **Stage** | Dual-write with shadowing |
| **Target Service** | NoCodeApp (NCA) |
| **Source Service** | API Monolith |

---

## Repos Involved

| Repo | Path | Description |
|------|------|-------------|
| api | `~/rzp/api` | PHP Monolith - source of Payment Pages code |
| no-code-apps | `~/rzp/no-code-apps` | Go microservice - target for migration |
| kube-manifests | `~/rzp/kube-manifests` | Helm charts for devstack deployment |
| docs | `~/rzp/docs` | This documentation |
| pythonscripts | `~/rzp/pythonscripts` | Analysis scripts and failure logs |

---

## Where to Find Things

| Need | Location |
|------|----------|
| Architecture & Migration Flow | [PAYMENT_PAGES_DECOMP.md](./PAYMENT_PAGES_DECOMP.md) |
| API List with Routes | [PAYMENT_PAGES_DECOMP.md#write-apis](./PAYMENT_PAGES_DECOMP.md#request-flow---writeread-apis) |
| **🔴 API Request Templates** | **[payment-pages-api.http](./payment-pages-api.http)** ← USE THIS FOR TESTING! |
| **Code Reference (NCA)** | [code/](./code/) |
| Task Tracking | [tasks/](./tasks/) |
| Failure Logs & Analysis | `/pythonscripts/decomp-scripts/failure_logs/` |
| Deployment Guide | [/docs/agent-actions/deploy-to-devstack.md](/docs/agent-actions/deploy-to-devstack.md) |
| Hot Reload Guide | [/docs/agent-actions/hot-reload-devspace.md](/docs/agent-actions/hot-reload-devspace.md) |

> **🔴 FOR ALL TESTING:** Use `payment-pages-api.http` as your request template!
> - All headers, auth, and variables are pre-configured
> - Just modify the request body to trigger specific diffs
> - DON'T build curl commands from scratch!

---

## Key Files in Codebase

> **⚠️ IMPORTANT:** NCA code is written to **exactly mimic monolith behavior**. Any mismatch is a bug.

> **📝 NOTE:** Some diffs may already be fixed in master or cherry-picked commits. If you encounter a diff that doesn't reproduce on devstack, flag it as `🔵 Already Fixed` and move to the next subtask. User will verify.

### NCA Service (no-code-apps repo)

| Area | File | Purpose |
|------|------|---------|
| Routes | `internal/router/payment_page_private_routes.go` | Route definitions |
| Controller | `internal/controllers/payment_page.go` | HTTP handlers |
| Core Logic | `internal/modules/payment_page/core.go` | Business logic |
| Validation | `internal/modules/payment_page/validation.go` | PP-specific validation |
| Base Validation | `internal/modules/nocode/validation.go` | Base validation (TrackerType check here!) |
| Dual Write | `internal/monolith_decomp/dual_write_handlers/base.go` | Proxy & diff logic |
| Diff Checker | `internal/monolith_decomp/diffs/diff_checker.go` | Response comparison |

> See [code/](./code/) for detailed code documentation

### API Monolith (api repo)
- `app/Http/Controllers/PaymentPageController.php` - Main controller
- `app/Models/PaymentPage.php` - Model
- `app/Http/Routes/payment_pages.php` - Routes

---

## Current Tasks

| Task | Status | Priority | File |
|------|--------|----------|------|
| Fix payment_page_create status code diffs | 🟡 In Progress | P0 | [tasks/pp-create-status-code-diffs.md](./tasks/pp-create-status-code-diffs.md) |

> See [tasks/_index.md](./tasks/_index.md) for full task list and status tracking

---

## Testing on Devstack

### Test Merchant ID

> **⚠️ CRITICAL:** Use the **devstack test merchant ID**, NOT production merchant IDs from failure logs!
>
> Failure logs contain production merchant IDs which don't exist on devstack. Always use:
> - **Test Merchant ID:** `LJ3P0FyFtOULha`
> - **Mode:** `live` (or `test` as needed)

### API Variables for Testing

When using `payment-pages-api.http`:

```
nca_personal_url = https://nca.dev.razorpay.in
merchant_id = LJ3P0FyFtOULha  # <-- Use this test merchant, NOT prod IDs from logs!
auth_token = UkFORE9NX05DQV9VU0VSOlJBTkRPTV9OQ0FfUEFTU1dPUkQ=
devstack_label = <your-devstack-label>
```

**After fix is applied:** Look for `DIFF_CHECKER_NO_DIFFS_FOUND` in NCA logs to confirm fix works.

> **Note:** Add fields from failure logs to the body to reproduce specific diffs (e.g., `"settings": { "goal_tracker": {} }`)

---

## Testing on Devstack - Auth Bypass

**⚠️ IMPORTANT:** When hitting NCA directly (not via Edge), Passport auth is not present. You MUST bypass it for testing.

In `internal/router/payment_page_private_routes.go`, update `GetMiddlewares()`:

```go
func (a *PaymentPageRoutes) GetMiddlewares() []gin.HandlerFunc {
    return []gin.HandlerFunc{
        middlewares.Serialize,
        middlewares.WithAppErrorHandler(),
        middlewares.WithRequestInterceptor(),
        middlewares.WithResponseInterceptor(),
        //middlewares.PassportPrivateAuth(),  // COMMENT OUT for direct testing
        middlewares.WithAuth(),               // USE THIS INSTEAD
        middlewares.WithMerchantIdInterceptor(),
        middlewares.WithModeInterceptor(),
        middlewares.WithDualWriteStateInterceptor(),
        middlewares.WithPrometheus(),
        tracingIntegration.GinTracingMiddleware,
    }
}
```

Apply this change via hot reload before testing. See [hot-reload-devspace.md](/docs/agent-actions/hot-reload-devspace.md).

> **⚠️ DO NOT COMMIT this change.** Keep it uncommitted throughout testing. Only commit your actual bug fixes.

**Tip:** Hot reload only works while `devspace dev` is running. No need to run `devspace purge` between tasks - just run `devspace dev` again if you closed the terminal.

---

## Getting Actual Request Bodies from Coralogix

**🔴 Don't guess request bodies - fetch the actual ones!**

### How to Fetch Request Body

1. Get `razorpay_request_id` from failure log CSV file
2. Use Coralogix MCP to search for the request:

| Route | Query Pattern |
|-------|--------------|
| `payment_page_create` | `"PAYMENT_PAGE_CREATE_REQUEST" AND "<request_id>"` |
| `payment_page_update` | `"PAYMENT_PAGE_UPDATE_REQUEST" AND "<request_id>"` |

**MCP Tool:** `mcp_razorpay-cora-mcp-server_search_logs`
- `applicationName`: `no-code-apps`
- **For recent logs:** Use `relative_hours` (e.g., `48`)
- **For older logs:** Use `start_time` + `end_time` in RFC3339 format (e.g., `2025-12-29T00:00:00Z`)

### Time Range Options

| Option | Usage | Example |
|--------|-------|---------|
| `relative_hours` | Recent logs (last N hours) | `relative_hours: 48` |
| `start_time` + `end_time` | Historical logs (any date within retention) | `start_time: 2025-12-29T00:00:00Z`, `end_time: 2025-12-30T00:00:00Z` |

> **Note:** Coralogix has 2-3 months retention. Choose log files within this retention period.

---

## Useful Commands

```bash
# Deploy to devstack
cd ~/rzp/kube-manifests/helmfile
helmfile lint && helmfile sync

# Check ALL pods for your devstack (single command!)
kubectl get pods -A -l name=pp-decomp-fix1
# Shows pods from all namespaces (api, no-code-apps, gimli) matching your label

# Check specific namespace
kubectl get pods -n no-code-apps -l name=pp-decomp-fix1

# View logs
kubectl logs <pod-name> -n <namespace> -f
```

### Testing APIs

> **⚠️ DON'T `kubectl exec` into pods to test!** Hit the URL directly with headers.

```bash
# Hit NCA directly with devstack routing
curl -X POST 'https://nca.dev.razorpay.in/v1/payment_pages' \
  -H 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
  -H 'X-Razorpay-Mode: live' \
  -H 'rzpctx-dev-serve-user: pp-decomp-fix1' \
  -H 'Authorization: Basic UkFORE9NX05DQV9VU0VSOlJBTkRPTV9OQ0FfUEFTU1dPUkQ=' \
  -H 'Content-Type: application/json' \
  -d '{"currency":"INR","title":"Test",...}'
```

---

## Decision Log

| Date | Decision |
|------|----------|
| 2024-12-30 | Using dual-write with shadowing migration strategy |
| 2024-12-30 | API list finalized - 7 write APIs, 14 read APIs |

---

## Related Links

- Postman Collection: `No Code Apps.postman_collection.json` (original, contains stores too)
- Tech Spec: `PAYMENT_PAGES_DECOMP.md`

