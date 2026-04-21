# Tasks Index - Payment Handles Decomposition

## Active Tasks

| # | Task | Created | Status | Priority | File |
|---|------|---------|--------|----------|------|
| 001 | Routing, proxy setup & splitz experiment integration | 2026-02-20 | 🟢 Completed | P0 | [001-routing-and-experiment.md](./001-routing-and-experiment.md) |
| 002 | NCA payment_handle_create & update with ID reuse | 2026-02-20 | ⏸️ Superseded by 006 | P0 | [002-ph-create-update.md](./002-ph-create-update.md) |
| 003 | Monolith: Replace function calls with NCA HTTP calls | 2026-02-20 | 🟢 Done (PR update needed — see 006) | P0 | [003-monolith-fn-replace.md](./003-monolith-fn-replace.md) |
| 004 | NCA: Payment handle read APIs (get, availability, suggestion, encryption) | 2026-02-21 | ⏸️ Superseded by 007 | P0 | [004-ph-read-apis.md](./004-ph-read-apis.md) |
| 005 | Kong: Edge routing changes for all payment handle APIs | 2026-02-21 | 🟢 Completed | P0 | [005-kong-routing.md](./005-kong-routing.md) |
| 006 | NCA-direct writes + monolith merchant_settings sync | 2026-02-23 | ⬜ Not Started | P0 | [006-nca-direct-writes.md](./006-nca-direct-writes.md) |
| 007 | NCA-first reads with monolith fallback | 2026-02-23 | ⬜ Not Started | P0 | [007-nca-first-reads.md](./007-nca-first-reads.md) |

## Devstack Status

| Service | URL | Status |
|---------|-----|--------|
| NCA | `https://nca.dev.razorpay.in` with header `rzpctx-dev-serve-user: ph-decomp` | ✅ Running |
| API | `https://api-web-ph-decomp.dev.razorpay.in` | ✅ Running |
| Gimli | `https://gimli-ph-decomp.dev.razorpay.in` | ✅ Running |

## Strategy Update (2026-02-23)

**The approach has changed from dual-write to NCA-direct writes.** Tasks 002 and 004 are superseded.

See [PaymentHandleDecomp_v2.md](/projects/payment-handles-decomp/PaymentHandleDecomp_v2.md) for the full updated spec.

**New approach summary:**
- All new merchant writes go directly to NCA (`nca_only` from day 1)
- No dual write / no proxy back to monolith for writes
- Reads: NCA checks its DB first, falls back to monolith for old merchants
- Monolith syncs `merchant_settings` after NCA create (for rollback safety)

## Blocked Items

- Task 006/007: Needs new NCA branch cut from `pp-fixes-2`
- Data migration of merchant settings + handles — manual task, after Task 007 is stable
- Read shadowing (diff checker for reads) — after Task 007 is merged
- Dashboards + alerts — monitoring setup pending

## Completed Work

- Task 001 ✅: NCA routing, splitz experiment setup, proxy state wiring
- Task 002 ✅: Dual write create/update (now superseded by Task 006)
- Task 003 ✅: Monolith internal function calls replaced with NCA HTTP calls (PR #64786 needs merchant_settings sync addition from Task 006)
- Task 004 ✅: NCA read APIs proxy setup (now superseded by Task 007)
- Task 005 ✅: Kong routes + upstream-override for all 6 payment handle APIs

## PR Order & Dependencies

| PR | Repo | Task | Depends On | Notes |
|----|------|------|------------|-------|
| #64786 (update) | `api` | 006 (merchant_settings sync) | — | Can be merged independently |
| New PR (Tasks 006+007) | `no-code-apps` | 006+007 | #64786 merged | NCA writes + reads |
| #1006 (update) | `no-code-apps` | 006 | — | Remove dual write handler |
| #1007 (update) | `no-code-apps` | 006 | — | Rewrite CreatePaymentHandle |
| #1008 (update) | `no-code-apps` | 007 | 006 merged to NCA | NCA-first reads |

**Recommended merge order:**
1. `api#64786` — monolith changes (adds upsert, removes Splitz gate for writes). Safe to merge first.
2. `no-code-apps#1006` + `#1007` — NCA write refactor. Once NCA starts directly creating, monolith is ready.
3. `no-code-apps#1008` — NCA reads. Requires NCA DB to have handle data (from step 2 running in prod for some merchants).

## Task Statuses

- ⬜ Not Started
- 🟡 In Progress
- 🟢 Completed
- 🔴 Blocked
- ⏸️ Paused / Superseded

## Devstack Configuration

| Service | Commit | Label | Notes |
|---------|--------|-------|-------|
| NCA | `2bd13e63a699e1decea6b5e5e92a4d86aec2afb5` | `ph-decomp` | Old: PR 1 + PR 2 (dual write). Update to new branch for Tasks 006+007 |
| API | `06383358f91aaae93705e78489b6f32088cea67b` | `ph-decomp` | Old: Task 003. Update with merchant_settings sync for Task 006 |
| Gimli | `acf7ce8b84037b15d82236a34cc36fa57877ffae` | `ph-decomp` | Default |

## Related Resources

- [Payment Handle API Requests](/projects/payment-handles-decomp/payment-handles-api.http)
- [PH Decomp Spec v2 (current)](/projects/payment-handles-decomp/PaymentHandleDecomp_v2.md)
- [PH Decomp Spec v1 (legacy)](/projects/payment-handles-decomp/PaymentHandleDecomp.md)
- [NCA Code Navigation](/projects/payment-handles-decomp/code/_index.md)
- [Deployment Guide](/docs/agent-actions/deploy-to-devstack.md)
- [Hot Reload Guide](/docs/agent-actions/hot-reload-devspace.md)
