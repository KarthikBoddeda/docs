# Tasks Index - Payment Handles Decomposition

## Active Tasks

| # | Task | Created | Status | Priority | File |
|---|------|---------|--------|----------|------|
| 001 | Routing, proxy setup & splitz experiment integration | 2026-02-20 | 🟡 In Progress | P0 | [001-routing-and-experiment.md](./001-routing-and-experiment.md) |
| 002 | NCA payment_handle_create & update with ID reuse | 2026-02-20 | 🟡 In Progress | P0 | [002-ph-create-update.md](./002-ph-create-update.md) |
| 003 | Monolith: Replace function calls with NCA HTTP calls | 2026-02-20 | 🟡 In Progress | P0 | [003-monolith-fn-replace.md](./003-monolith-fn-replace.md) |

## Devstack Status

| Service | URL | Status |
|---------|-----|--------|
| NCA | `https://nca.dev.razorpay.in` with header `rzpctx-dev-serve-user: ph-decomp` | ✅ Running |
| API | `https://api-web-ph-decomp.dev.razorpay.in` | ✅ Running |
| Gimli | `https://gimli-ph-decomp.dev.razorpay.in` | ✅ Running |

## Blocked Items

All tasks are partially tested. The following require a merchant with payment handle enabled:
- Full dual-write DB write test (Task 002, subtasks 1-3)
- Monolith activation flow test (Task 003, subtasks 1-3)
- Routing between handle/page experiments for create_order (Task 001, subtask 5)

## Task Statuses

- ⬜ Not Started
- 🟡 In Progress
- 🟢 Completed
- 🔴 Blocked
- ⏸️ Paused

## Devstack Configuration

| Service | Commit | Label | Notes |
|---------|--------|-------|-------|
| NCA | `2bd13e63a699e1decea6b5e5e92a4d86aec2afb5` | `ph-decomp` | PR 1 + PR 2 changes |
| API | `06383358f91aaae93705e78489b6f32088cea67b` | `ph-decomp` | Monolith PR changes |
| Gimli | `acf7ce8b84037b15d82236a34cc36fa57877ffae` | `ph-decomp` | Default |

## Related Resources

- [Payment Handle API Requests](/projects/payment-handles-decomp/payment-handles-api.http)
- [PH Decomp Spec](/projects/payment-handles-decomp/PaymentHandleDecomp.md)
- [NCA Code Navigation](/projects/payment-handles-decomp/code/_index.md)
- [Deployment Guide](/docs/agent-actions/deploy-to-devstack.md)
- [Hot Reload Guide](/docs/agent-actions/hot-reload-devspace.md)
