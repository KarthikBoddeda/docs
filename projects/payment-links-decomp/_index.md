# Payment Links Decomposition - Project Index

## One-liner

Working with the Payment Links microservice for testing, debugging, and development tasks.

---

## Quick Context

| Attribute | Value |
|-----------|-------|
| **Project** | Payment Links Decomposition |
| **Service** | Payment Links (Go microservice) |
| **Stage** | Active Development |

---

## Repos Involved

| Repo | Path | Description |
|------|------|-------------|
| payment-links | `~/rzp/payment-links` | Go microservice for payment links |
| kube-manifests | `~/rzp/kube-manifests` | Helm charts for devstack deployment |
| docs | `~/rzp/docs` | This documentation |

---

## Where to Find Things

| Need | Location |
|------|----------|
| **🔴 API Request Templates** | **[payment-links-api.http](./payment-links-api.http)** ← USE THIS FOR TESTING! |
| Postman Collection | [Payment-Links.postman_collection.json](./Payment-Links.postman_collection.json) |
| V1 vs V2 Flow Analysis | [v1_v2_merchants.md](./v1_v2_merchants.md) |
| Task Tracking | [tasks/](./tasks/) |
| Deployment Guide | [deploy-to-devstack.md](./deploy-to-devstack.md) |
| General Deployment Guide | [/docs/agent-actions/deploy-to-devstack.md](/docs/agent-actions/deploy-to-devstack.md) |
| Hot Reload Guide | [/docs/agent-actions/hot-reload-devspace.md](/docs/agent-actions/hot-reload-devspace.md) |

> **🔴 FOR ALL TESTING:** Use `payment-links-api.http` as your request template!
> - All headers, auth, and variables are pre-configured
> - Just modify the request body as needed
> - DON'T build curl commands from scratch!

---

## Key Files in Codebase

### Payment Links Service (payment-links repo)

| Area | File | Purpose |
|------|------|---------|
| Routes | `internal/routing/router/route_list.go` | Route definitions |
| Controller | `internal/controllers/payment_link.go` | HTTP handlers |
| Core Logic | `internal/services/service.go` | Business logic |
| Validation | `internal/payment_link/validator.go` | Request validation |
| Model | `internal/payment_link/model.go` | Payment link model |
| Request Mapping | `internal/payment_link/request.go` | Request to model conversion |
| V1 Mapper | `internal/mapper/payment_link_v1_request.go` | V1 ↔ V2 request transformation |
| V1 Response | `internal/mapper/payment_link_v1_response.go` | V1 ↔ V2 response transformation |

---

## Current Tasks

| Task | Status | Priority | File |
|------|--------|----------|------|
| Dashboard API Validation | 🟡 In Progress | P0 | [tasks/dashboard-api-validation.md](./tasks/dashboard-api-validation.md) |

> See [tasks/_index.md](./tasks/_index.md) for full task list and status tracking

---

## Testing on Devstack

### Test Merchant ID

> **⚠️ CRITICAL:** Use the **devstack test merchant ID**, NOT production merchant IDs!
>
> - **Test Merchant ID:** `LJ3P0FyFtOULha`
> - **Mode:** `live` (or `test` as needed)

### API Variables for Testing

When using `payment-links-api.http`:

```
base_url = https://payment-links.dev.razorpay.in
merchant_id = LJ3P0FyFtOULha
auth_token = ZGV2OmRldi1wYXNzd29yZA==  # dev:dev-password
devstack_label = <your-devstack-label>
```

### Access Methods

**Option 1: Direct URL with devstack label**
```
https://payment-links-<devstack-label>.dev.razorpay.in/v1/payment_links
```

**Option 2: Base URL with header**
```bash
curl -H "rzpctx-dev-serve-user: <devstack-label>" https://payment-links.dev.razorpay.in/v1/payment_links
```

---

## Dashboard API Routes

The following APIs are exposed via the Razorpay Dashboard:

| API | Method | Endpoint | Description |
|-----|--------|----------|-------------|
| Create Link | POST | `/v1/payment_links` | Create a new payment link |
| List Links | GET | `/v1/payment_links` | List all payment links |
| Get Link | GET | `/v1/payment_links/:id` | Get a specific payment link |
| Update Link | PATCH | `/v1/payment_links/:id` | Update a payment link |
| Cancel Link | POST | `/v1/payment_links/:id/cancel` | Cancel a payment link |

---

## Useful Commands

```bash
# Deploy to devstack
cd ~/rzp/kube-manifests/helmfile
helmfile lint && helmfile sync

# Check ALL pods for your devstack
kubectl get pods -A -l name=<your-label>

# Check payment-links namespace
kubectl get pods -n payment-links

# View logs
kubectl logs <pod-name> -n payment-links -f

# Get current prod commit
curl https://paymentlinks-test.razorpay.com/commit.txt
```

---

## Related Links

- Postman Collection: `Payment-Links.postman_collection.json`
- V1 vs V2 Flow: `v1_v2_merchants.md`
