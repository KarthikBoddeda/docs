# Payment Page Set Receipt Details - Status Code Diffs

**Created:** 2026-01-05  
**API:** `POST /v1/payment_pages/{id}/set_receipt_details`  
**Route:** `payment_page_set_receipt_details`
**Total Failures:** 236
**Source:** `/pythonscripts/decomp-scripts/failure_logs/payment_page_set_receipt_details/`

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

| # | Diff Type | Count | M | N | Deployed | ReqFound | Reproduced | CodeEvidence | HotReload | TC1 | TC2 | TC3 | TC4 | DiffCheck | Status | Commit | Review | Notes |
|---|-----------|-------|---|---|----------|----------|------------|--------------|-----------|-----|-----|-----|-----|-----------|--------|--------|--------|-------|
| 1 | `input field not present` (lowercase) | 195 | 200 | 400 | N/A | ✅ | N/A | ✅ | N/A | N/A | N/A | N/A | N/A | N/A | 🔵 | N/A | ⬜ | **Data mismatch** - NCA's UDF schema missing field Monolith has |
| 2 | `Input field not present` (capital I) | 18 | 400 | 200 | N/A | ✅ | N/A | ✅ | N/A | N/A | N/A | N/A | N/A | N/A | 🔵 | N/A | ⬜ | **Data mismatch** - Monolith's UDF schema missing field NCA has |
| 3 | `READ ONLY transaction` (DB error) | 12 | 200 | 400 | N/A | ✅ | N/A | ✅ | N/A | N/A | N/A | N/A | N/A | N/A | 🔵 | N/A | ⬜ | DR drill Nov 19 2AM IST caused AZ failover |
| 4 | `The id provided does not exist` | 11 | 400 | 200 | N/A | ✅ | N/A | ✅ | N/A | N/A | N/A | N/A | N/A | N/A | 🔵 | N/A | ⬜ | **Data mismatch** - Page exists in NCA DB, not in Monolith DB |

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

### Subtask #3: `READ ONLY transaction` (DB error) - 🔵 INFRA ISSUE (DR DRILL)

**Date:** 2026-01-05

**Error Details:**
- **MySQL Error:** `Error 1792 (25006): Cannot execute statement in a READ ONLY transaction.`
- **Occurrences:** 12 instances on Nov 18, 2025
- **Monolith:** Returned 200 (success)
- **NCA:** Returned 400 with db_error

**Important Architecture Note:**
> **Dual-write means Monolith and NCA have SEPARATE databases.** That's why it's called "dual writes" - each system writes to its own database independently.

**Root Cause Analysis:**
All 12 errors occurred on **2025-11-18** during the **Multi-AZ DR Drill** (Nov 19-20, 2025).

During the DR drill, one AZ was brought down causing database connections to failover. NCA's transaction started on a connection that got rerouted to a read-only replica during the AZ failover.

**Status:** 🔵 Not a Code Bug - Infrastructure-level transient issue during DR drill. No fix required.

---

### 2026-01-05: Full Analysis

#### Subtask #1: `input field not present` (lowercase) - 🔵 DATA MISMATCH

**What happens:**
- Monolith returns 200 (success)
- NCA returns 400 with `validation_failure: input field not present`

**Root Cause:**
- Both NCA and Monolith have the **same validation logic** for `selected_udf_field`
- The validation checks if `selected_udf_field` value exists in the payment page's UDF schema
- NCA's UDF schema data is **missing fields** that Monolith's schema has
- This is a **data synchronization** issue, not a code issue

**Evidence:**
```
// NCA validation (core.go:523-552)
func validateSelectedUdfField(ctx context.Context, udfSchemaString *string, selectedField *string) errors.IError {
    valErr := errorclass.ErrValidationFailure.New("").Wrap(goerr.New("input field not present"))
    // ... loops through UDF schema to find matching field
}

// Monolith validation (Validator.php:1085-1105)
public function validateSelectedUdfField(string $attribute, string $value) {
    // ... same logic, throws "Input field not present"
}
```

**Resolution:** Fix UDF schema data in NCA database. No code change.

---

#### Subtask #2: `Input field not present` (capital I) - 🔵 DATA MISMATCH

**What happens:**
- Monolith returns 400 with `Input field not present`
- NCA returns 200 (success)

**Root Cause:**
- **Opposite** of Subtask #1
- Monolith's UDF schema is **missing fields** that NCA's schema has
- The `selected_udf_field` value (e.g., "calendar_type") exists in NCA but not in Monolith

**Sample Log:**
```json
{
  "selected_udf_field": "calendar_type",
  "monolith_status_code": 400,
  "shadow_status_code": 200
}
```

**Resolution:** Fix UDF schema data in Monolith database. No code change.

---

#### Subtask #4: `The id provided does not exist` - 🔵 DATA MISMATCH

**What happens:**
- Monolith returns 400 with `The id provided does not exist`
- NCA returns 200 (success)

**Root Cause:**
- The payment page exists in **NCA's database** but **NOT in Monolith's database**
- This is a data synchronization issue where pages were created in NCA but not Monolith

**Resolution:** Fix payment page data - ensure pages exist in both databases. No code change.

---

### Summary

| # | Issue | Type | Resolution |
|---|-------|------|------------|
| 1 | NCA: `input field not present` | Data | Sync UDF schema to NCA |
| 2 | Monolith: `Input field not present` | Data | Sync UDF schema to Monolith |
| 3 | `READ ONLY transaction` | Infra | DR drill - transient |
| 4 | `The id provided does not exist` | Data | Sync page data to Monolith |

**All issues are data mismatch - no code fixes required.**

