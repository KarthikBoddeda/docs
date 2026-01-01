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
| API Request Examples (.http) | [payment-pages-api.http](./payment-pages-api.http) |
| Task Tracking | [tasks/](./tasks/) |
| Failure Logs & Analysis | `/pythonscripts/decomp-scripts/failure_logs/` |
| Deployment Guide | [/docs/agent-actions/deploy-to-devstack/overview.md](/docs/agent-actions/deploy-to-devstack/overview.md) |

---

## Key Files in Codebase

### API Monolith (api repo)
- `app/Http/Controllers/PaymentPageController.php` - Main controller
- `app/Models/PaymentPage.php` - Model
- `app/Http/Routes/payment_pages.php` - Routes

### NCA Service (no-code-apps repo)
- `internal/paymentpage/` - Payment page handlers
- `internal/proxy/` - Proxy logic for monolith calls
- `internal/dualwrite/` - Dual write implementation

---

## Current Tasks

| Task | Status | Priority |
|------|--------|----------|
| TBD | - | - |

> Add tasks to `tasks/` folder as separate files for complex tasks

---

## API Variables for Testing

When using `payment-pages-api.http`:

```
nca_personal_url = https://nca.dev.razorpay.in  (or devstack URL)
merchant_id = <your-merchant-id>
auth_token = <base64-encoded-key:secret>
page_id = pl_xxxxx
payment_id = pay_xxxxx
devstack_label = <your-devstack-label>
```

For devstack, add header: `rzpctx-dev-serve-user: {{devstack_label}}`

---

## Useful Commands

```bash
# Deploy to devstack
cd ~/rzp/kube-manifests/helmfile
helmfile lint && helmfile sync

# Check pods
kubectl get pods -A -l name=<devstack-label>

# View logs
kubectl logs <pod-name> -n <namespace> -f

# Test API with devstack header
curl -H "rzpctx-dev-serve-user: <label>" https://api.dev.razorpay.in/v1/payment_pages
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

