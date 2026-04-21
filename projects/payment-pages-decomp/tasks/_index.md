# Tasks Index - Payment Pages Decomposition

## Active Tasks

| # | Task | Created | Status | Priority | File |
|---|------|---------|--------|----------|------|
| 001 | Fix payment_page_create status code diffs | 2026-01-01 | 🟡 In Progress | P0 | [001-pp-create-status-code-diffs.md](./001-pp-create-status-code-diffs.md) |
| 002 | Fix payment_page_update status code diffs | 2026-01-04 | ⬜ Not Started | P1 | [002-pp-update-status-code-diffs.md](./002-pp-update-status-code-diffs.md) |
| 003 | Fix payment_page_activate status code diffs | 2026-01-05 | ⬜ Not Started | P1 | [003-pp-activate-status-code-diffs.md](./003-pp-activate-status-code-diffs.md) |
| 004 | Fix payment_page_item_update status code diffs | 2026-01-05 | ⬜ Not Started | P2 | [004-pp-item-update-status-code-diffs.md](./004-pp-item-update-status-code-diffs.md) |
| 005 | Fix payment_page_set_receipt_details status code diffs | 2026-01-05 | ⬜ Not Started | P1 | [005-pp-set-receipt-details-status-code-diffs.md](./005-pp-set-receipt-details-status-code-diffs.md) |
| 006 | Fix payment_page_create_order status code diffs | 2026-01-05 | ⬜ Not Started | P0 | [006-pp-create-order-status-code-diffs.md](./006-pp-create-order-status-code-diffs.md) |
| 007 | PR Review Action Items | 2026-01-09 | ⬜ Not Started | P0 | [007-pr-review-action-items.md](./007-pr-review-action-items.md) |
| 008 | Unit Test Coverage Gaps | 2026-01-14 | 🟡 In Progress | P1 | [008-unit-test-coverage-gaps.md](./008-unit-test-coverage-gaps.md) |
| 009 | Fix NCA Unexpected Errors | 2026-01-17 | 🟢 Complete | P1 | [009-nca-unexpected-errors.md](./009-nca-unexpected-errors.md) |
| 010 | Phase 2 - Write APIs Status Code Diffs | 2026-01-20 | 🟢 Deployed | P0 | [010-phase-2-write-apis-status-code-diffs.md](./010-phase-2-write-apis-status-code-diffs.md) |
| 011 | Validation Gaps Analysis | 2026-01-21 | ⬜ Not Started | P1 | [011-validation-gaps-analysis.md](./011-validation-gaps-analysis.md) |
| 012 | Data Migration - Top 50 Merchants | 2026-01-22 | ⬜ Not Started | P0 | [012-data-migration-top-50-merchants.md](./012-data-migration-top-50-merchants.md) |
| 013 | Fix Response Body Diffs (All Routes) | 2026-01-23 | 🟡 In Progress | P1 | [013-response-body-diffs.md](./013-response-body-diffs.md) |
| 014 | Phase 3 After Datafix 1 | 2026-01-23 | ⬜ Not Started | P0 | [014-phase-3-after-datafix-1.md](./014-phase-3-after-datafix-1.md) |
| 015 | Live Analytics Non-Cached Spec | 2026-01-27 | 📝 Draft | P1 | [015-live-analytics-non-cached-spec.md](./015-live-analytics-non-cached-spec.md) |
| 016 | Phase 3 - Response Body Key Diff Fixes | 2026-02-14 | 🟡 In Progress | P0 | [016-phase-3-key-diff-fixes.md](./016-phase-3-key-diff-fixes.md) |
| 018 | All Merchants - Status Code Mismatches | 2026-04-16 | 🟡 In Progress | P0 | [018-all-merchants-status-code-mismatches.md](./018-all-merchants-status-code-mismatches.md) |
| 019 | All Merchants - Response Body Diff Keys | 2026-04-16 | ⬜ Not Started | P0 | [019-all-merchants-diff-keys.md](./019-all-merchants-diff-keys.md) |
| 020 | Security: Agents Can Create Payment Pages via Admin Dashboard (Login-as-Merchant) | 2026-04-21 | 🔴 Open | P0 | [020-admin-dashboard-payment-page-create-authz-gap.md](./020-admin-dashboard-payment-page-create-authz-gap.md) |

## Task Statuses

- ⬜ Not Started
- 🟡 In Progress
- 🟢 Completed
- 🔴 Blocked
- ⏸️ Paused

## How to Work on Tasks

1. Read the task file thoroughly
2. Check prerequisites (devstack deployment, commits)
3. Work through subtasks in priority order
4. Update status and work log after each subtask
5. If blocked, mark as blocked and notify user

## Related Resources

- [Failure Logs Analysis (Status Code Diffs)](/pythonscripts/decomp-scripts/failure_logs/)
- [Diff Logs Analysis (Response Body Diffs)](/pythonscripts/decomp-scripts/diff_logs/phase_1/)
- [Unexpected Errors Logs](/pythonscripts/decomp-scripts/failure_logs/unexpected_errors/)
- [Deployment Guide](/docs/agent-actions/deploy-to-devstack.md)
- [API Requests](/docs/projects/payment-pages-decomp/payment-pages-api.http)
- [Project Overview](/docs/projects/payment-pages-decomp/PAYMENT_PAGES_DECOMP.md)

