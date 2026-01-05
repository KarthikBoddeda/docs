# Payment Page Create Order - Status Code Diffs

**API:** `POST /v1/payment_pages/{id}/order`
**Route:** `payment_page_create_order`
**Total Failures:** 47,011
**Source:** `/pythonscripts/decomp-scripts/failure_logs/pp_create_order/`

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not Started |
| 🟢 | Fixed & Verified |
| 🔵 | Already Fixed / No Fix Needed |
| 🟠 | In Progress |
| 🔴 | Blocked |

---

## Diff Summary Table

> **Note:** Many errors are item-specific (e.g., `ppi_XXX is mandatory`). These are grouped by error pattern below.

| # | Diff Type | Count | M | N | Deployed | ReqFound | Reproduced | CodeEvidence | HotReload | TC1 | TC2 | TC3 | TC4 | DiffCheck | Status | Commit | Review | Notes |
|---|-----------|-------|---|---|----------|----------|------------|--------------|-----------|-----|-----|-----|-----|-----------|--------|--------|--------|-------|
| 1 | `amount should be equal to payment page item amount` | 22,437 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Amount validation mismatch |
| 2 | `ppi_XXX is mandatory payment page item, should be present` | 10,847 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Mandatory item validation |
| 3 | `order cannot be created for payment page which is not active` | 4,197 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Status check mismatch |
| 4 | `item ppi_XXX does not exist` | 3,504 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Item existence validation |
| 5 | `failed to unmarshal monolith response` (dual write) | 2,120 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Response parsing issue |
| 6 | `INVALID REQUEST PAYLOAD` | 824 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Request validation |
| 7 | `amount should not be lesser than the payment page item min_amount` | 535 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Min amount validation |
| 8 | `READ ONLY transaction` (DB error) | 227 | 200 | 400 | N/A | N/A | N/A | ✅ | N/A | N/A | N/A | N/A | N/A | N/A | 🔵 | N/A | ⬜ | DR drill Nov 19 2AM IST caused AZ failover |
| 9 | `line item count mismatch` (dual write) | 32 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Dual write sync issue |
| 10 | `no stock left` | 30 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Stock validation |
| 11 | `amount should not be greater than the payment page item max_amount` | 21 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Max amount validation |
| 12 | `internal server error` | 19 | 200 | 500 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | NCA internal error |

---

## Grouped Error Details

### `ppi_XXX is mandatory payment page item` (10,847 total)

This error occurs when NCA validates that a mandatory payment page item must be included in the order request. Sample item IDs with highest counts:

| Item ID | Count |
|---------|-------|
| ppi_RP98RPN02CeEyw | 3,527 |
| ppi_QI9NBuDrWFxcil | 2,509 |
| ppi_RWNquH0CVLdB0J | 947 |
| ppi_RRdZB6cYoeHM2z | 870 |
| ppi_RRdZBAse9hrzZX | 554 |
| ppi_R1BU9CJjUA937m | 475 |
| ... | ... |

### `item ppi_XXX does not exist` (3,504 total)

This error occurs when NCA cannot find the payment page item referenced in the order request. Sample item IDs:

| Item ID | Count |
|---------|-------|
| ppi_QAwuOsLJ7e5XTP | 1,965 |
| ppi_RTDctFmUXHaGdr | 412 |
| ppi_QPDvRadw7Gq8HS | 142 |
| ppi_R3KBULHsQAFVy1 | 129 |
| ppi_RM3FH5Vb1zujv3 | 121 |
| ... | ... |

---

## Workflow for Each Subtask

> **🚨 MANDATORY: Follow these steps IN ORDER. Do NOT skip steps. Do NOT mark complete without testing.**

### Phase 1: Analysis
1. **Deployed** - Check if fix is already in production
2. **ReqFound** - Find sample request in failure logs
3. **Reproduced** - Reproduce on devstack
4. **CodeEvidence** - Find root cause in code

### Phase 2: Implementation
5. **HotReload** - Deploy fix via hot-reload
6. **TC1-TC4** - Test cases pass

### Phase 3: Verification
7. **DiffCheck** - Verify with `DIFF_CHECKER_NO_DIFFS_FOUND`
8. **Status** - Mark final status

---

## Work Log

### Subtask #8: `READ ONLY transaction` (DB error) - 🔵 INFRA ISSUE (DR DRILL)

**Date:** 2026-01-05

**Error Details:**
- **MySQL Error:** `Error 1792 (25006): Cannot execute statement in a READ ONLY transaction.`
- **Occurrences:** 227 instances on Nov 18, 2025
- **Monolith:** Returned 200 (success)
- **NCA:** Returned 400 with db_error

**Important Architecture Note:**
> **Dual-write means Monolith and NCA have SEPARATE databases.** That's why it's called "dual writes" - each system writes to its own database independently.

**Root Cause Analysis:**
All 227 errors occurred on **2025-11-18** during the **Multi-AZ DR Drill** (Nov 19-20, 2025).

During the DR drill, one AZ was brought down causing database connections to failover. NCA's transaction started on a connection that got rerouted to a read-only replica during the AZ failover.

**Status:** 🔵 Not a Code Bug - Infrastructure-level transient issue during DR drill. No fix required.


