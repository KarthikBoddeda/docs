# Phase 3 - Response Body Key Diff Fixes

**Created:** 2026-02-14  
**Status:** 🟡 In Progress  
**Priority:** P0  
**Data Source:** `/pythonscripts/decomp-scripts/diff_logs/phase_3/` analysis reports (generated 2026-02-14)  
**Proxy State:** `dual_write_shadow_read_no_external`

---

## Context

After multiple phases of data migration and diff fixes, the diff checker still reports response body key mismatches between monolith and NCA. These indicate:
- **Data sync issues** - NCA database not in sync with monolith (analytics counters, missing pages, status, item data)
- **Code fixes needed** - NCA serialization/logic doesn't match monolith
- **Data migration gaps** - Fields not migrated or not kept in sync

Each mismatch means the NCA response doesn't exactly match the monolith response, even though both return the same HTTP status code. **Monolith is source of truth.**

---

## Grand Summary

| Route | Log Rows | Total Diffs | Unique Paths | Analysis File |
|-------|----------|-------------|--------------|---------------|
| `pages_view` | 10,929 | 23,025 | 19 | `/pythonscripts/decomp-scripts/diff_logs/phase_3/pages_view/analysis.md` |
| `payment_page_list` | 594 | 1,770 | 8 | `/pythonscripts/decomp-scripts/diff_logs/phase_3/payment_page_list/analysis.md` |
| `pages_view_post` | 176 | 563 | 5 | `/pythonscripts/decomp-scripts/diff_logs/phase_3/pages_view_post/analysis.md` |
| `payment_page_get_details` | 69 | 241 | 17 | `/pythonscripts/decomp-scripts/diff_logs/phase_3/payment_page_get_details/analysis.md` |
| `payment_page_update` | 8 | 23 | 5 | `/pythonscripts/decomp-scripts/diff_logs/phase_3/payment_page_update/analysis.md` |
| `payment_page_create` | 6 | 6 | 2 | `/pythonscripts/decomp-scripts/diff_logs/phase_3/payment_page_create/analysis.md` |
| **Total** | **11,782** | **25,628** | | |

---

## Subtasks by Route

---

### 1. `pages_view` (23,025 diffs, 19 paths)

**API:** GET/POST `/v1/pages/{id}/view` (hosted page for customers)  
**Categorized logs:** `/pythonscripts/decomp-scripts/diff_logs/phase_3/pages_view/categorized/`

#### 1A. Analytics Counters (data_value_mismatch)

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 1A-1 | `/payment_link/payment_page_items//quantity_available` | 7,536 | data_value_mismatch | ⬜ |
| 1A-2 | `/payment_link/settings/goal_tracker/meta_data/collected_amount` | 2,951 | data_value_mismatch | ⬜ |
| 1A-3 | `/payment_link/settings/goal_tracker/meta_data/sold_units` | 2,951 | data_value_mismatch | ⬜ |
| 1A-4 | `/payment_link/settings/goal_tracker/meta_data/supporter_count` | 2,951 | data_value_mismatch | ⬜ |
| 1A-5 | `/payment_link/settings/goal_tracker/meta_data/available_units` | 2,943 | extra_field_nca (2,939) + missing_field_nca (4) | ⬜ |

**Root Cause:** NCA splitz gate (`PaymentCallback` experiment) may skip payment event processing. See [015-live-analytics-non-cached-spec.md](./015-live-analytics-non-cached-spec.md).

**Samples (1A-1):** monolith=19 vs NCA=20, monolith=17 vs NCA=18 (NCA consistently 1 higher — indicates NCA processes events monolith skips, or vice versa)

**Samples (1A-5):** monolith=`null`, NCA=`0`. NCA returns `available_units: 0` as an extra field when monolith doesn't return it at all.

#### 1B. Item Data Mismatch (367 diffs each - likely single page with bad item data)

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 1B-1 | `/payment_link/payment_page_items//item/active` | 367 | data_value_mismatch | ⬜ |
| 1B-2 | `/payment_link/payment_page_items//item/amount` | 367 | data_not_present | ⬜ |
| 1B-3 | `/payment_link/payment_page_items//item/currency` | 367 | data_value_mismatch | ⬜ |
| 1B-4 | `/payment_link/payment_page_items//item/id` | 367 | data_value_mismatch | ⬜ |
| 1B-5 | `/payment_link/payment_page_items//item/name` | 367 | data_value_mismatch | ⬜ |
| 1B-6 | `/payment_link/payment_page_items//item/type` | 367 | data_value_mismatch | ⬜ |
| 1B-7 | `/payment_link/payment_page_items//item/unit_amount` | 367 | data_not_present | ⬜ |
| 1B-8 | `/payment_link/payment_page_items//mandatory` | 367 | data_value_mismatch | ⬜ |
| 1B-9 | `/payment_link/payment_page_items//settings/position` | 367 | missing_field_nca | ⬜ |

**Root Cause:** NCA item data is completely wrong for some payment pages — item `id`, `name`, `currency`, `type`, `amount`, `unit_amount` are all empty/null/wrong in NCA while monolith has correct values. `active` is `false` in NCA but `true` in monolith. `mandatory` is `false` in NCA vs `true` in monolith. `settings/position` is missing (`null`) in NCA.

**Samples:**
- `item/id`: monolith=`item_SFg16CUN8N4TB1`, NCA=`` (empty)
- `item/name`: monolith=`AMOUNT`, NCA=`` (empty)
- `item/active`: monolith=`true`, NCA=`false`
- `item/amount`: monolith=`66600`, NCA=`null`

**Analysis:** All 9 paths have exactly 367 diffs, strongly suggesting this is a **single payment page (or small set)** with corrupted/missing item data in NCA. The item entity in NCA was either not migrated or created incorrectly.

**Next Steps:**
- [ ] Identify the affected payment page IDs from categorized logs
- [ ] Check if this is a data migration gap (item not synced) or a dual-write bug (item created incorrectly)
- [ ] Fix via data migration or API re-sync

#### 1C. Status/Status Reason Mismatch

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 1C-1 | `/payment_link/status` | 180 | data_value_mismatch | ⬜ |
| 1C-2 | `/payment_link/status_reason` | 182 | data_not_present (180) + data_value_mismatch (2) | ⬜ |

**Samples:**
- `status`: monolith=`inactive`, NCA=`active` (NCA thinks page is active, monolith says inactive)
- `status_reason`: monolith=`completed`, NCA=`null` (NCA missing the completed status_reason)

**Root Cause:** Pages were deactivated/completed in monolith but NCA didn't process the status change. **Data sync issue** - either the deactivate/expire webhook wasn't processed by NCA, or the status was manually changed in monolith.

**Next Steps:**
- [ ] Identify affected payment page IDs
- [ ] Sync status and status_reason from monolith to NCA database

#### 1D. Expire By Mismatch

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 1D-1 | `/payment_link/expire_by` | 13 | data_value_mismatch | ⬜ |
| 1D-2 | `/payment_link/expire_by_formatted` | 13 | data_value_mismatch | ⬜ |

**Samples:**
- `expire_by`: monolith=`1770402599`, NCA=`1770056999` (different timestamps, ~4 day difference)
- `expire_by_formatted`: monolith=`6 Feb 2026`, NCA=`2 Feb 2026`

**Root Cause:** `expire_by` values differ between monolith and NCA databases. Either the page was updated in monolith (expire_by changed) and NCA didn't sync, or the migration copied an old value.

**Next Steps:**
- [ ] Identify affected payment page IDs
- [ ] Sync `expire_by` from monolith to NCA database

#### 1E. Title Mismatch

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 1E-1 | `/payment_link/title` | 2 | data_value_mismatch | ⬜ |

**Samples:**
- monolith=`E-133 (No Blouse Piece)`, NCA=`E-133`

**Root Cause:** Title was updated in monolith but NCA has stale value. **Data sync issue.**

**Next Steps:**
- [ ] Identify payment page and sync title

---

### 2. `pages_view_post` (563 diffs, 5 paths)

**API:** POST `/v1/pages/{id}/view` (hosted page POST variant)  
**Categorized logs:** `/pythonscripts/decomp-scripts/diff_logs/phase_3/pages_view_post/categorized/`

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 2-1 | `/payment_link/settings/goal_tracker/meta_data/collected_amount` | 131 | data_value_mismatch | ⬜ |
| 2-2 | `/payment_link/settings/goal_tracker/meta_data/sold_units` | 131 | data_value_mismatch | ⬜ |
| 2-3 | `/payment_link/settings/goal_tracker/meta_data/supporter_count` | 131 | data_value_mismatch | ⬜ |
| 2-4 | `/payment_link/settings/goal_tracker/meta_data/available_units` | 125 | extra_field_nca | ⬜ |
| 2-5 | `/payment_link/payment_page_items//quantity_available` | 45 | data_value_mismatch | ⬜ |

**Root Cause:** Same as `pages_view` analytics counters (#1A). Same code path, same splitz gate issue.

---

### 3. `payment_page_list` (1,770 diffs, 8 paths)

**API:** GET `/v1/payment_pages` (dashboard list API)  
**Categorized logs:** `/pythonscripts/decomp-scripts/diff_logs/phase_3/payment_page_list/categorized/`

#### 3A. Data Sync - Missing/Extra Pages

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 3A-1 | `pages_extra_in_nca` | 399 | data_not_present | ⬜ |
| 3A-2 | `pages_missing_in_nca` | 395 | data_not_present | ⬜ |
| 3A-3 | `/count` | 49 | data_value_mismatch | ⬜ |

**Samples:**
- `pages_extra_in_nca`: NCA has pages like `pl_SFfxKxPq5q5LUJ`, `pl_SFfvLvr8yaMouR` that monolith doesn't return
- `pages_missing_in_nca`: Monolith has pages like `pl_SEnYTXAwer4MT3`, `pl_SCSV1jew0iaDMe` that NCA doesn't have
- `/count`: monolith=`2`, NCA=`100`; monolith=`4`, NCA=`25`

**Root Cause:** Bidirectional data sync gap:
- Pages created in monolith before dual-write that weren't migrated to NCA (missing_in_nca)
- Pages somehow existing in NCA but not monolith (extra_in_nca) - possibly from failed dual-writes where monolith rejected but NCA created
- Count mismatches reflect the total page count difference

**Next Steps:**
- [ ] Extract page ID lists from categorized logs
- [ ] Run data migration for missing pages
- [ ] Investigate and clean up extra pages in NCA

#### 3B. Analytics Values

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 3B-1 | `/items//payment_page_items//quantity_sold` | 286 | data_value_mismatch | ⬜ |
| 3B-2 | `/items//payment_page_items//total_amount_paid` | 286 | data_value_mismatch | ⬜ |
| 3B-3 | `/items//total_amount_paid` | 245 | data_value_mismatch | ⬜ |

**Root Cause:** Same analytics counter sync issue as #1A. Item-level and page-level amounts not synced.

#### 3C. Image URL Missing

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 3C-1 | `/items//payment_page_items//image_url` | 90 | data_not_present | ⬜ |

**Samples:** monolith=`https://s3.ap-south-1.amazonaws.com/rzp-prod-merch...`, NCA=`null`

**Root Cause:** `image_url` field not populated in NCA for some payment page items. Could be a data migration gap (field not copied) or a code issue (field not being stored/returned).

**Next Steps:**
- [ ] Check if `image_url` is stored in NCA database
- [ ] If stored but not returned: code fix in response serialization
- [ ] If not stored: data migration fix

#### 3D. Expire By Mismatch

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 3D-1 | `/items//expire_by` | 20 | data_value_mismatch | ⬜ |

**Samples:** monolith=`1770488999`, NCA=`1768501799` (different timestamps)

**Root Cause:** Same as #1D - `expire_by` values differ between databases.

---

### 4. `payment_page_get_details` (241 diffs, 17 paths)

**API:** GET `/v1/payment_pages/{id}/details` (dashboard details API)  
**Categorized logs:** `/pythonscripts/decomp-scripts/diff_logs/phase_3/payment_page_get_details/categorized/`

#### 4A. Image URL Mismatch

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 4A-1 | `/payment_page_items//image_url` | 66 | data_value_mismatch | ⬜ |

**Samples:** Both monolith and NCA return S3 URLs but they differ. Need to check if NCA is storing a stale/different image URL.

**Root Cause:** `image_url` differs between monolith and NCA. Unlike list route (where NCA returns `null`), here both have URLs but different ones. Likely a data migration issue where the URL was updated in monolith after migration.

#### 4B. Analytics Values

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 4B-1 | `/payment_page_items//quantity_sold` | 33 | data_value_mismatch | ⬜ |
| 4B-2 | `/payment_page_items//total_amount_paid` | 33 | data_value_mismatch | ⬜ |
| 4B-3 | `/total_amount_paid` | 29 | data_value_mismatch | ⬜ |
| 4B-4 | `/captured_payments_count` | 27 | data_value_mismatch | ⬜ |

**Root Cause:** Same analytics counter sync issue. `captured_payments_count` is a new field not seen in other routes — likely derived from the same payment event data.

#### 4C. User Fields

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 4C-1 | `/user/email` | 13 | data_format_null_vs_empty | ⬜ |
| 4C-2 | `/user/metadata` | 10 | missing_field_nca | ⬜ |
| 4C-3 | `/user/contact_mobile` | 5 | data_value_mismatch | ⬜ |
| 4C-4 | `/user/contact_mobile_verified` | 5 | data_value_mismatch | ⬜ |
| 4C-5 | `/user/second_factor_auth_setup` | 5 | data_value_mismatch | ⬜ |

**Samples:**
- `email`: monolith=`null`, NCA=`""` (null vs empty)
- `metadata`: monolith=`{'ownership_transfer': True, 'sender_user_id': 'Rn...}`, NCA=`null` (missing)
- `contact_mobile`: monolith=`+919606496410`, NCA=`` (empty)
- `contact_mobile_verified`: monolith=`true`, NCA=`false`
- `second_factor_auth_setup`: monolith=`true`, NCA=`false`

**Root Cause:** NCA fetches user data from an API but the response either doesn't include all fields or NCA doesn't map them correctly. The `metadata` field is completely missing in NCA. The `contact_mobile`, `contact_mobile_verified`, and `second_factor_auth_setup` fields suggest NCA is returning stale/default user data.

**Next Steps:**
- [ ] Check how NCA fetches user details and what fields it maps
- [ ] Fix `email` null vs empty serialization
- [ ] Add `metadata` field to user response
- [ ] Fix `contact_mobile`, `contact_mobile_verified`, `second_factor_auth_setup` mapping

#### 4D. Status/Expire By

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 4D-1 | `/status` | 4 | data_value_mismatch | ⬜ |
| 4D-2 | `/status_reason` | 4 | data_not_present | ⬜ |
| 4D-3 | `/expire_by` | 2 | data_value_mismatch | ⬜ |

**Samples:**
- `status`: monolith=`active`, NCA=`inactive`
- `status_reason`: monolith=`null`, NCA=`expired`
- `expire_by`: monolith=`1771093799`, NCA=`1770920999`

**Root Cause:** Same data sync issues as #1C and #1D.

#### 4E. Analytics (Goal Tracker)

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 4E-1 | `/settings/goal_tracker/meta_data/available_units` | 2 | extra_field_nca | ⬜ |
| 4E-2 | `/settings/goal_tracker/meta_data/collected_amount` | 1 | data_value_mismatch | ⬜ |
| 4E-3 | `/settings/goal_tracker/meta_data/sold_units` | 1 | data_value_mismatch | ⬜ |
| 4E-4 | `/settings/goal_tracker/meta_data/supporter_count` | 1 | data_value_mismatch | ⬜ |

**Root Cause:** Same analytics sync issue as #1A.

---

### 5. `payment_page_update` (23 diffs, 5 paths)

**API:** PUT `/v1/payment_pages/{id}` (update payment page)  
**Categorized logs:** `/pythonscripts/decomp-scripts/diff_logs/phase_3/payment_page_update/categorized/`

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 5-1 | `/payment_page_items//quantity_sold` | 7 | data_value_mismatch | ⬜ |
| 5-2 | `/payment_page_items//total_amount_paid` | 7 | data_value_mismatch | ⬜ |
| 5-3 | `/total_amount_paid` | 7 | data_value_mismatch | ⬜ |
| 5-4 | `/status` | 1 | data_value_mismatch | ⬜ |
| 5-5 | `/status_reason` | 1 | data_not_present | ⬜ |

**Samples:**
- `quantity_sold`: monolith=3491, NCA=3488
- `status`: monolith=`active`, NCA=`inactive`
- `status_reason`: monolith=`null`, NCA=`expired`

**Root Cause:** Analytics sync + status sync (same as other routes).

---

### 6. `payment_page_create` (6 diffs, 2 paths)

**API:** POST `/v1/payment_pages` (create payment page)  
**Categorized logs:** `/pythonscripts/decomp-scripts/diff_logs/phase_3/payment_page_create/categorized/`

| # | Diff Path | Count | Category | Status |
|---|-----------|-------|----------|--------|
| 6-1 | `/user/contact_mobile` | 4 | data_format_null_vs_empty | ⬜ |
| 6-2 | `/user/metadata` | 2 | missing_field_nca | ⬜ |

**Samples:**
- `contact_mobile`: monolith=`null`, NCA=`""` (null vs empty)
- `metadata`: monolith=`{'ownership_transfer': True, ...}`, NCA=`null`

**Root Cause:**
- **6-1:** Code fix - NCA returns `""` instead of `null` when `contact_mobile` is empty.
- **6-2:** Code fix - NCA doesn't return `user.metadata` field. Same as #4C-2.

---

## Cross-Cutting Issues

### A. Analytics Counters Not Synced

**Affects:** 1A, 2-1 to 2-5, 3B, 4B, 4E, 5-1 to 5-3  
**Total Diffs:** ~20,000+  
**Fields:** `collected_amount`, `sold_units`, `supporter_count`, `available_units`, `quantity_available`, `quantity_sold`, `total_amount_paid`, `captured_payments_count`

**Root Cause:** NCA splitz gate (`PaymentCallback` experiment) controls whether payment events are processed. Not at 100%.

**Fix:** Enable `PaymentCallback` splitz at 100%. See [015-live-analytics-non-cached-spec.md](./015-live-analytics-non-cached-spec.md).

### B. Item Data Corruption/Missing (pages_view)

**Affects:** 1B (all 9 item fields, 367 diffs each = 3,303 total)

**Root Cause:** Item entity data in NCA is empty/wrong for a subset of payment pages. Likely a data migration gap.

**Fix:** Identify affected pages and re-migrate item data from monolith.

### C. Status/Status_Reason Out of Sync

**Affects:** 1C, 4D-1/2, 5-4/5  
**Total Diffs:** ~372

**Root Cause:** Pages deactivated/completed/expired in monolith but NCA has stale status.

**Fix:** Sync status values from monolith to NCA database.

### D. Expire By Mismatch

**Affects:** 1D, 3D, 4D-3  
**Total Diffs:** ~35

**Root Cause:** `expire_by` updated in monolith after initial migration.

**Fix:** Sync `expire_by` values from monolith to NCA.

### E. User Fields Not Complete

**Affects:** 4C, 6-1, 6-2  
**Total Diffs:** ~52  
**Fields:** `email` (null vs empty), `metadata` (missing), `contact_mobile` (value mismatch), `contact_mobile_verified`, `second_factor_auth_setup`

**Root Cause:** NCA user fetch doesn't return all fields, or serialization differs.

**Fix:** Code fix to map all user fields correctly + null vs empty normalization.

### F. Image URL Missing/Different

**Affects:** 3C, 4A  
**Total Diffs:** ~156

**Root Cause:** `image_url` either not migrated or differs between databases.

**Fix:** Data migration for missing URLs + investigate value mismatches.

### G. Pages Missing/Extra in NCA (List API)

**Affects:** 3A  
**Total Diffs:** ~843

**Root Cause:** Bidirectional data sync gap between monolith and NCA databases.

**Fix:** Run data migration for missing pages, investigate/clean extra pages.

---

## Priority Order (Suggested)

| Priority | Issue | Impact | Fix Type |
|----------|-------|--------|----------|
| 1 | **A. Analytics counters** | ~20,000 diffs | Splitz config (no code change) |
| 2 | **B. Item data corruption** | 3,303 diffs | Data migration |
| 3 | **G. Pages missing/extra** | 843 diffs | Data migration |
| 4 | **C. Status/status_reason** | 372 diffs | Data sync |
| 5 | **F. Image URL** | 156 diffs | Data migration + investigation |
| 6 | **E. User fields** | 52 diffs | Code fix |
| 7 | **D. Expire by** | 35 diffs | Data sync |
