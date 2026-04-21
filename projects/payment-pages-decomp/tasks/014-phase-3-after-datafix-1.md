# Phase 3 After Datafix - Status Code Diff Analysis

**Created:** 2026-01-23  
**Updated:** 2026-01-27 (Added hosted view diff analysis)  
**Proxy State:** `dual_write_shadow_read_no_external`

---

## Hosted View Diff Analysis (pages_view)

### Diff Categories

| # | Diff Path | Count | Status | Type |
|---|-----------|-------|--------|------|
| 1 | `/payment_link/payment_page_items//item/description` | 70,147 | **Open** | Code Fix |
| 2 | `/payment_link/expire_by_formatted` | 59,025 | **Fixed** ✅ | Code + Data |
| 3 | `/payment_link/settings/goal_tracker/meta_data/goal_end_timestamp_formatted` | 9,611 | **Open** | Code Fix |
| 4 | `/merchant/support_email` | 2,513 | **Fixed** ✅ | Code Fix |
| 5 | `/org/branding/branding_logo` | 846 | **Fixed** ✅ | Code Fix |
| 6 | `/payment_link/status` + `/status_reason` | 275 each | **Open** | Data Fix |
| 7 | `/payment_link/payment_page_items//settings` | 74 | **Open** | Code Fix |

### Code Fixes Checklist

- [x] **expire_by_formatted** - Changed format from `"02 Jan 2006"` to `"2 Jan 2006"` (no zero-padding)
- [x] **support_email** - Use `StringToStringPtrWhereEmptyIsNil()` to return null instead of empty string
- [x] **branding_logo** - Added conditional `else` clause to not overwrite merchant's logo
- [x] **item/description** - Already fixed with `StringToStringPtr()` (returns "" for empty descriptions)
- [x] **goal_end_timestamp_formatted** - Fixed: Removed midnight truncation to match Carbon's `diffInDays()` behavior
- [x] **payment_page_items//settings** - Added `SkipEmptyArrayAndObjectPathRegexes` config to treat `[]` and `{}` as equivalent (still checks for actual content differences)

---

## Summary

After the data fixes, monitoring shows the following status code mismatches:

| Route | Error | Count | Status | Type |
|-------|-------|-------|--------|------|
| payment_page_list | `json: cannot unmarshal object into Go value of type []interface {}` | 33 | **Open** | Code Fix |
| payment_page_get_details | `json: cannot unmarshal object into Go value of type []interface {}` | 1 | **Open** | Code Fix |
| payment_page_get_details | `record_not_found: record not found` | 7 | **Open** | Data Fix |
| payment_page_activate | `Cannot activate a payment page that has already expired` | 2 | Investigate | Behavior Diff |
| payment_page_activate | `Payment link cannot be activated as it is already active` | 2 | Investigate | Behavior Diff |
| payment_page_create_order | `order cannot be created for payment page which is not active` | 2 | **Open** | Data Sync |
| pages_view | NCA HTML error (cache miss + API timeout) | 5 | **Open** | Code Fix |
| pages_view | NCA case-insensitive ID lookup (should be case-sensitive) | 52 | **Open** | Code Fix |

**Grand Total:** 104 logs analyzed
- **Code Fixes Required:** 91 (34 JSON unmarshal + 5 NCA HTML cache + 52 case-sensitivity)
- **Data Fixes Required:** 9 (7 record_not_found + 2 order for inactive)
- **Behavior Decisions Needed:** 4 (activate validation differences)

---

## Issues Requiring Code Fixes

### 1. JSON Unmarshal Error (payment_page_list + payment_page_get_details)

**Error Message:**
```
internal_error: json: cannot unmarshal object into Go value of type []interface {}
```

**Total Occurrences:** 34 (33 in list + 1 in get_details)

**Affected Routes:**
- `payment_page_list`: 33 occurrences across 4 days
- `payment_page_get_details`: 1 occurrence

**Sample Occurrences (payment_page_list):**

| # | Task ID | Request ID | Merchant ID | Timestamp |
|---|---------|------------|-------------|-----------|
| 1 | `d5pmoa1s5lkc713e93eg` | `d5pmoa1s5lkc713e93e0` | `F4nh3jBiH6yDGz` | 2026-01-23T12:40:09.232Z |
| 2 | `d5pmf8cgr0rs7176o4cg` | `d5pmf8cgr0rs7176o4c0` | `F4nh3jBiH6yDGz` | 2026-01-23T12:20:50.325Z |

**Sample Occurrence (payment_page_get_details):**

| # | Task ID | Request ID | Merchant ID | Payment Page | Timestamp |
|---|---------|------------|-------------|--------------|-----------|
| 1 | `d5rhg9cgr0rs717gers0` | `d5rhg9cgr0rs717gerrg` | `G7NMeax5Gewf8a` | `pl_IyjugjxfgZMqSQ` | 2026-01-26T07:30:46.538Z |

**Root Cause:**

The `udf_schema` field stored in the database for some payment pages contains `{}` (empty object) instead of `[]` (empty array). When NCA tries to unmarshal this into `[]interface{}`, it fails.

**Affected Function:**

`no-code-apps/internal/modules/payment_page/response.go` → `getUdfStringForV1Pages()`

**Next Steps:**

- [ ] Fix `getUdfStringForV1Pages()` to handle `{}` as equivalent to `[]`
- [ ] Verify fix is deployed to production
- [ ] Run data fix to correct `udf_schema` values in affected payment pages

---

## Issues Requiring Data Fixes

### 2. payment_page_get_details - Record Not Found

**Error Message:**
```
record_not_found: record not found
```

**Occurrences:** 7 (all for the same payment page)

| # | Task ID | Request ID | Merchant ID | Payment Page | Timestamp |
|---|---------|------------|-------------|--------------|-----------|
| 1 | `d5s5f665p2gc715g5v70` | `d5s5f665p2gc715g5v6g` | `RnV89DaE06b2kn` | `pl_S1IMEdQOlHbpx0` | 2026-01-27T06:13:45.258Z |
| 2 | `d5s3mju5p2gc715foebg` | `d5s3mju5p2gc715foeb0` | `RnV89DaE06b2kn` | `pl_S1IMEdQOlHbpx0` | 2026-01-27T04:13:03.456Z |
| 3 | `d5rp876r4dbs716m20ag` | `d5rp876r4dbs716m20a0` | `RnV89DaE06b2kn` | `pl_S1IMEdQOlHbpx0` | 2026-01-26T16:19:40.495Z |

**Root Cause:**

Payment page `pl_S1IMEdQOlHbpx0` exists in the monolith database but NOT in the NCA database. This is a data migration issue.

**Payment Page Details:**
- **ID:** `pl_S1IMEdQOlHbpx0`
- **Merchant:** `RnV89DaE06b2kn`
- **Created At:** 1767855815 (2026-01-08)
- **Title:** "Jamming Session"
- **Status:** inactive (expired)

**Root Cause Analysis:**

This is a **data migration gap**:
- Merchant `RnV89DaE06b2kn` is in dual-write scope for new pages
- But page `pl_S1IMEdQOlHbpx0` was created **before** dual-write was enabled
- The page exists in monolith but was never migrated to NCA

**Next Steps:**

- [ ] **Data Fix**: Run migration script to copy `pl_S1IMEdQOlHbpx0` from monolith to NCA
- [ ] **Broader Fix**: Identify all payment pages for dual-write merchants that weren't migrated
- [ ] **Prevention**: Ensure migration scripts run before enabling dual-write for a merchant

---

### 3. payment_page_create_order - Order for Inactive Page

**Error Message:**
```
validation_failure: order cannot be created for payment page which is not active
```

**Occurrences:** 2

| # | Task ID | Request ID | Merchant ID | Payment Page | Timestamp |
|---|---------|------------|-------------|--------------|-----------|
| 1 | `d5r0pqer4dbs716hst10` | `d5r0pqer4dbs716hst0g` | `Ha18e7jHMVjYEb` | `pl_RlDIZYAgTiG4po` | 2026-01-25T12:30:34.234Z |

**Root Cause:**

This is a cascade effect from the activate validation issue (#4). The monolith activate API returned 200 (activating an expired page), but NCA correctly rejected this. When the user then tried to create an order, NCA sees the page as still inactive/expired.

**Monolith Response:** 200 with order created  
**NCA Response:** 400 validation error

**Next Steps:**

- [ ] Depends on resolution of issue #4 (activate behavior)
- [ ] If NCA behavior is correct, this is expected until data sync is fixed

---

## Issues Requiring Investigation (Behavior Differences)

### 4. payment_page_activate - Expired/Already Active Page

**Error Messages:**
```
validation_failure: Cannot activate a payment page that has already expired
validation_failure: Payment link cannot be activated as it is already active
```

**Occurrences:** 4 (2 expired + 2 already active)

**Expired Page Activation:**

| # | Task ID | Payment Page | Merchant ID | Timestamp |
|---|---------|--------------|-------------|-----------|
| 1 | `d5r01jcgr0rs717dpnhg` | `pl_RlDIZYAgTiG4po` | `Ha18e7jHMVjYEb` | 2026-01-25T11:38:54.202Z |

**Already Active Page Activation:**

| # | Task ID | Payment Page | Merchant ID | Timestamp |
|---|---------|--------------|-------------|-----------|
| 1 | `d5s6cmer4dbs716noqc0` | `pl_S7hqb5vBbzMhYn` | `Ha18e7jHMVjYEb` | 2026-01-27T07:16:42.348Z |

**Behavior Difference:**

| Scenario | Monolith | NCA |
|----------|----------|-----|
| Activate expired page | Returns 200 (activates anyway) | Returns 400 (validation error) |
| Activate already active page | Returns 200 (idempotent) | Returns 400 (validation error) |

**Analysis:**

- **NCA behavior is stricter** - it validates that a page cannot be activated if:
  - It has already expired (`expire_by` is in the past)
  - It is already in `active` status

- **Monolith behavior is lenient** - it allows these operations and returns 200

**Decision Required:**

- [ ] Should NCA match monolith's lenient behavior?
- [ ] Or is NCA's stricter validation correct (and monolith should be fixed)?

---

## pages_view HTML Rendering Errors (57 occurrences)

### 5. NCA HTML Errors (5 occurrences) - **Code Fix Required**

**Error:** NCA returns error HTML page saying "Something went wrong"

**Root Cause Chain:**

1. **Cache miss** - Redis returns `nil` for key `nca_live:payment_page:{id}:hosted`
2. **External API timeout** - When fetching merchant details from `api-graphql.razorpay.com`, request is canceled
3. **Fallback fails** - NCA renders error page instead of payment page

**Error Flow:**
```
CACHE_ERROR_GET_KEY_FAILURE (redis: nil)
  → HOSTED_PAGE_ERROR_WHILE_GETTING_PAYLOAD_FROM_CACHE
  → GET_MERCHANT_DETAILS_ERROR_WHILE_FETCHING (context canceled)
  → PAYMENT_PAGE_VIEW_ERROR: "Something went wrong"
```

**Sample Occurrence:**

| # | Task ID | Payment Page | Merchant ID | Timestamp |
|---|---------|--------------|-------------|-----------|
| 1 | `d5rndg65p2gc715e5k70` | `pl_S0roiE1SAtt13O` | `QagXBwUNeuZFow` | 2026-01-26T14:14:25.226Z |

**Analysis:**
- Page `pl_S0roiE1SAtt13O` was not in NCA's Redis cache
- When NCA tried to build the payload from scratch, external API call timed out
- Monolith successfully rendered the page (likely has its own caching/different flow)

**Root Cause Analysis:**

The issue is a **timing/infrastructure problem** in shadow read mode:
1. In `dual_write_shadow_read_no_external`, NCA runs **after** monolith returns
2. Both operations share the same HTTP request context
3. When monolith returns quickly, the context may get canceled
4. NCA's external API calls (e.g., GetMerchantDetails) fail with "context canceled"

**Why This Happens:**
- Pages created **before dual-write** don't have cached payloads in NCA's Redis
- When NCA tries to build the payload from scratch, it needs to call external APIs
- If the request context times out, these API calls fail

**Next Steps:**

- [ ] **Data Migration**: Run cache warming script to populate hosted payloads for existing pages
- [ ] **Code Fix**: Consider using a detached context for shadow read operations to avoid context cancellation
- [ ] **Short-term**: These errors don't affect production (monolith response is served) - they only affect diff metrics

---

### 6. NCA Case-Insensitive ID Lookup (52 occurrences) - **Code Fix Required**

**Error:** Monolith returns 400 "The id provided does not exist", NCA returns 200

**Root Cause:** **NCA performs case-insensitive ID lookup (incorrect)**

**Scenario:**
- Request URL: `/v1/pages/pl_rklskc5wr0cssb/view` (lowercase ID)
- Monolith: Returns 400 - "The id provided does not exist" (correct - case-sensitive)
- NCA: Returns 200 with page for `pl_RKlsKc5wr0cSsB` (incorrect - case-insensitive)

**Sample Occurrence:**

| # | Request ID | Requested ID (lowercase) | Actual ID | Timestamp |
|---|------------|-------------------------|-----------|-----------|
| 1 | `d5rtm81s5lkc713q5rtg` | `pl_rklskc5wr0cssb` | `pl_RKlsKc5wr0cSsB` | 2026-01-26T21:22:41.452Z |

**Analysis:**
- Requests come from Facebook crawler: `facebookexternalhit/1.1`
- Facebook stores/sends lowercase URLs
- NCA performs case-insensitive ID lookup (bug)
- Monolith performs case-sensitive lookup (correct behavior)

**Why Case Sensitivity Matters:**
- Payment page IDs are case-sensitive by design
- Returning data for a different ID (even if only case differs) is incorrect
- Could lead to security/data integrity issues

**Next Steps:**

- [ ] Fix NCA to perform case-sensitive ID lookup in `pages_view` route
- [ ] Verify the database query uses case-sensitive comparison
- [ ] Check if this affects other routes (`payment_page_get_details`, etc.)

---

## Other Excluded Items

### Monolith 500 Errors (2 occurrences)

These are cases where the monolith itself returned 500. NCA correctly reports this as a failure. Not an NCA code issue.

| # | Route | Error | Timestamp |
|---|-------|-------|-----------|
| 1 | payment_page_create_order | `monolith order creation failed with status code: 500` | 2026-01-27T05:40:27.501Z |

---

## Coralogix Query

To fetch status code mismatch logs:

```sql
source logs
| filter $l.applicationname == 'no-code-apps'
| wildfind 'DIFF_CHECKER_SHADOW_STATUS_CODE_MISMATCH'
| wildfind 'dual_write_shadow_read_no_external'
| filter !$d.log.contains('context canceled')
| extract $d.log into $d using regexp(/"route_name":"(?<route_name>[A-Za-z_]+)/)
| extract $d.log into $d using regexp(/"monolith_status_code":(?<monolith_code>\d+)/)
| extract $d.log into $d using regexp(/"shadow_status_code":(?<shadow_code>\d+)/)
| extract $d.log into $d using regexp(/"error_message":"(?<error_message>[^"]+)/)
| join (
   source logs
   | filter $l.applicationname == 'no-code-apps'
   | filter $d.message == 'NEW_NCA_REQUEST_RECEIVED'
 )
 on left=>$d.task_id == right=>$d.task_id into request_log
| choose
   $d.route_name as route_name,
   $d.monolith_code as monolith_code,
   $d.shadow_code as shadow_code,
   $d.error_message as error_message,
   $d.task_id as task_id,
   $d.request_id as request_id,
   $d.log as diff_checker_log,
   request_log.log as request_log
```
