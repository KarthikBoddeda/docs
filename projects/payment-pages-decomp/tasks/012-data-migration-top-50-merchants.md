# Data Migration - Top 50 Merchants

**Created:** 2026-01-22

## Overview

Migrate Payment Pages data for the top 50 merchants (by order count) from TiDB (monolith) to NCA database and verify parity.

---

## Status

| Attribute | Value |
|-----------|-------|
| **Status** | ⬜ Not Started |
| **Priority** | P0 |
| **Estimated Effort** | 2-3 days |
| **Dependencies** | NCA service deployed, TiDB access |

---

## Pre-Migration Checklist

- [ ] **Identify Target Merchants**
  - Get top 50 merchant IDs from `/pythonscripts/decomp-scripts/target_merchants.tsv`
  - Merchants are sorted by `recent_orders_count` (descending)
  - Top 50 merchants have 5,000+ recent orders each

- [ ] **Get Payment Link IDs for Each Merchant**
  - Query TiDB to get all `payment_link_ids` for each merchant
  - Format: CSV with `pl_` prefix (e.g., `pl_ABC123`)

- [ ] **Verify Infrastructure**
  - NCA service is running (`nca-dark-concierge.razorpay.com` accessible)
  - TiDB connectivity is working
  - Auth credentials are valid (Basic auth in scripts)

- [ ] **Review Batch Limits**
  - Migration API processes 100 pl_ids per batch
  - Query limits: 10,000 per table, 20,000 for settings
  - Plan batch execution accordingly

---

## Migration Execution

### Step 1: Prepare Input File

Create `input_datafix.csv` in `/pythonscripts/decomp-scripts/migration/` with payment link IDs:

```csv
pl_ABC123
pl_DEF456
pl_GHI789
...
```

> **Note:** Each line must start with `pl_` prefix. The script strips this prefix before calling the API.

### Step 2: Run Migration Script

```bash
cd /Users/boddedakarthik.s/rzp/pythonscripts/decomp-scripts/migration
python3 datafix.py
```

**What the script does:**
1. Reads pl_ids from `input_datafix.csv`
2. Sends batch requests (100 IDs at a time) to TiDB migration API
3. Writes results to `output_datafix.csv`
4. Shows progress bar with ETA

### Step 3: Monitor Output

Check `output_datafix.csv` for:
- [ ] All batches show `status: success`
- [ ] No error responses
- [ ] All pl_ids processed

### Step 4: Handle Failures

If any batches fail:
1. Extract failed pl_ids from output
2. Create new input CSV with only failed IDs
3. Re-run the migration script
4. Investigate persistent failures

---

## Post-Migration Parity Verification

### Step 1: Dashboard API Parity (`parity_checker.py`)

Verifies `GET /v1/payment_pages/{id}/details` returns same data from NCA and monolith.

```bash
cd /Users/boddedakarthik.s/rzp/pythonscripts/decomp-scripts/parity

# Prepare input
# parity_input.csv format: merchant_id,payment_link_id (without pl_ prefix)
echo "merchant_id,payment_link_id" > parity_input.csv
# Add rows...

python3 parity_checker.py
```

- [ ] Run parity checker for all migrated pages
- [ ] Review `parity_output.csv` for diffs

### Step 2: Hosted Page Parity (`parity_hosted.py`)

Verifies `GET /v1/pages/{id}/view` (customer-facing hosted page).

```bash
cd /Users/boddedakarthik.s/rzp/pythonscripts/decomp-scripts/parity_hosted

# Prepare input
# parity_hosted_input.csv format: merchant_id,payment_link_id
python3 parity_hosted.py
```

- [ ] Run hosted parity checker
- [ ] Review `parity_hosted_output.csv` for diffs

### Step 3: List API Parity (`parity_list.py`)

Verifies `GET /v1/payment_pages` (list of pages for merchant).

```bash
cd /Users/boddedakarthik.s/rzp/pythonscripts/decomp-scripts/parity_list

# Prepare input
# parity_list_input.csv format: merchant_id
python3 parity_list.py
```

- [ ] Run list parity checker
- [ ] Review `parity_list_output.csv` for diffs

---

## Analyzing Parity Results

### Filter Large Response Columns

```bash
cd /Users/boddedakarthik.s/rzp/pythonscripts/decomp-scripts/parity
python3 filter.py
```

Removes `monolith_resp` and `nca_resp` columns for easier analysis.

### Ignore Expected Diffs

```bash
python3 ignore.py
```

Filters out known acceptable diff paths:
- `/captured_payments_count` - Real-time count, expected to differ
- `/payment_page_items//quantity_sold` - Real-time analytics
- `/payment_page_items//total_amount_paid` - Real-time analytics
- `/total_amount_paid` - Real-time analytics
- `/times_payable` - Computed field
- `/description` - HTML encoding differences
- `/settings/udf_schema` - Schema differences

### Review Remaining Diffs

After filtering, check `ignored_parity_output.csv`:
- [ ] No rows = perfect parity
- [ ] Rows present = investigate each diff

---

## Validation Criteria

### Success Criteria

- [ ] All payment pages migrated successfully (no failures in output)
- [ ] Dashboard API parity: No critical diffs after filtering
- [ ] Hosted page parity: No critical diffs after filtering
- [ ] List API parity: No critical diffs after filtering
- [ ] All APIs return HTTP 200

### Rollback Plan

If critical issues found:
1. Identify affected pl_ids
2. Delete from NCA database (use bulk delete functions)
3. Re-migrate after fixing issues

---

## Merchant Batching Strategy

### Recommended Approach

Process merchants in batches of 5-10:

| Batch | Merchants | Estimated Pages | Notes |
|-------|-----------|-----------------|-------|
| 1 | Top 5 | ~150 pages | Highest volume, test thoroughly |
| 2 | 6-10 | ~100 pages | |
| 3 | 11-20 | ~200 pages | |
| 4 | 21-30 | ~150 pages | |
| 5 | 31-50 | ~300 pages | |

### Per-Batch Checklist

For each batch:
- [ ] Prepare input CSV with pl_ids
- [ ] Run migration
- [ ] Verify success in output
- [ ] Run all three parity checkers
- [ ] Analyze and resolve diffs
- [ ] Sign off before next batch

---

## Work Log

| Date | Action | Status | Notes |
|------|--------|--------|-------|
| | | | |

---

## Related Resources

- [Data Migration Scripts Guide](/docs/projects/payment-pages-decomp/data-migration-scripts-guide.md) - Detailed script documentation
- [Target Merchants List](/pythonscripts/decomp-scripts/target_merchants.tsv)
- [Migration Script](/pythonscripts/decomp-scripts/migration/datafix.py)
- [Parity Scripts](/pythonscripts/decomp-scripts/parity/)
- [TiDB Migration API Implementation](/no-code-apps-datafixes/internal/modules/payment_page/tidb_data_migration.go)
