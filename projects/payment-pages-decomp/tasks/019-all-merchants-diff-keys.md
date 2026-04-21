# All Merchants - Response Body Diff Keys (Shadow Mode)

**Created:** 2026-04-16
**Source:** Coralogix diff checker logs (`DIFF_CHECKER_SHADOW_DIFF_PATHS`)
**Total Diffs:** 14,161
**Unique Merchants:** 2,340
**Time Range:** ~48 hours ending 2026-04-15
**Data:** `/page-status-mismatch/diff_keys_categorized.csv`
**Script:** `/page-status-mismatch/categorize_diff_keys.py`

### 2026-04-21 Update

**Organized:** `phase_all_merchants_2026-04-21/` — 24h window
**Total Rows:** ~12,158 | **Total Diffs:** ~20,750 | **Routes:** 12

| Route | Rows | Diffs | Top Issues |
|-------|------|-------|------------|
| payment_page_list | 6,093 | 9,429 | aggregation (2877), empty items (1759), pages_extra_in_nca (1295), pages_missing_in_nca (1006), count (759) |
| pages_view_by_slug | 2,930 | 4,452 | goal_tracker (1022), times_payable (332), merchant_image (302), short_url (153), item_data (147) |
| pages_view | 2,297 | 4,249 | merchant_image (801), item_image_url (439), merchant_name (316), support_mobile (283), fb_pixel (213×3) |
| payment_page_get_details | 658 | 2,308 | aggregation (538+538+367), image_url (246), fb_pixel (53×3), payment_success_settings (79) |
| pages_view_by_slug_post | 77 | 81 | goal_tracker (59), item_description (11) |
| pages_view_post | 56 | 127 | image_url (20), goal_tracker_meta (13), merchant_name (13) |
| Other write routes | 47 | 87 | aggregation dominant |

**New findings vs previous run:**
- `pages_extra_in_nca` (1,295 in list): NCA returns pages monolith doesn't — added as #12
- `payment_success_settings_mismatch` (79 in get_details): redirect_url + message missing in NCA — added as #13
- `merchant/image` (1,103 across routes), `fb_pixel_settings` (798), `merchant/name` case (316) — previously removed from checklist, still occurring

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

| # | Category | Count | % | Severity | Merchants | Status | Notes |
|---|----------|-------|---|----------|-----------|--------|-------|
| 1 | [goal_tracker_mismatch](#1-goal_tracker_mismatch) | 1,119 | 7.9% | MEDIUM | 1 | 🟠 | `tracker_type` value mismatch — datafix needed for 5 pages |
| 2 | [payment_page_items_mismatch](#2-payment_page_items_mismatch) | 966 | 6.8% | HIGH | 79 | 🟠 | 3 root causes: item not linked (387), aggregation drift (365), description missing/different (368) — all datafixes, no code changes |
| 7 | [list_count_plus_empty_items](#7-list_count_plus_empty_items) | 59 | 0.4% | MEDIUM | 15 | ⬜ | `/items` — `[]` vs `null` serialization diff in list |
| 8 | [short_url_mismatch](#8-short_url_mismatch) | 54 | 0.4% | LOW | 1 | ⬜ | Different short URL output |
| 14 | [payment_success_redirect_url](#14-payment_success_redirect_url) | 40 | NEW | MEDIUM | few | ⬜ | `/settings/payment_success_redirect_url` missing in NCA |
| 15 | [payment_success_message](#15-payment_success_message) | 39 | NEW | MEDIUM | few | ⬜ | `/settings/payment_success_message` missing in NCA |
| 22 | [merchant_tnc_link_mismatch](#22-merchant_tnc_link_mismatch) | 16 | NEW | LOW | few | ⬜ | `/merchant/tnc_link` differs |
| 23 | [pp_fb_event_add_to_cart](#23-pp_fb_event_add_to_cart) | 340 | NEW | MEDIUM | many | ⬜ | `/settings/pp_fb_event_add_to_cart_enabled` missing in NCA |
| 24 | [pp_fb_event_initiate_payment](#24-pp_fb_event_initiate_payment) | 340 | NEW | MEDIUM | many | ⬜ | `/settings/pp_fb_event_initiate_payment_enabled` missing in NCA |
| 25 | [pp_fb_event_payment_complete](#25-pp_fb_event_payment_complete) | 340 | NEW | MEDIUM | many | ⬜ | `/settings/pp_fb_event_payment_complete_enabled` missing in NCA |
| 26 | [pp_fb_pixel_tracking_id](#26-pp_fb_pixel_tracking_id) | 14 | NEW | LOW | few | ⬜ | `/settings/pp_fb_pixel_tracking_id` missing in NCA |
| 27 | [enable_g_details_mismatch](#27-enable_g_details_mismatch) | 126 | NEW | MEDIUM | many | ⬜ | `/payment_link/settings/enable_g_details` differs |
| 28 | [checkout_options_mismatch](#28-checkout_options_mismatch) | 29 | NEW | LOW | few | ⬜ | `/payment_link/settings/checkout_options` differs |
| 29 | [enable_custom_serial_number_mismatch](#29-enable_custom_serial_number_mismatch) | 11 | NEW | LOW | few | ⬜ | `/payment_link/settings/enable_custom_serial_number` differs |
| 30 | [enable_receipt_mismatch](#30-enable_receipt_mismatch) | 11 | NEW | LOW | few | ⬜ | `/payment_link/settings/enable_receipt` differs |
| 31 | [theme_mismatch](#31-theme_mismatch) | 5 | NEW | LOW | few | ⬜ | `/settings/theme` differs |
| 35 | [custom_domain_mismatch](#35-custom_domain_mismatch) | 189 | NEW | LOW | few | ⬜ | `/payment_link/settings/custom_domain` (164) + `/settings/custom_domain` (25) |
| 36 | [title_mismatch](#36-title_mismatch) | 35 | NEW | HIGH | few | ⬜ | Page title differs — possible data drift after migration |

---

## Category Details

### 1. goal_tracker_mismatch

**Count:** 1,119 (7.9%) — 1 merchant
**Severity:** MEDIUM
**Diff:** `/payment_link/settings/goal_tracker/tracker_type` — `donation_amount_based` vs `donation_supporter_based`

99% of hits from a single page (`savekeshkali` slug — 1,108/1,119). 5 unique slugs total. Goes both directions (1,109 monolith=amount_based/NCA=supporter_based, 10 the reverse).

**Root Cause:** Value mismatch. NCA's `goal_tracker.type` column has wrong data. Monolith is source of truth until proxy state is `nca_only`. The NCA transformer reads `tracker_type` from `goal_tracker.type` column — the data in that column doesn't match monolith.

**Fix:** Datafix — update `goal_tracker.type` to match monolith's `payment_links.settings->goal_tracker->tracker_type` for affected pages. No code change needed.

**Related sub-paths (same root cause):**
- `/payment_link/settings/goal_tracker/meta_data/available_units` — 356 diffs (missing_field_nca or value mismatch e.g. `"09"` vs `"9"`)
- `/payment_link/settings/goal_tracker/is_active` — 50 diffs
- `/payment_link/settings/goal_tracker/meta_data/goal_end_timestamp_formatted` — 39 diffs
- `/payment_link/settings/goal_tracker` — 29 diffs (whole object missing/different)

**Datafix checklist:**
- [ ] Get page IDs for slugs: `savekeshkali`, `ktnask`, `hadiyaforscholars`, `shopsy`, `pl_QkwTReCBAF80Kv`
- [ ] Query monolith: `SELECT id, JSON_EXTRACT(settings, '$.goal_tracker.tracker_type') FROM payment_links WHERE slug IN (...)`
- [ ] Update NCA: `UPDATE goal_tracker SET type = <monolith_value> WHERE nocode_id = <page_id>`
- [ ] Check `available_units` and `is_active` drift — may need same datafix scope
- [ ] Verify diff is resolved

---

### 2. payment_page_items_mismatch

**Count:** 966 (6.8%) — 79 merchants
**Severity:** HIGH
**Routes:** `pages_view_by_slug`, `pages_view`, `payment_page_get_details`, `payment_page_list`

Item data (amounts, names, active status, IDs) differ between monolith and NCA.

| Subcategory | Count | Notes |
|-------------|-------|-------|
| `amount_mismatch` | 310 | Item amount/unit_amount differs |
| `full_item_data_mismatch` | 217 | ID, active, currency, type, amount all differ |
| `item_fields_1` | 181 | Single item field differs |
| `amount_mismatch_plus_1_other` | 157 | Amount + 1 other field |
| `position_ordering` | 43 | Item position/ordering differs |
| Other | 58 | Various combinations |

**Root Cause Analysis (completed):**

Three distinct root causes identified:

| Subtype | Count | Root Cause | Fix |
|---------|-------|------------|-----|
| `total_amount_paid` / `quantity_sold` differs | ~365 | Aggregation not syncing — payments processed but NCA counters not updated | Datafix: re-compute from payments |
| `full_item_data_mismatch` (NCA item empty) | ~387 | NCA `line_item` not linked to Razorpay `item` — monolith has `item_id`, `active=true`, `amount`; NCA has all null/empty. 100% of cases show NCA values as empty. | Datafix: re-link items or re-migrate |
| `item/description` missing or different | 368 | 340 cases: NCA has `null`, monolith has plain text (migration gap). 28 cases: both have text but values differ (data drift). NOT a format issue. | Datafix: re-migrate item descriptions |
| `image_url` null in NCA | ~55 | Image URL exists in monolith but not migrated to NCA | Datafix |
| `position` / `name` / `mandatory` | ~46 | Various field-level data drift | Datafix |

Top merchants: `RUVtN4AQw2Bd9e` (70), `OEbYkk5e6bHfEN` (51), `K1xMwILVEuNF1L` (20)

**Action items:**
- [ ] Datafix: re-link Razorpay items to NCA line_items for `full_item_data_mismatch` pages (387 entries, highest priority)
- [ ] Datafix: re-compute `total_amount_paid` / `quantity_sold` from payment records
- [ ] Datafix: migrate missing `image_url` values
- [ ] Datafix: re-migrate item descriptions — 340 are null in NCA (migration gap), 28 have different text (data drift)

---

### 3. description_mismatch

**Count:** 711 (5.0%) — 64 unique pages
**Severity:** LOW
**Routes:** `pages_view_by_slug` (666), `pages_view` (45)

NOT a serialization issue — both monolith and NCA return Quill JSON, but the **actual content differs**. The description in NCA DB is different from monolith.

Examples:
- `pl_Sdjg1tqoUZj83F`: different image URL (`sdjfhurwbmpuu9.jpeg` vs `sdk0jakqnuag3a.jpeg`), extra `\n` insert in NCA, same text otherwise
- `ssbdom` (328 hits) and `sigl` (307 hits) account for 89% of diffs — two high-traffic pages with stale descriptions

89% of diffs from 2 pages. 64 unique pages total.

**Root cause:** Description was updated in monolith after NCA migration, or the migration itself transformed the quill JSON slightly (e.g. image re-upload, newline handling). Data mismatch.

**Fix:** Datafix — re-sync descriptions from monolith for the 64 affected pages.

---

### 4. times_payable_mismatch

**Count:** 286 — 51 unique pages
**Severity:** MEDIUM
**Diff:** `/payment_link/times_payable` — monolith has value, NCA has `null`

Examples:
- `CSKFCYelloveMembership`: monolith=`488`, NCA=`null`
- `CSKFCBasicMembership`: monolith=`95`, NCA=`null`

**Root cause:** `times_payable` not migrated to NCA, or updated in monolith post-migration (e.g. via payments incrementing the counter). Datafix needed.

---

### 5. user_data_mismatch

**Count:** 192 (1.4%) — 31 merchants
**Severity:** LOW
**Diff:** `/user/email`, `/user/contact_mobile`, `/user/second_factor_auth`

**Status: 🔵 No Fix Needed** — user data fetched at request time, different auth context.

---

### 6. text_content_mismatch

**Count:** 164 (1.2%) — 16 merchants
**Severity:** LOW
**Diff:** `/notes`, `/terms`, `/items//notes`, `/items//terms`, `/items//description`

**Status: 🔵 No Fix Needed** — minor text content differences, likely serialization or whitespace.

---

### 7. list_count_plus_empty_items

**Count:** 59 (0.4%) — 15 merchants; new data: `/items`=1,759 (monolith=`[]`, NCA=`null`)
**Severity:** LOW
**Diff:** `/items` — list returns `[]` in monolith, `null` in NCA for empty item lists

The `/count` diffs are ES lag (see #16). The `/items` diff is a serialization difference — monolith returns `[]` for empty, NCA returns `null`.

**Fix:** Add `/items` to `SkipEmptyArrayAndObjectPathRegexes` in `paymentPageListResponseComparator`.

---

### 8. short_url_mismatch

**Count:** 54 (0.4%) — 1 merchant
**Severity:** LOW
**Diff:** `/payment_link/short_url` — different short URL generated

**Status: 🔵 No Fix Needed** — URL shortener produces different slugs, both valid.

---

### 9. items_times_paid_mismatch

**Count:** 38 (0.3%) — 2 merchants
**Severity:** MEDIUM
**Diff:** `/items//times_paid` — payment count on items differs

**Investigation checklist:**
- [ ] Check if payments were processed differently in monolith vs NCA
- [ ] Could be stale aggregation from migration

---

### 10. items_status_mismatch

**Count:** 37 (0.3%) — 3 merchants
**Severity:** HIGH
**Diff:** `/items//status`, `/items//status_reason` — individual item status differs

**Investigation checklist:**
- [ ] Check if item-level deactivation/activation bypasses NCA (same kong gap)
- [ ] Check the 3 merchants — are they using item-level status changes via API?

---

### 11. amount_metadata_mismatch

**Count:** 5 (0.0%) — 1 merchant
**Severity:** MEDIUM
**Diff:** `/payment_link/min_amount_value`, `/payment_link/currency_symbol`

**Related paths (new data):**
- `/payment_link/amount` — 55 diffs (not_present: monolith has value, NCA null) — fixed-amount pages
- `/payment_link/amount_formatted` — 55 diffs (same)
- `/items//currency_symbol` — 3 diffs in list

**Investigation checklist:**
- [ ] Check if `min_amount_value` was updated in monolith post-migration
- [ ] Check if `/payment_link/amount` is mapped in NCA transformers for fixed-amount pages
- [ ] Low volume — deprioritize

---

### 14. fb_pixel_settings_mismatch

**Count:** ~798 — routes: `pages_view`, `pages_view_post`, `payment_page_get_details`
**Severity:** MEDIUM
**Diff:** `/payment_link/settings/pp_fb_event_add_to_cart_enabled`, `pp_fb_event_initiate_payment_enabled`, `pp_fb_event_payment_complete_enabled` — monolith has value (e.g. `0`), NCA returns `null`

**Sample:** monolith=`0`, NCA=`null` (type: `missing_field_nca`)

These are Facebook Pixel event tracking flags. Monolith stores them in `payment_links.settings`, NCA is not serializing them in the response transformer.

**Root cause:** NCA transformer for hosted page response doesn't include `pp_fb_event_*` fields from settings. Either not mapped or not migrated.

**Fix options:**
- Skip in diff checker if FB pixel is irrelevant to decomp parity (these are 0/disabled for most pages)
- Or: ensure NCA transformer maps these fields from `nocode.settings`

**Related paths (same category):**
- `/settings/pp_fb_pixel_tracking_id` — 14 diffs
- `/payment_link/settings/pp_fb_pixel_tracking_id` — 5 diffs
- `/payment_link/settings/pp_ga_pixel_tracking_id` — 7 diffs (Google Analytics pixel)

**Investigation checklist:**
- [ ] Check if `pp_fb_event_*` fields are stored in `nocode.settings` column in NCA
- [ ] If not — these merchants have FB pixel enabled; check how many have non-zero values
- [ ] Decide: skip diff or fix transformer

---

### 15. merchant_data_mismatch

**Count:** ~2,200+ diffs — routes: `pages_view`, `pages_view_by_slug`, `pages_view_post`
**Severity:** MEDIUM
**Paths and counts (new data):**

| Path | Count | Notes |
|------|-------|-------|
| `/merchant/image` | 1,103 | 754 missing_field_nca, 32 value diff, 15 not_present |
| `/merchant/name` | 442 | Case mismatch — "Lenka Academy" vs "lenka academy" |
| `/merchant/support_mobile` | 325 | not_present: monolith has value, NCA null |
| `/merchant/support_email` | 147 | value mismatch |
| `/merchant/brand_color` | 189 | different color value |
| `/merchant/tnc_link` | 22 | not_present |
| `/merchant/contact_optional` | 25 | value mismatch |
| `/merchant/email_optional` | 18 | value mismatch |
| `/payment_link/support_contact` + `/items//support_contact` | 13 | not_present |

**Root cause:** Merchant data is fetched differently in NCA vs monolith — NCA may be reading from its own cache/table which is stale or uses different data sources. Image, name, support contact all come from the `merchants` table, which NCA may query independently.

**Investigation checklist:**
- [ ] Check how NCA fetches merchant data in hosted page transformers — does it query `merchants` table directly or use a cached value?
- [ ] For `merchant/name` case diff — check if NCA lowercases the name somewhere
- [ ] For `merchant/image` missing — check NCA's merchant image lookup path

---

### 16. page_list_count_mismatch

**Count:** ~2,100+ diffs — route: `payment_page_list`
**Severity:** LOW (pagination drift) / MEDIUM (`/items//amount`)
**Status: 🔵 No Fix Needed** for `pages_missing_in_nca` and `/count`

**Paths:**

| Path | Count | Status | Notes |
|------|-------|--------|-------|
| `pages_missing_in_nca` | 1,006 | 🔵 ES lag | [+1,-1]/[+2,-2] pagination drift — monolith uses ES, NCA uses DB |
| `/count` | 759 | 🔵 ES lag | Count diff is a direct consequence of the same ES lag |
| `/items//amount` | 382 | ⬜ Investigate | Item `amount` field missing in NCA list response (not_present: monolith=250000, NCA=null) |

**Action item:**
- [ ] `/items//amount`: check NCA list transformer — is the payment page `amount` field mapped for fixed-amount pages?

---

### 17. settings_fields_mismatch

**Count:** ~400 diffs — routes: `pages_view`, `pages_view_by_slug`, `payment_page_get_details`
**Severity:** MEDIUM
**Paths:**

| Path | Count | Notes |
|------|-------|-------|
| `/payment_link/settings/udf_schema` + `/settings/udf_schema` | ~151 | value_mismatch (both show null vs null — likely deep-escape) |
| `/payment_link/settings/enable_g_details` | 126 | extra_field_nca: NCA returns `0`, monolith returns null |
| `/settings/version` | 30 | value diff |
| `/settings/checkout_options/email` | 21 | value diff |
| `/settings/checkout_options/undefined` | 14 | extra/missing field |
| `/payment_link/settings/enable_custom_serial_number` | 11 | missing_field_nca |
| `/payment_link/settings/enable_receipt` | 11 | missing_field_nca |
| `/payment_link/settings/checkout_options` | 11 | diff |
| `/settings/theme` | 5 | value diff |
| `/payment_link/settings/payment_button_label` | 6 | value diff |
| `/payment_link/settings/allow_social_share` | 3 | missing |
| `/payment_link/settings/settings` | 15 | nested settings key |

**Root cause:** Mixed — some fields not mapped in NCA transformer, some are extra fields NCA adds, some are serialization differences (udf_schema deep-escape causing phantom diffs).

**Investigation checklist:**
- [ ] `udf_schema`: both values appear null — likely a deep-escape false diff. Skip in config?
- [ ] `enable_g_details`: NCA adds 0 for this when monolith omits it — extra field in NCA
- [ ] `version`, `checkout_options`, `enable_custom_serial_number`, `enable_receipt`: check if these are in `nocode.settings` and mapped in transformers

---

### 18. org_branding_mismatch

**Count:** ~179 diffs — routes: `pages_view`, `pages_view_by_slug`, `pages_view_by_slug_post`
**Severity:** LOW
**Paths:**

| Path | Count | Notes |
|------|-------|-------|
| `/org/branding/branding_logo` | 87 | monolith has URL, NCA returns empty |
| `/org/branding/show_rzp_logo` | 87 | False vs True |
| `/org/branding/security_branding_logo` | 5 | monolith has URL, NCA empty |

**Root cause:** NCA fetches org branding from a different source or has stale data from migration. `show_rzp_logo=True` in NCA when it should be False suggests wrong default.

**Investigation checklist:**
- [ ] Check how NCA resolves org branding — does it query orgs table or use cached settings?
- [ ] Check if this is a small set of orgs that have custom branding

---

### 19. custom_domain_mismatch

**Count:** ~211 diffs — routes: `pages_view`, `pages_view_by_slug`, `payment_page_get_details`
**Severity:** LOW
**Paths:**
- `/payment_link/settings/custom_domain` — 186 (120 missing_field_nca: monolith=`""`, NCA=`null`)
- `/settings/custom_domain` — 25

**Root cause:** Mostly serialization — monolith stores empty string `""`, NCA returns `null`. A few cases may be actual value diffs.

**Fix:** Add `custom_domain` to `SkipEmptyStringAndNilPathRegexes` in diff checker config — or skip in `SkipPathRegexes` as low value field.

---

### 20. title_mismatch

**Count:** 35 — routes: `payment_page_get_details`, `pages_view_by_slug`
**Severity:** HIGH
**Diff:** `/title` — page title differs between monolith and NCA

**Sample (pages_view_post):** monolith=`"श्री गौ गौरी गोपाल सेवा संस्थान 2026"`, NCA=`"अक्षय तृतीया 2026"` — completely different titles.

**Root cause:** Either:
1. Title was updated in monolith after NCA migration (data drift) — most likely
2. NCA is serving a different page for the same request (routing bug) — less likely but HIGH severity

**Investigation checklist:**
- [ ] Sample 3-5 page IDs with title diff — compare `payment_links.title` vs `nocode.title` directly in DB
- [ ] If data drift: add to datafix scope
- [ ] If routing bug: investigate immediately

---

### 12. pages_extra_in_nca

**Count:** 1,295 requests — route: `payment_page_list`
**Severity:** MEDIUM (title search bug) / LOW (ES lag)
**Status: 🔵 ES lag for +N/-N — ⬜ Title filter bug needs fix**

#### Breakdown (per-request analysis)

| Pattern | Requests | % | Classification |
|---------|----------|---|----------------|
| Both extra AND missing, **equal counts** (e.g. +1/-1, +2/-2) | 741 | 50.5% | 🔵 Pure ES lag — ignore |
| Both extra AND missing, **unequal counts** (e.g. +1/-5) | 14 | 1.0% | 🔵 Mostly ES lag — ignore |
| **Only extra** (NCA has more, monolith has no corresponding missing) | 493 | 33.6% | 🔵 Likely ES lag — new pages not yet indexed in ES |
| **Only missing** (NCA missing pages, monolith has no corresponding extra) | 220 | 15.0% | ⬜ **Title filter bug** — see below |

#### ES lag explanation (+N/-N pattern)
Monolith uses Elasticsearch for its list query; NCA queries the DB directly. For a given pagination window, one page appears in NCA's DB window that ES hasn't indexed yet, and one different page appears in monolith's ES results that falls just outside NCA's window. Both systems are consistent at the dataset level, just not at the pagination boundary.

#### Only-extra (493 requests)
85% are +1 extra page. Most likely new pages recently created that haven't been indexed in ES yet — NCA's DB shows them, ES doesn't. Not a real data issue.

#### Only-missing (220 requests) — title filter bug (replicated)

All 38 requests for the top "only-missing" merchant (`IiRmRinfbseRoG`) use a **`title` query param** — it's a typeahead search ("astra f", "astra fa", "astra fashion show"...). Pages **do exist in NCA DB** (no diffs without the filter). The issue is that **NCA's title filter doesn't work**:

```
title='astra fashion show' → monolith=3 pages, NCA=0 pages (returns nothing)
title='astra solo dance'   → monolith=12 pages, NCA=0 pages
title='astra mehendi'      → monolith=25 pages, NCA=0 pages
title='astra' (broad)      → +7/-7  (ES pagination drift only)
```

**Root cause:** The `title` query parameter is either not passed to NCA's DB query, or the DB matching logic differs from ES (ES supports partial/fuzzy match; NCA may be doing exact match or ignoring it).

**Fix checklist:**
- [ ] Check NCA `payment_page_list` handler — is the `title` param read from request input?
- [ ] Check how the DB query is built for `title` — exact match vs `LIKE '%title%'`
- [ ] ES does case-insensitive partial match; NCA must match the same semantics
- [ ] The other "only-missing" merchants (`IqkJ7RSboivUPw`, `EchXXlLfVXQGON`) likely have the same title-filter pattern — verify

---

### 13. payment_success_settings_mismatch

**Count:** 79 — route: `payment_page_get_details`
**Severity:** MEDIUM
**Diff:** `/settings/payment_success_redirect_url` (40), `/settings/payment_success_message` (39) — present in monolith, `null` in NCA

**Root cause:** These settings fields are either not migrated or not serialized in the NCA `payment_page_get_details` response transformer.

**Investigation checklist:**
- [ ] Check if NCA stores `payment_success_redirect_url` / `payment_success_message` in `nocode.settings` column
- [ ] If stored: check transformer for `payment_page_get_details` — is it mapping these fields?
- [ ] If not stored: datafix needed — migrate from `payment_links.settings`

---

## Route Distribution

| Route | Count | Notes |
|-------|-------|-------|
| payment_page_list | 9,352 | Most diffs from list endpoint shadow reads |
| pages_view_by_slug | 2,738 | Hosted page rendering |
| pages_view | 1,667 | Hosted page rendering |
| payment_page_get_details | 332 | Detail fetches |
| pages_view_by_slug_post | 50 | POST-based page views |
| payment_page_update | 8 | Write path diffs |
| pages_view_post | 8 | POST-based page views |
| payment_page_create | 3 | Create path diffs |
| payment_page_get_details_admin | 2 | Admin detail fetches |
| payment_page_deactivate | 1 | Deactivate diff |

---

## Priority Order

1. **expire_by_mismatch** (4) — Customer-facing risk: premature page expiry
2. **page_list_count_mismatch** (762) — Pages missing/extra between systems
3. **payment_page_items_mismatch** (966) — Item data drift, amounts differ
4. **status_mismatch** (151) — Status out of sync
5. **items_status_mismatch** (37) — Item-level status drift
6. **aggregation_mismatch** (77) — Payment totals differ
7. **goal_tracker_mismatch** (1,119) — Single merchant config issue
8. **times_payable_mismatch** (286) — Single merchant
9. Rest — LOW severity, cosmetic

---

## Known Root Causes

1. **API Kong missing upstream-override** — `prod/api/api.tf` has no upstream-override to NCA for activate, deactivate, list, get, get_details, notify, get_payments. Only dashboard Kong (`api-dashboard/merchant-dashboard.tf`) routes to NCA. Any API-path calls bypass NCA entirely.
2. **NCA independent crons acting on stale data** — `expire_by` cron uses NCA's value which can be out of sync with monolith.
3. **Serialization differences** — `null` vs `[]`, rich text escaping, empty string vs null. Not real data issues.
4. **Migration-time stale data** — Some fields may not have been updated since initial migration.
