# All Merchants - Response Body Diff Keys (Shadow Mode)

**Created:** 2026-04-16
**Updated:** 2026-04-24
**Source:** Coralogix diff checker logs (`DIFF_CHECKER_SHADOW_DIFF_PATHS`)
**Total Diffs:** 14,161 (2026-04-15) → ~20,750 (2026-04-21) → ~15,000 (2026-04-24)
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

### 2026-04-24 Update

**Source:** `all_merchants_diff_keys_cloned_cloned_logs.tsv`
**Total Rows:** 8,265 | **Routes:** 10

| Route | Rows | Top Issues |
|-------|------|------------|
| payment_page_list | 3,917 | aggregation/total_amount_paid (1,965), pages_extra_in_nca (1,300), pages_missing_in_nca (1,169), count (745), times_paid (192) |
| pages_view_by_slug | 2,063 | merchant_image (637), support_email (345), support_mobile (332), times_payable (227), fb_pixel (97×3), items (123+), status (34+34) |
| pages_view | 1,535 | fb_pixel (300×3), merchant_image (217), times_payable (149), items (111+), enable_g_details (96) |
| payment_page_get_details | 637 | aggregation (466+466+433), fb_pixel (52×3), payment_success (51+49), goal_tracker (26+10) |
| pages_view_post | 50 | fb_pixel (18×3), goal_tracker_meta (17) |
| pages_view_by_slug_post | 36 | merchant_image (22) |
| payment_page_update | 17 | aggregation (15+15+15) |
| payment_page_deactivate | 6 | aggregation (5+5+4) |
| payment_page_activate | 2 | aggregation (2+2+2) |
| payment_page_item_update | 2 | aggregation (2+2) |

**Key changes vs 2026-04-21:**
- **aggregation_mismatch** exploded: 3,593 diffs across **191 merchants** — now the single largest category. Elevated to own priority row.
- **items_status_mismatch** (#10): 37 → **152** diffs, now appearing on `pages_view_by_slug` (70 hits on hosted page route — HIGH severity, users see wrong status)
- **goal_tracker_mismatch** (#1): now **9 merchants** (was 1) — spread widening
- **short_url_mismatch** (#8): 54 → **206**
- **times_payable_mismatch** (#4): 286 → **408**
- **payment_success_settings** (#13): 79 → **100**
- **fb_pixel** (#14): ~798 → **1,421** across 17 merchants
- **org_branding** (#18): 179 → **50** (improving)
- **custom_domain** (#19): 211 → **19** (improving)
- **NEW**: `expire_by` diffs (26) — `pages_view_by_slug` + `pages_view` showing `/payment_link/expire_by` mismatch. Connects to Scze422kvsbnCq expiry bug.
- **NEW**: `merchant/brand_text_color` (70) — not in previous checklist

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

| # | Category | Apr-15 | Apr-21 | Apr-24 | Severity | Merchants | Status | Notes |
|---|----------|--------|--------|--------|----------|-----------|--------|-------|
| AGG | [aggregation_mismatch](#agg-aggregation_mismatch) | ~2,877 | ~2,877 | **3,593** | HIGH | **191** | ⬜ | `total_amount_paid`, `quantity_sold`, `times_paid` not syncing — 191 merchants |
| 1 | [goal_tracker_mismatch](#1-goal_tracker_mismatch) | 1,119 | 1,119 | **448** | MEDIUM | **9** | 🟠 | `tracker_type` mismatch — now 9 merchants (was 1) |
| 2 | [payment_page_items_mismatch](#2-payment_page_items_mismatch) | 966 | 966 | **2,584** | HIGH | 30 | 🟠 | Item data drift — item not linked, description missing |
| 4 | [times_payable_mismatch](#4-times_payable_mismatch) | 286 | 286 | **408** | MEDIUM | 9 | ⬜ | `times_payable` null in NCA |
| 7 | [list_count_plus_empty_items](#7-list_count_plus_empty_items) | 59 | 59 | ~0 | MEDIUM | — | ⬜ | `/items` — `[]` vs `null` |
| 8 | [short_url_mismatch](#8-short_url_mismatch) | 54 | 54 | **206** | LOW | — | ⬜ | Different short URL output — increasing |
| 10 | [items_status_mismatch](#10-items_status_mismatch) | 37 | 37 | **152** | **HIGH** | 5 | ⬜ | Now hitting `pages_view_by_slug` (70 hits) — users see wrong status on hosted pages |
| 13 | [payment_success_settings_mismatch](#13-payment_success_settings_mismatch) | 79 | 79 | **100** | MEDIUM | — | ⬜ | redirect_url (51) + message (49) missing in NCA |
| 14 | [fb_pixel_settings_mismatch](#14-fb_pixel_settings_mismatch) | ~798 | ~798 | **1,421** | MEDIUM | 17 | ⬜ | `pp_fb_event_*` fields missing in NCA — increasing |
| 15 | [merchant_data_mismatch](#15-merchant_data_mismatch) | ~2,200 | ~2,200 | **2,326** | MEDIUM | — | ⬜ | image (877), support_email (420), support_mobile (364) — new: brand_text_color (70) |
| 16 | [page_list_count_mismatch](#16-page_list_count_mismatch) | ~2,100 | ~2,100 | **3,299** | LOW/MED | — | 🔵/⬜ | ES lag (🔵) + items//amount (85, ⬜) |
| 17 | [settings_fields_mismatch](#17-settings_fields_mismatch) | ~400 | ~400 | **158** | MEDIUM | — | ⬜ | enable_g_details (109), theme (9) |
| 18 | [org_branding_mismatch](#18-org_branding_mismatch) | ~179 | ~179 | **50** | LOW | — | ⬜ | Improving |
| 19 | [custom_domain_mismatch](#19-custom_domain_mismatch) | ~211 | ~211 | **19** | LOW | — | ⬜ | Improving — likely serialization fix landed |
| 20 | [title_mismatch](#20-title_mismatch) | 35 | 35 | **42** | HIGH | — | ⬜ | Page title differs — data drift |
| NEW | [expire_by_mismatch](#new-expire_by_mismatch) | — | — | **26** | HIGH | — | ⬜ NEW | `/payment_link/expire_by` diff on hosted page routes — premature expiry risk |
| NEW | [brand_text_color_mismatch](#new-brand_text_color_mismatch) | — | — | **70** | LOW | — | ⬜ NEW | `/merchant/brand_text_color` missing in NCA |

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

**Count:** 37 (Apr-15) → **152 (Apr-24)** — 5 merchants
**Severity:** HIGH ⬆️
**Diff:** `/items//status`, `/items//status_reason` + `/payment_link/status`, `/payment_link/status_reason`

**Apr-24 breakdown:**
| Path | Count | Route | Severity |
|------|-------|-------|----------|
| `/items//status_reason` | 47 | payment_page_list | HIGH |
| `/items//status` | 35 | payment_page_list | HIGH |
| `/payment_link/status` | 35 | pages_view_by_slug | **CRITICAL** |
| `/payment_link/status_reason` | 35 | pages_view_by_slug | **CRITICAL** |

**Critical finding (Apr-24):** Status mismatch now appearing on `pages_view_by_slug` — this means users visiting the hosted payment page are being served the **wrong status** directly from NCA. 70 of 152 hits are on hosted page routes. Connected to the page-level status mismatch investigation (QVVfanTkaqXGGA etc.) — same root cause, now confirmed surfacing on the customer-facing render path.

**Root cause:** Same API Kong gap — `payment_page_deactivate/activate` on `prod/api` Kong has no upstream-override to NCA. Monolith status updated, NCA not synced, hosted page renders from NCA's stale status.

**Investigation checklist:**
- [ ] Check if item-level deactivation/activation bypasses NCA (same kong gap)
- [ ] Check the 5 merchants — are they using status changes via API path (not dashboard)?
- [ ] Correlate with page-status-mismatch analysis — same 4 pages?
- [ ] Fix: add upstream-override to `prod/api` Kong for deactivate/activate routes

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

---

### AGG. aggregation_mismatch

**Count:** ~2,877 (Apr-21) → **3,593 (Apr-24)** — **191 merchants**
**Severity:** HIGH
**Routes:** `payment_page_list`, `payment_page_get_details`, `payment_page_update`, `payment_page_deactivate`, `payment_page_activate`, `payment_page_item_update`

| Path | Count | Notes |
|------|-------|-------|
| `/items//payment_page_items//total_amount_paid` | 1,965 | list route — payment totals not syncing |
| `/payment_page_items//quantity_sold` | 488 | get_details / write routes |
| `/payment_page_items//total_amount_paid` | 488 | get_details / write routes |
| `/total_amount_paid` | 456 | top-level total |
| `/items//times_paid` | 192 | list route — payment count stale |

191 unique merchants affected. This is the largest single category by merchant count and growing. Payments are being processed but NCA's aggregation counters (`total_amount_paid`, `quantity_sold`, `times_paid`) are not being updated.

**Root cause:** NCA aggregation is not receiving payment success events — either event not published to NCA, NCA consumer failing silently, or aggregation computed at query time in monolith but stored/cached in NCA. Needs investigation into NCA's payment event consumer.

**Investigation checklist:**
- [ ] Check NCA's payment event consumer — is it receiving payment captured events?
- [ ] Check if NCA recomputes totals at query time or reads from a stored counter
- [ ] Sample 5 pages with high drift — compare payment records vs NCA's stored total
- [ ] Check if Kafka/SNS payment events are published to NCA's consumer topic

---

### NEW. expire_by_mismatch

**Count:** **26 (Apr-24 NEW)**
**Severity:** HIGH — customer-facing premature expiry risk
**Routes:** `pages_view_by_slug` (3), `pages_view` (4+3), `payment_page_get_details` (1), `payment_page_list` (12)

`/payment_link/expire_by` and `/payment_link/expire_by_formatted` differ between monolith and NCA. Connected to the confirmed incident with `Scze422kvsbnCq` — NCA had a 48-hour shorter `expire_by`, its cron expired the page prematurely.

**Root cause:** `expire_by` update via API path (monolith only) doesn't sync to NCA. NCA's independent expiry cron then acts on stale data.

**Investigation checklist:**
- [ ] Identify the 26 pages with expire_by drift — compare monolith vs NCA values
- [ ] Check which direction: monolith longer or NCA longer?
- [ ] Any of these at risk of imminent premature NCA expiry?
- [ ] Fix: ensure expire_by updates go through NCA dual-write

---

### NEW. brand_text_color_mismatch

**Count:** **70 (Apr-24 NEW)**
**Severity:** LOW
**Routes:** `pages_view_by_slug` (46), `pages_view` (24)
**Diff:** `/merchant/brand_text_color` — present in monolith, missing/different in NCA

Subcategory of `merchant_data_mismatch` (#15). NCA's merchant data fetch doesn't include `brand_text_color`.

---

## Priority Order

### Apr-24 Priority

1. **aggregation_mismatch** (3,593 diffs, **191 merchants**) — Payment totals not syncing; largest category by merchant count
2. **items_status_mismatch** (152, now on hosted page route) — Users seeing wrong page status on `pages_view_by_slug` — CRITICAL customer-facing
3. **expire_by_mismatch** (26 NEW) — Premature page expiry risk; confirmed causing real incidents
4. **payment_page_items_mismatch** (2,584) — Item data drift
5. **fb_pixel_settings_mismatch** (1,421, 17 merchants) — FB pixel fields missing in NCA
6. **merchant_data_mismatch** (2,326) — image/support_email/support_mobile stale in NCA
7. **goal_tracker_mismatch** (448, now 9 merchants) — Spreading beyond 1 merchant; datafix needed
8. **times_payable_mismatch** (408) — Increasing trend
9. **title_mismatch** (42) — High severity if routing bug; low if data drift
10. **payment_success_settings** (100), **short_url** (206) — Medium/low
11. Rest — cosmetic or no-fix-needed

---

## Known Root Causes

1. **API Kong missing upstream-override** — `prod/api/api.tf` has no upstream-override to NCA for activate, deactivate, list, get, get_details, notify, get_payments. Only dashboard Kong (`api-dashboard/merchant-dashboard.tf`) routes to NCA. Any API-path calls bypass NCA entirely.
2. **NCA independent crons acting on stale data** — `expire_by` cron uses NCA's value which can be out of sync with monolith.
3. **Serialization differences** — `null` vs `[]`, rich text escaping, empty string vs null. Not real data issues.
4. **Migration-time stale data** — Some fields may not have been updated since initial migration.
