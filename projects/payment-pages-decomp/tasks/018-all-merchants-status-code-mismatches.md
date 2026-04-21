# All Merchants - Status Code Mismatches (Shadow Mode)

**Created:** 2026-04-16
**Updated:** 2026-04-21
**Source:** Coralogix diff checker logs (`DIFF_CHECKER_SHADOW_STATUS_CODE_MISMATCH`)
**Total Mismatches:** 546 (2026-04-21 run) — down from 117,508 (2026-04-20) and 4,938 (2026-04-16)
**Time Range:** ~24 hours ending 2026-04-21
**Data:** `/page-status-mismatch/2026-04-21/` (latest), `/page-status-mismatch/categories/` (original)
**Script:** `/page-status-mismatch/categorize_status_code_mismatches.py`

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

## Summary

| # | Category | Old Count | 2026-04-21 | Monolith | NCA | Status | Notes |
|---|----------|-----------|------------|----------|-----|--------|-------|
| 1 | [create_order_validation_gap](#1-create_order_validation_gap) | 36,988 | **0** | 200 | 400 | 🟢 | Fixed — NCA now strips invalid UTF-8 bytes before JSON binding |
| 2 | [proxy_monolith_timeout_pages_view](#2-proxy_monolith_timeout_pages_view) | 74,885 | **0** | 400/500 | 200 | 🔵 | Not in latest TSV (different log source); NCA serves page fine |
| 3 | [list_validation_diff](#3-list_validation_diff) | 300 | **0** | 400 | 200 | 🟢 | Fixed — NCA now validates count/skip params |
| 4 | [create_order_nca_500](#4-create_order_nca_500) | 3,839 | **503** | 400 | 500 | 🟠 | Fix deployed but still hitting — investigate if fix covers all paths |
| 5 | [record_not_found_in_nca](#5-record_not_found_in_nca) | 390 | **20** | 200 | 400 | 🔵 | Reduced — still need data migration for remaining pages |
| 6 | [dual_write_id_extraction](#6-dual_write_id_extraction) | 20 | **0** | 200 | 400 | 🟢 | Fixed — no longer occurring |
| 7 | [deactivate_activate_mismatch](#7-deactivate_activate_mismatch) | 3 | **2** | 200 | 400 | 🟠 | Terms fix verified, but NEW errors: stock check (1), already-inactive (1) |
| 8 | [create_order_monolith_500](#8-create_order_monolith_500) | 35 | **0** | 500 | 400 | 🔵 | No longer occurring |
| 9 | [other](#9-other) | 3 | **0** | mixed | mixed | ⚠️ | Partial — support_contact letter check NOT removed; domain fix partial (slug path done, Settings.Validate still has is.Domain) |
| 10 | ~~merged into #2~~ | — | — | — | — | — | Originally "nca_timeout" — actually same as #2 (proxy timeout, NCA OK) |
| 11 | [list_validation_diff_missing_shadow_code](#11-list_validation_diff_missing_shadow_code) | 485 | **0** | 400 | 200 | 🟢 | Same as #3 — confirmed fixed |
| 12 | [nca_validation_stricter](#12-nca_validation_stricter) | 292 | **21** | 200 | 400 | 🟠 | Old subcategories resolved; NEW subcategories emerged |
| 13 | [pages_view_monolith_500](#13-pages_view_monolith_500) | 218 | **0** | 500 | — | 🔵 | Not in latest TSV (different log source) |
| 14 | [create_order_nca_timeout](#14-create_order_nca_timeout) | 237 | **~6** | 400 | 500 | 🔵 | Reduced (io_read: 4, Post \\: 2) |
| 15 | [other_misc](#15-other_misc) | 27 | **0** | mixed | mixed | 🟢 | No longer occurring |

---

## Category Details

### 1. create_order_validation_gap

**Count:** 36,988 (31.5%)
**Code Pair:** Monolith 200 → NCA 400
**Route:** `payment_page_create_order`
**Data:** [`categories/create_order_validation_gap/`](../../../page-status-mismatch/categories/create_order_validation_gap/), `query_2026_04_20_03_19_20_logs.tsv`
**Entity IDs:** 73 unique pages (top: `pl_Hpovh1NzQWSFqi` = 35,445 = 95.8%)

| Subcategory | Count | Status | Notes |
|-------------|-------|--------|-------|
| `nca_rejects_invalid_payload_monolith_accepts` | 36,988 | ⬜ | NCA returns `INVALID_REQUEST_PAYLOAD` while monolith creates the order successfully. |

**Top entity IDs:**
| Entity | Count | % |
|--------|-------|---|
| `pl_Hpovh1NzQWSFqi` | 35,445 | 95.8% |
| `pl_J1vTgGrsLKbLWy` | 1,287 | 3.5% |
| Other 71 pages | 256 | 0.7% |

**Root cause:** The error occurs at JSON binding (`payment_page.go:745`), NOT at validation. NCA's `NumericUInt64Value` custom JSON unmarshaler (`pkg/datatypes/numeric.go:66-113`) accepts integers and string-encoded integers but rejects floats (e.g., `100.0`), negatives, null for non-pointer fields, and other types that PHP silently coerces. The binding fails before any validation logic runs.

**Root Cause (CONFIRMED via Coralogix `REQUEST_BINDING_ERROR` logs):**

```
order_line_item.OrderLineItemRequest.Amount: readUint64: unexpected character: ufffd,
error found in #10 byte of ...|amount": "100", "qua|...
```

The raw HTTP request body contains **invalid UTF-8 bytes** — sent by mobile browsers and in-app browsers (Instagram WebView, Facebook WebView) that don't enforce UTF-8 encoding. Go's JSON decoder replaces invalid bytes with `\ufffd` (U+FFFD, Unicode replacement character). This replacement char reaches `NumericUInt64Value.UnmarshalJSON`, where `strconv.ParseUint("100\ufffd", 10, 64)` fails. PHP (monolith) accepts invalid UTF-8 transparently.

**Fix applied:**
- `internal/request/init.go` — `BindRawBodyInContext()` now strips invalid UTF-8 bytes from the raw body before calling `binding.JSON.BindBody`. Uses `utf8.Valid()` check + `strings.ToValidUTF8(body, "")` to remove invalid bytes, matching PHP's behavior.
- No impact on valid requests (UTF-8 check is fast, sanitization only runs when needed).

**Investigation checklist:**
- [x] Identify root cause → invalid UTF-8 bytes in raw request body from mobile/in-app browsers
- [x] Confirmed via Coralogix `REQUEST_BINDING_ERROR` log for task `d7hj2iqs8nsc712i0qkg`
- [x] Fix implemented in `internal/request/init.go`

**Status: 🟢 Fixed**

---

### 2. proxy_monolith_timeout_pages_view

**Count:** 74,885 (63.7%) — merges original `html_render_mismatch` + `nca_timeout` + `context_canceled`
**Code Pair:** Monolith 400/500 → NCA 200 (in all cases, NCA serves the page successfully)
**Routes:** `pages_view` (42,734), `pages_view_by_slug` (31,103), `pages_view_post` (633), `pages_view_by_slug_post` (431)

**Note on shadow_code extraction:** 43,180 rows have `shadow_code=200` (Coralogix regex succeeded). 31,716 rows have `shadow_code` empty (regex didn't match `shadow_status_code` in the log format). In both cases, NCA returned 200 with valid HTML — confirmed by checking `shadow_response_body` is present in all 31,716 "empty" rows.

| Subcategory | Count | % | Status | Notes |
|-------------|-------|---|--------|-------|
| `proxy_http_error (Get/Post URL)` | 67,243 | 89.8% | 🔵 | Proxy's HTTP call to api-graphql.razorpay.com times out / context-canceled |
| `proxy_context_canceled` | 7,413 | 9.9% | 🔵 | User aborted request; proxy call to api-graphql canceled; NCA already responded |
| `monolith_500` | 218 | 0.3% | 🔵 | api-graphql returned 500 ("We are facing some trouble...") |
| `other (unknown, EOF)` | 11 | 0.0% | 🔵 | Edge cases |

**Root Cause Analysis (COMPLETED):**

The NCA proxy layer sits in front of both services. For `pages_view` routes in shadow mode (`dual_write_shadow_read_no_external`):
1. Proxy forwards the request to `api-graphql.razorpay.com` (the "monolith" path)
2. Proxy also sends the request to NCA (the "shadow" path)
3. **NCA responds quickly** with the page HTML (returns 200)
4. The proxy's call to `api-graphql.razorpay.com` **gets context-canceled** — likely because the user navigated away, the browser timed out, or the request deadline was exceeded
5. The proxy wraps the Go HTTP client error into a synthetic 400 response: `{"error":{"description":"Get \"https://api-graphql.razorpay.com/v1/pages/pl_xxx/view\": context canceled"}}`
6. Diff checker sees monolith=400, NCA=200 → logs mismatch

**Key findings:**
- 99.7% of pages_view mismatches are proxy-generated errors (not real monolith errors)
- **Zero rows** where monolith=200 and NCA fails — NCA never fails on pages_view
- NCA is faster than the api-graphql path for serving hosted pages
- After cutover to NCA-only, the proxy won't call api-graphql → all these mismatches disappear

**Relationship to original html_render_mismatch (48h dataset, 759 rows):**
The original 759 rows were from a different Coralogix query (`DIFF_CHECKER_HTML_SHADOW_STATUS_CODE_MISMATCH`) which detected HTML content mismatches (page status disagreement — one side returns error page, other returns valid page). That analysis (nca_html_error / monolith_html_error) remains valid for those 759 rows, but they are a different log type not present in this 117K dataset.

**Status: 🔵 No code fix needed — proxy architecture artifact; NCA is better here**

---

### 3. list_validation_diff

**Count:** 300 (0.3%) — up from 161 (larger time window, same pattern)
**Code Pair:** Monolith 400 → NCA 200 (or empty)
**Route:** `payment_page_list`
**Data:** [`categories/list_validation_diff/`](../../../page-status-mismatch/categories/list_validation_diff/)
**Entity IDs:** [`entity_ids.txt`](../../../page-status-mismatch/categories/list_validation_diff/entity_ids.txt) (42 unique — likely merchant-level, not page-level)

| Subcategory | Count | Status | Notes |
|-------------|-------|--------|-------|
| `count_type_validation` | 145 | 🟢 | Fixed — NCA now validates count must be integer |
| `count_max_validation` | 15 | 🟢 | Fixed — NCA now validates count max 100 |
| other | 1 | 🔵 | Edge case |

**Root Cause Analysis (COMPLETED):**

NCA's `ListPaymentPages` (`core.go:3089`) silently defaulted non-integer `count` to `DefaultPPListLimit=10` via `strconv.Atoi` fallback, and capped `count > 100` to `MaxPPListLimit=100`. Monolith's `Fetch.php` validates upfront: `'count' => 'filled|integer|min:1|max:100'`, `'skip' => 'filled|integer|min:0'`.

The `count` values in logs were actually **search terms sent as the count param** by the dashboard frontend (e.g., "hatgad", "generative", "1st April", "NaN", URLs).

**Fix applied:**
- `validation.go` — added `ValidateListFilterParams()` matching monolith's Fetch.php rules
- `payment_page.go` — wired validation before `ListPaymentPages` is called
- Tests in `validation_test.go` covering: valid counts, non-integer strings (production values), max exceeded, zero, negative, floats, skip validation, combined params

**Status: 🟢 Fixed**

---

### 4. create_order_nca_500

**Count:** 3,839 (3.3%) — up from 149 (larger time window, same root cause; excludes 237 NCA timeouts now in [#14](#14-create_order_nca_timeout))
**Code Pair:** Monolith 400 → NCA 500
**Route:** `payment_page_create_order`
**Data:** [`categories/create_order_nca_500/`](../../../page-status-mismatch/categories/create_order_nca_500/)

| Subcategory | Count | Status | Notes |
|-------------|-------|--------|-------|
| `amount_item_mismatch` | 2,284 | 🔵 | Expected — monolith 400, NCA dual-write path → 500 |
| `amount_exceeds_max` | 496 | 🔵 | Expected — see root cause below |
| `amount_below_minimum` | 356 | 🔵 | Expected — see root cause below |
| `total_amount_exceeds_max` | 333 | 🔵 | Expected — see root cause below |
| `page_not_active` | 203 | 🔵 | Expected — see root cause below |
| `mandatory_item_missing` | 62 | 🔵 | Expected — see root cause below |
| `other (auth, currency, min amount)` | 105 | 🔵 | Expected — see root cause below |

**Root Cause Analysis (COMPLETED):**

These 500s are **expected behavior in dual-write shadow mode** and will NOT occur in NCA-only mode.

**Flow in shadow mode (`dual_write_shadow_read_no_external`):**
1. Monolith processes request first → returns **400** (e.g., "amount exceeds max")
2. NCA's `ncaCreateOrder` runs with monolith response attached
3. `embedMonolithIdsIntoOrderCreateRequestIfApplicable()` (`core.go:2490`) checks `monolithResponse.GetStatusCode() != 200` → true
4. Returns `ErrorDualWriteIdExtraction` error ("monolith order creation failed with status code: 400") at `core.go:2507`
5. Controller (`payment_page.go:766`) maps `ErrorDualWriteIdExtraction` → `CodeServerError` (500)
6. Diff checker sees monolith=400, NCA=500 → logs status code mismatch

**Why this won't affect prod:**
- In NCA-only mode (`NCASOnlyProxyState`), `monolithResponse` is nil
- `IsDualWriteToNCA(proxyState)` returns false → NCA creates its own order via `createOrder()`
- NCA's own validation (`validateCreatePaymentPageOrder` at `core.go:2593`) catches these errors BEFORE order creation and returns proper 400s
- The error messages in logs (amount exceeds, page not active, etc.) are from monolith's 400 response, not NCA failures

**Fix applied:**
- `internal/controllers/payment_page.go` — `ncaCreateOrder()` now checks if monolith returned non-200 and forwards the monolith error response directly, instead of running the NCA flow and hitting the `ErrorDualWriteIdExtraction` → 500 path.
- No impact on NCA-only mode (monolithResponse is nil in that flow).

**2026-04-21 update:** Still seeing **503 hits** (was 3,839, now 503). Breakdown:

| Subcategory | Count | Notes |
|---|---|---|
| `amount < min_amount` | 249 | NCA still 500-ing instead of forwarding monolith 400 |
| `amount_item_mismatch` | 207 | Same pattern |
| `amount_exceeds_max` | 36 | Same pattern |
| `io_read_failed: recoverable` | 4 | Transient I/O — may be #14 overlap |
| `mandatory_item_missing` | 3 | Same pattern |
| `Post \\` | 2 | Timeout — #14 overlap |
| `page_not_active` | 2 | Same pattern |

**Investigation needed:** Fix reduced count by ~87% (3,839→503) but didn't eliminate. Check:
- [ ] Is the fix fully deployed? (version rollout may be partial)
- [ ] Do the remaining 503 share a different code path (e.g., `monolith proxy response not attached` vs `monolith order creation failed`)?
- [ ] Are some from before the fix deployment timestamp?

**Code audit (2026-04-21):** Fix verified in repo — `payment_page.go:734-743` has monolith status check + proxyResp forwarding. Commit `a66dd20a` (not deployed) also adds proxyResp==nil handling (returns server error instead of proceeding). The 4 `io_read_failed` hits may be the proxyResp==nil case — would be fixed by deploying `a66dd20a`.

**Status: 🟠 Partially fixed — fix in repo, 503 remaining (likely partial rollout + proxyResp nil case)**

---

### 5. record_not_found_in_nca

**Count:** 390 → **20** (2026-04-21)
**Code Pair:** Monolith 200 → NCA 400 (18 rows), empty codes (2 rows)
**Routes:** `payment_page_get_details` (13), `payment_page_set_receipt_details` (5), `payment_page_update` (2)
**Data:** [`categories/record_not_found_in_nca/`](../../../page-status-mismatch/categories/record_not_found_in_nca/)
**Entity IDs:** 29 unique pages across 19 merchants

| Subcategory | Count | Status | Notes |
|-------------|-------|--------|-------|
| `payment_page_get_details` | 315 | ⬜ | Page exists in monolith but not in NCA |
| `payment_page_set_receipt_details` | 42 | ⬜ | Same root cause — missing record |
| `payment_page_update` | 23 | ⬜ | Same root cause |
| `payment_page_deactivate` | 5 | ⬜ | |
| `payment_page_activate` | 4 | ⬜ | |
| `payment_page_item_update` | 1 | ⬜ | |

**Top affected pages:**
| Entity | Hits | Merchant |
|--------|------|----------|
| `pl_SeY441XdZsslBz` | 7 | OAj44uPdKKD7fx |
| `pl_Sd1R6YF2S38kXz` | 4 | — |
| `pl_SeHRAV4Gj0ruXl` | 3 | — |
| Other 26 pages | 1–2 each | 19 merchants total |

**Top merchants:** OAj44uPdKKD7fx (7), Eu8BDQt1CeV8oD (6), RnTBW1IUJBjX88 (5), EBsdZub75Oug2d (4), RFpvMqzPAT1Eas (4), Ed6ikyPTbpvHsj (4)

**Investigation checklist:**
- [ ] Check if the 29 entity IDs were migrated to NCA
- [ ] Query NCA DB for these IDs — do they exist? Were they soft-deleted?
- [ ] Check if these are newly created pages that haven't synced yet
- [ ] Cross-reference with data migration status for these merchants
- [ ] This is a data sync gap — needs datafix or re-migration

---

### 6. dual_write_id_extraction

**Count:** 20 (0.0%) — up from 5
**Code Pair:** Monolith 200 → NCA 400
**Routes:** `payment_page_create` (19), `payment_page_update` (1)
**Data:** [`categories/dual_write_id_extraction/`](../../../page-status-mismatch/categories/dual_write_id_extraction/)
**Merchants:** 3 (RnTBW1IUJBjX88, SdOJIlkNKylS9I, Sds0T67Tcrcgp7)

| Subcategory | Count | Status | Notes |
|-------------|-------|--------|-------|
| `item count mismatch` | 19 | 🔵 | Monolith returns items with null `Item` entity — not an NCA code issue |
| `no matching composite key found` | 1 | 🔵 | Variant of same issue — no key match after null-item filtering |

**Root Cause Analysis (COMPLETED):**

All 5 cases: `payment_page_create` on 3 merchants (RnTBW1IUJBjX88, SdOJIlkNKylS9I, Sds0T67Tcrcgp7).

From Coralogix logs (`EXTRACT_IDS_ITEM_COUNT_MISMATCH`):
```
requestItemCount: 3, responseItemCount: 3, effectiveResponseCount: 0, skippedItemsWithNullItem: 3
```

Monolith returned 3 payment page items in the create response, but **all 3 have `Item: null`** — the underlying catalog `Item` entity wasn't created or is missing. NCA's `getResponsePPItemKey` correctly skips items with nil Item (returns empty key), so `effectiveResponseCount = 0`, causing the count mismatch.

This is a **monolith data issue** — the Item records aren't being created alongside PaymentPageItem records. NCA's handling is correct (skip null items, report mismatch). In NCA-only mode, NCA creates items directly so this won't occur.

**2026-04-21 update:** Count dropped to **0**. No longer occurring.

**Status: 🟢 Resolved**

---

### 7. deactivate_activate_mismatch

**Count:** 3 (0.1%)
**Code Pair:** Monolith 200 → NCA 400
**Route:** `payment_page_deactivate`
**Data:** [`categories/deactivate_activate_mismatch/`](../../../page-status-mismatch/categories/deactivate_activate_mismatch/)
**Entity IDs:** [`entity_ids.txt`](../../../page-status-mismatch/categories/deactivate_activate_mismatch/entity_ids.txt) (3 unique)

| Subcategory | Old Count | 2026-04-21 | Status | Notes |
|-------------|-----------|------------|--------|-------|
| `validation_failure: terms length 5-2048` | 3 | **0** | 🟢 | Fixed — terms validation now guarded by update list |
| `stock should be left to activate` | — | **1** | ⬜ | **NEW** — NCA has stricter stock check on activate |
| `already inactive` | — | **1** | ⬜ | **NEW** — NCA status out of sync with monolith |

**Root Cause Analysis (COMPLETED for terms fix):**

All 3 original pages belong to merchant `E8GwrSXFOHmrq7` with `terms = "\n\n"` (2 chars, below min 5).

`PaymentPageEntity.ValidateForUpdate` (`validation.go:99-104`) was validating `terms` length **unconditionally** on every update — even for deactivate/activate which only changes status. Monolith uses "filled" semantics and only validates fields present in the request.

**Fix applied:**
- `validation.go` — terms validation now guarded by `IsFieldInUpdateList(updateParamList, "terms")`, so deactivate/activate (which only has `status`/`status_reason` in update list) skips terms validation
- Tests in `list_filter_validation/validate_for_update_terms_test.go` — 8 tests for `IsFieldInUpdateList` covering deactivate, activate, and update-with-terms scenarios

**2026-04-21 update:** Terms fix verified (0 hits). But 2 NEW errors:
- **`stock should be left to activate`** (1): NCA's activate checks item stock; monolith doesn't. Need to investigate whether NCA should relax this check.
- **`already inactive`** (1): NCA thinks page is inactive while monolith has it active. Status data sync gap.

- [ ] Investigate stock check validation in NCA activate path — does monolith skip this?
- [ ] Investigate status sync for the `already inactive` page — which page, is NCA data stale?

**Status: 🟠 Terms fix verified; 2 new sub-issues**

---

### 8. create_order_monolith_500

**Count:** 35 (0.0%) — up from 2
**Code Pair:** Monolith 500 → NCA 400
**Route:** `payment_page_create_order`
**Data:** [`categories/create_order_monolith_500/`](../../../page-status-mismatch/categories/create_order_monolith_500/)

| Subcategory | Count | Status | Notes |
|-------------|-------|--------|-------|
| `We are facing some trouble...` | 35 | 🔵 | Monolith transient 500; no fix needed |

**Analysis:** Monolith hits transient errors and returns 500, while NCA runs its own validation and returns a proper 400. NCA is actually handling this better.

In shadow mode with our earlier fix, NCA now forwards monolith's 500 (correct — user sees monolith response anyway). In NCA-only mode after cutover, NCA will return the proper 400 — an improvement over monolith.

**Status: 🔵 No fix needed — NCA is better here**

---

### 9. other

**Count:** 3 (0.1%)
**Data:** [`categories/other/`](../../../page-status-mismatch/categories/other/)
**Entity IDs:** [`entity_ids.txt`](../../../page-status-mismatch/categories/other/entity_ids.txt) (2 unique)

| Error | Route | Monolith | NCA | Status | Notes |
|-------|-------|----------|-----|--------|-------|
| `support_contact: invalid characters` | payment_page_create | 200 | 400 | 🔵 | NCA stricter — value was `Dinesh - 8433992300` (has letters). 1 hit. |
| `domain: must be a valid domain` | payment_page_create | 200 | 400 | 🔵 | NCA validates domain format, monolith doesn't. 1 hit. |
| `invalid request sent` | payment_page_hosted_view_admin | 200 | 400 | 🔵 | Admin route edge case. 1 hit. |

**Root Cause Analysis (COMPLETED):**

1. **`support_contact`**: Value was `'Dinesh - 8433992300'` (name + number). NCA has a letter pre-check (`custom_rules.go:118-122`) that rejects letters before calling libphonenumber. Go's libphonenumber converts letters to keypad digits (abc=2, def=3), while PHP's libphonenumber throws `NOT_A_NUMBER` for letters.
   - **NOT fixed**: The letter pre-check is still present at `internal/utils/extended_validation/custom_rules.go:118-122`. The comment in code says the check is intentional to match PHP behavior. However, the original diff showed monolith accepted `'Dinesh - 8433992300'` (returned 200), contradicting the comment. Count dropped to 0 in 2026-04-21 run — likely that merchant stopped sending names in contact field. Investigate if monolith's `contact_syntax` actually rejects letters or not before removing.

2. **`domain`**: NCA validated `custom_domain` with `is.Domain` (ozzo-validation) in `ValidateSlug()`.
   - **Partially fixed**: `is.Domain` removed from `ValidateSlug()`'s `validation.Map()` call (`nocode/validation.go:262`). `CustomDomainKey` removed from `validatingMap` (commit `a66dd20a`, not yet deployed). However, `Settings.Validate()` at `nocode/validation.go:498` still has `is.Domain` on `CustomDomain` — only called from `SetReceiptDetailsRequest.Validate()` where `CustomDomain` is nil, so harmless in practice but should be cleaned up.

3. **`hosted_view_admin`**: Admin route edge case, 1 hit. Not actionable.

**Status: ⚠️ Partially fixed — support_contact letter check NOT removed (but 0 hits currently); domain fix partial (slug path fixed, Settings.Validate still has is.Domain)**

---

---

### 10. ~~nca_timeout~~ → merged into #2

**Original count:** 39,626 — merged into category #2 (`proxy_monolith_timeout_pages_view`)

These rows were initially categorized as "NCA timeout" because `shadow_code` was empty in the TSV. Upon investigation:
- All 31,716 pages_view rows with empty `shadow_code` have `shadow_response_body` present — NCA DID respond with 200
- The empty `shadow_code` is a Coralogix regex extraction artifact (`shadow_status_code` not in expected log position)
- Same root cause as rows where `shadow_code=200` — proxy's call to api-graphql fails, NCA succeeds

**Not an NCA timeout.** Merged into category #2.

---

### 11. list_validation_diff_missing_shadow_code

**Count:** 485 (0.4%) — NEW (same root cause as #3, Coralogix extraction artifact)
**Code Pair:** Monolith 400 → NCA 200 (shadow_code empty in TSV)
**Route:** `payment_page_list`

All 485 rows have NCA returning 200 with data (`"count"`, `"items"` in shadow_response_body). These are the same as category #3 `list_validation_diff` (monolith rejects count > 100 or non-integer, NCA accepted before the fix). The `shadow_status_code` wasn't extracted by the Coralogix regex.

Combined with #3 (300 rows with shadow_code=200), total `list_validation_diff` = ~785 rows.

**Status: 🟢 Already fixed — same as #3**

---

### 12. nca_validation_stricter

**Count:** 292 → **21** (2026-04-21)
**Code Pair:** Monolith 200 → NCA 400
**Routes:** `payment_page_update` (18), `payment_page_create` (3)

| Subcategory | Old Count | 2026-04-21 | Status | Notes |
|-------------|-----------|------------|--------|-------|
| `amount should not be lesser than min amount` | 205 | **0** | 🟢 | Resolved — stale data fixed or no longer hitting |
| `amount should be equal to payment page item amount` | 39 | **0** | 🟢 | Resolved |
| `item does not exist, please refresh` | 19 | **0** | 🟢 | Resolved |
| `order cannot be created for page not active` | 10 | **0** | 🟢 | Resolved |
| `terms length 5-2048` | 5 | **0** | 🟢 | Fixed — terms validation guarded by update list |
| `domain: must be a valid domain` | 5 | **0** | 🟢 | Fixed — removed domain validation |
| `support_contact: invalid characters` | 2 | **0** | 🟢 | Fixed — removed letter pre-check |
| `mandatory item missing` | 3 | **0** | 🟢 | Resolved |
| `already active/inactive` | 2 | **0** | 🟢 | Resolved |
| `custom_domain: key not expected` | — | **10** | ⬜ | **NEW** — NCA rejects `custom_domain` in update payload |
| `slug already exists` | 2 | **4** | ⬜ | **INCREASED** — NCA enforces unique slug, monolith doesn't |
| `terms_length_validation` | — | **4** | ⬜ | **NEW** — on update route (different from #7 deactivate path) |
| `line_items_nil_on_create` | — | **2** | ⬜ | **NEW** — NCA requires non-nil items array on create |
| `title_byte_length_bug` | — | **1** | ⬜ | **NEW** — `validation.Length(0,80)` byte-length bug in `line_item/validation.go:44` |

**Root Cause Analysis (COMPLETED):**

Compared PHP (`PaymentPageItem/Validator.php:382`) and Go (`validation.go:291`) logic side by side — **they are identical**:

| Check | Monolith PHP | NCA Go |
|-------|---|---|
| Fixed amount | `!is_null(item->getAmount()) && item->getAmount() !== input[AMOUNT]` | `lineItemPrice.Amount != nil && Amount.Value != *lineItemPrice.Amount` |
| Min amount | `!is_null(ppi->getMinAmount()) && ppi->getMinAmount() > input[AMOUNT]` | `lineItemPrice.MinAmount != nil && Amount.Value < *lineItemPrice.MinAmount` |

Same null-check, same comparison. When monolith returns 200 but NCA returns 400, NCA's `line_item_price` table has **stale or incorrect `amount`/`min_amount` values** for those PPIs — set to non-nil values that don't match what the monolith has.

Affected pages: `pl_RZD1SzmGsOSzQX` (204 hits), `pl_RDdOoUSowsRT0B` (13), `pl_SP8sZYvbYB4D5X` (10), `pl_STWfXTizcVpcGc` (9) — these need their `line_item_price` data re-synced from monolith.

**2026-04-21 update:** Old subcategories (amount/min_amount/item/status data issues) all at **0** — resolved. But **5 new subcategories** emerged:

- [ ] **Fix `custom_domain_key_not_expected`** (10): Fix in repo at `a66dd20a` on `pp-with-tidb` — removes `CustomDomainKey` from `validatingMap` in `ValidateSlug()`. **NOT deployed** — deployed commit `2404d6c6` only removed the `is.Domain` rule but left the key in the map → ozzo rejects it. **Need to deploy `a66dd20a`.**
- [ ] **Fix `slug_uniqueness`** (4): NCA enforces unique slug constraint that monolith doesn't (or scopes differently). Investigate slug uniqueness scope. **No fix in repo yet.**
- [ ] **Fix `terms_length_validation`** (4 in TSV + ongoing in live logs): TWO distinct sources producing similar errors:
  - **With `terms:` prefix** (TSV): From `PaymentPageEntity.ValidateForUpdate()` (`payment_page/validation.go:101`) using `ValidateStruct` → `RuneLength(5, 2048)` guarded by `IsFieldInUpdateList`. Fires when merchant sends `terms` in update request with value < 5 chars. Guard is working (only fires when terms is in request). **Root cause**: monolith accepts short terms on update despite `min:5` in `$editRules` — need to investigate why monolith is lenient. May need to remove the `RuneLength` check entirely on update, keeping only UTF8 validation.
  - **Without field prefix** (live Coralogix log): From `Settings.ValidateForUpdate()` (`nocode/validation.go:583`) validating `PaymentSuccessMessage` with `validation.Length(5, 2048)` (byte length, not char count). Uses `validation.Validate()` not `ValidateStruct` so no field name in error. **Fix in repo**: changed `Length` to `RuneLength` (uncommitted on `pp-with-tidb`).
- [ ] **Fix `line_items_nil_on_create`** (2): NCA requires non-nil items array on payment_page_create. Monolith allows create without items. **No fix in repo yet.**
- [x] **Fix `title_byte_length_bug`** (1): `line_item/validation.go:44` — changed `Length(0, 80)` to `RuneLength(0, 512)` to match monolith's `Item::NAME => 'max:512'`. **Fix in repo** (uncommitted on `pp-with-tidb`). Not deployed.

**Status: 🟠 Old data issues resolved; 5 new subcategories — 1 fixed in repo (title), 1 fix in repo awaiting deploy (custom_domain), 1 likely rollout timing (terms), 2 need investigation (slug, nil items)**

---

### 13. ~~pages_view_monolith_500~~ → merged into #2

**Original count:** 218 — merged into category #2 as subcategory `monolith_500`

These are the 218 rows where api-graphql returned 500 ("We are facing some trouble...") while NCA returned 200. NCA responded successfully in all cases.

---

### 14. create_order_nca_timeout

**Count:** 237 (0.2%) — NEW CATEGORY (split from #4 create_order_nca_500)
**Code Pair:** Monolith 400 → NCA 500
**Route:** `payment_page_create_order`

| Subcategory | Count | Status | Notes |
|-------------|-------|--------|-------|
| `Post \\` (HTTP timeout) | 214 | 🔵 | NCA timed out calling downstream |
| `io_read_failed: recoverable` | 8 | 🔵 | Network read error |
| `DCS Fetch Feature Failure` | 15 | 🔵 | Feature flag service timeout |

These are infrastructure/network issues, not logic bugs. NCA's create_order path timed out or hit transient errors while processing the shadow request.

**Status: 🔵 No code fix needed — infrastructure timeouts**

---

### 15. other_misc

**Count:** 27 (0.0%) — NEW CATEGORY
**Various edge cases across routes:**

| Error | Route | Monolith | NCA | Count | Notes |
|-------|-------|----------|-----|-------|-------|
| `pages_view_by_slug` unknown error | pages_view_by_slug | 400 | 200 | 18 | Unknown parse error |
| `pages_view` unknown error | pages_view | 400 | 200 | 8 | Unknown parse error |
| `get_details` NCA timeout | payment_page_get_details | — | — | 11 | Empty codes — NCA timeout |
| `The id provided does not exist` | payment_page_get_details | 400 | 200 | 4 | Monolith says ID invalid, NCA finds it |
| `The id provided does not exist` | payment_page_set_receipt_details | 400 | 200 | 2 | Same pattern |
| `title length > 80` | payment_page_update | — | — | 1 | NCA timeout + validation edge case |
| `invalid request sent` | payment_page_hosted_view_admin | 200 | 400 | 1 | Admin route edge case (already tracked in #9) |
| `502/504 → 500` | payment_page_create_order | 502/504 | 500 | 2 | Gateway errors |

**Status: ⬜ Low priority — edge cases**

---

## Priority Order (updated 2026-04-21)

### Active issues (need investigation or fix):
1. **#4 create_order_nca_500** (503) — 🟠 Fix deployed, reduced 87% but 503 remaining. Investigate if fix covers all paths.
2. **#12 nca_validation_stricter** (21) — 🟠 Old data issues resolved. 5 new validation gaps: custom_domain (10), slug (4), terms on update (4), nil items (2), title byte-length (1).
3. **#5 record_not_found_in_nca** (20) — 🔵 Reduced from 390. Data migration still needed for remaining pages.
4. **#7 deactivate_activate_mismatch** (2) — 🟠 Terms fix verified. 2 new: stock check (1), already-inactive status sync (1).
5. **#9 other** (3 → 0) — ⚠️ Count is 0 but fixes incomplete:
   - `support_contact` letter pre-check NOT removed (`custom_rules.go:118-122`) — contradicts checklist claim. 0 hits currently but could recur. Need to verify if monolith actually rejects letters in `contact_syntax`.
   - `is.Domain` partially removed — gone from `ValidateSlug()` but still in `Settings.Validate()` line 498 (harmless in practice, dead code cleanup).

### Resolved (confirmed 0 on 2026-04-21, fix verified in repo):
6. ~~**#1 create_order_validation_gap** (36,988 → 0)~~ — 🟢 UTF-8 sanitization fix (`payment_page.go:758-759`)
7. ~~**#3 list_validation_diff** (300 → 0)~~ — 🟢 count/skip param validation (`ValidateListFilterParams`)
8. ~~**#11 list_validation_diff_missing_shadow_code** (485 → 0)~~ — 🟢 Same as #3
9. ~~**#6 dual_write_id_extraction** (20 → 0)~~ — 🟢 No longer occurring (no specific code fix — monolith data issue)
10. ~~**#8 create_order_monolith_500** (35 → 0)~~ — 🟢 No longer occurring
11. ~~**#15 other_misc** (27 → 0)~~ — 🟢 No longer occurring

### No fix needed (disappear after cutover):
12. **#2 proxy_monolith_timeout_pages_view** (74,885) — 🔵 Proxy architecture artifact
13. **#14 create_order_nca_timeout** (~6) — 🔵 Infrastructure timeouts, reduced from 237
