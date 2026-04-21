# Ignored Fields Analysis - Payment Pages APIs

**Purpose:** Comprehensive analysis of all fields being ignored during response comparison in NCA diff checker and parity scripts.

**Sources:**
- NCA Diff Checker: `no-code-apps/internal/monolith_decomp/diffs/configs.go`
- Parity Ignore Script: `pythonscripts/decomp-scripts/parity/ignore.py`
- Entity Mapping: `/docs/projects/payment-pages-decomp/entity-mapping.md`

---

## Status Legend

| Status | Meaning |
|--------|---------|
| ✅ **Valid** | Correctly ignored - safe to ignore |
| ⚠️ **Verify** | Needs verification - may be incorrectly ignored |
| ❌ **Remove** | Should NOT be ignored - needs fix |
| 🔍 **Review** | Needs manual review by user |

---

## 1. Global Skip Patterns (All Routes)

These patterns are applied to most response comparisons.

| # | Field Pattern | Skip Reason | Status | Justification |
|---|---------------|-------------|--------|---------------|
| 1 | `/created_at` | Timestamp | ✅ **Valid** | Timestamps may differ by milliseconds between systems. NCA generates its own timestamp during creation. |
| 2 | `/updated_at` | Timestamp | ✅ **Valid** | Same as above - timestamps can differ due to processing time. |
| 3 | `/item/created_at` | Item timestamp | ⚠️ **Verify** | Should match if migrated correctly. Diffs show 1-second differences - likely migration issue. See diff logs. |
| 4 | `/order/created_at` | Order timestamp | ✅ **Valid** | Order is created fresh by NCA - timestamp will naturally differ. |
| 5 | `/settings` | Extra NCA field | 🔍 **Review** | NCA returns extra `settings` field at root level. Verify if frontend handles this. |
| 6 | `/payment_page_items/\d+/settings` | PPI settings | 🔍 **Review** | NCA returns position info. May be intentional but verify frontend compatibility. |

---

## 2. Hosted Page Response (`pages_view`, `pages_view_post`)

**API:** `GET /v1/pages/{id}/view`, `POST /v1/pages/{id}/view`

### 2.1 Auth/Internal Fields

| # | Field | Skip Reason | Status | Justification |
|---|-------|-------------|--------|---------------|
| 7 | `/keyless_header` | Auth header | ✅ **Valid** | Internal auth header, differs per environment. Not visible to end users. |
| 8 | `/key_id` | API key | ⚠️ **Verify** | Code has `TODO: make sure it's actually ignorable`. **Needs verification** - could expose different API keys. |

### 2.2 Analytics Fields

| # | Field | Skip Reason | Status | Justification |
|---|-------|-------------|--------|---------------|
| 9 | `/payment_link/times_paid` | Analytics | ✅ **Valid** | Updated async after payments. NCA analytics may lag behind monolith. |

### 2.3 Unused/Abandoned Settings

| # | Field | Skip Reason | Status | Justification |
|---|-------|-------------|--------|---------------|
| 10 | `/payment_link/settings/shipping_fee_rule` | Unused | ✅ **Valid** | Feature was planned but never implemented. No pages use this. |
| 11 | `/payment_link/settings/one_click_checkout` | Abandoned | ✅ **Valid** | Only 1 test page has this. Feature was abandoned. |
| 12 | `/payment_link/settings/checkout_options/alphabets` | Unused | ✅ **Valid** | Dead setting - no frontend usage found. |
| 13 | `/payment_link/settings/allow_multiple_units` | Unused | ✅ **Valid** | Dead setting - no frontend usage. |

### 2.4 Template-Derived Fields

| # | Field | Skip Reason | Status | Justification |
|---|-------|-------------|--------|---------------|
| 14 | `/cross_origin_enabled` | Derived | ✅ **Valid** | Computed from view_preferences, not stored. |
| 15 | `/enable_optimized_web_vitals` | Derived | ✅ **Valid** | Computed from merchant/org settings. |
| 16 | `/environment` | Derived | ✅ **Valid** | "production" vs "development" - always differs per env. |
| 17 | `/error_description` | Derived | ✅ **Valid** | Error rendering field, only present on error pages. |
| 18 | `/error_description_in_request_params` | Derived | ✅ **Valid** | Request params for error display. |
| 19 | `/is_error_view` | Derived | ✅ **Valid** | Boolean flag for error state. |
| 20 | `/is_preview` | Derived | ✅ **Valid** | Preview mode flag from request params. |
| 21 | `/meta_description` | Derived | ✅ **Valid** | SEO field computed from description. |
| 22 | `/meta_image` | Derived | ✅ **Valid** | SEO field computed from images. |
| 23 | `/theme` | Derived | ✅ **Valid** | Derived from settings for template use. |
| 24 | `/request_params` | Derived | ✅ **Valid** | Request context passed to template. |

### 2.5 Extra NCA Fields

| # | Field | Skip Reason | Status | Justification |
|---|-------|-------------|--------|---------------|
| 25 | `/merchant/business_registered_address` | Extra NCA field | 🔍 **Review** | NCA fetches additional merchant data. Verify if frontend uses this. |

### 2.6 Normalized Before Comparison

| # | Field | Normalization Reason | Status | Justification |
|---|-------|---------------------|--------|---------------|
| 26 | `/payment_link/settings/udf_schema` | JSON formatting | ✅ **Valid** | Same data, different JSON serialization order. Normalized to compare content. |
| 27 | `/payment_link/description` | Rich text formatting | ✅ **Valid** | Quill.js JSON can have different formatting. Content is same. |

---

## 3. Payment Page Create/Update Response

**API:** `POST /v1/payment_pages`, `PUT /v1/payment_pages/{id}`

| # | Field | Skip Reason | Status | Justification |
|---|-------|-------------|--------|---------------|
| 28 | `/created_at` | Timestamp | ✅ **Valid** | (inherited from global) |
| 29 | `/updated_at` | Timestamp | ✅ **Valid** | (inherited from global) |
| 30 | `/payment_page_items/\d+/settings` | Extra field | 🔍 **Review** | NCA returns position settings. |
| 31 | `/description` | Normalized | ✅ **Valid** | JSON formatting difference. |

---

## 4. Payment Page Details Response (`payment_page_get_details`)

**API:** `GET /v1/payment_pages/{id}/details`

| # | Field | Skip Reason | Status | Justification |
|---|-------|-------------|--------|---------------|
| 32 | `/times_paid` | Analytics | ✅ **Valid** | Async update after payments. |
| 33 | `/amount` | Legacy field | ⚠️ **Verify** | Legacy field from 2018-2019. Should be null for most pages. **Verify if any pages still use this.** |
| 34 | `/settings/shipping_fee_rule` | Unused | ✅ **Valid** | (same as #10) |
| 35 | `/settings/one_click_checkout` | Abandoned | ✅ **Valid** | (same as #11) |
| 36 | `/settings/checkout_options/alphabets` | Unused | ✅ **Valid** | (same as #12) |
| 37 | `/settings/allow_multiple_units` | Unused | ✅ **Valid** | (same as #13) |

### 4.1 Empty String vs Null Normalization

| # | Field | Normalization Reason | Status | Justification |
|---|-------|---------------------|--------|---------------|
| 38 | `/payment_page_items/\d+/item/description` | "" vs null | ✅ **Valid** | Monolith returns "", NCA returns null. Functionally equivalent. |
| 39 | `/settings/selected_udf_field` | "" vs null | ✅ **Valid** | Same - empty string vs null normalization. |

---

## 5. Payment Page List Response (`payment_page_list`)

**API:** `GET /v1/payment_pages`

| # | Field | Skip Reason | Status | Justification |
|---|-------|-------------|--------|---------------|
| 40 | `/items/\d+/created_at` | Timestamp | ✅ **Valid** | Item timestamps in list response. |
| 41 | `/items/\d+/updated_at` | Timestamp | ✅ **Valid** | Item timestamps in list response. |
| 42 | `/items/\d+/payment_page_items/\d+/settings` | Extra field | 🔍 **Review** | Settings in list response items. |

---

## 6. Payment Page Item Update Response

**API:** `PUT /v1/payment_pages/{id}/items/{item_id}`

| # | Field | Skip Reason | Status | Justification |
|---|-------|-------------|--------|---------------|
| 43 | `/item/created_at` | Item timestamp | ⚠️ **Verify** | Item timestamps should match if not being recreated. |
| 44 | `/settings` | Extra field | 🔍 **Review** | NCA returns settings, monolith doesn't. |

---

## 7. Payment Page Create Order Response

**API:** `POST /v1/payment_pages/{id}/order`

| # | Field | Skip Reason | Status | Justification |
|---|-------|-------------|--------|---------------|
| 45 | `/order/created_at` | Order timestamp | ✅ **Valid** | Fresh order - different timestamp expected. |

---

## 8. Parity Script Ignores

These are additional ignores applied by the parity checking scripts (`parity/ignore.py`).

| # | Field | Skip Reason | Status | Justification |
|---|-------|-------------|--------|---------------|
| 46 | `/captured_payments_count` | Analytics | ✅ **Valid** | Updated async after payments. Not synced in real-time between systems. |
| 47 | `/payment_page_items//quantity_sold` | Analytics | ✅ **Valid** | Payment aggregation data. Updated after each payment async. |
| 48 | `/payment_page_items//total_amount_paid` | Analytics | ✅ **Valid** | Payment aggregation data. Updated after each payment async. |
| 49 | `/total_amount_paid` | Analytics | ✅ **Valid** | Page-level payment total. Updated async. |
| 50 | `/times_payable` | Legacy unused | ✅ **Valid** | null for ALL payment pages. Legacy field never used. |
| 51 | `/description` | JSON formatting | ✅ **Valid** | Rich text JSON formatting differences. Content is equivalent. |
| 52 | `/settings/udf_schema` | JSON formatting | ✅ **Valid** | JSON serialization order differences. Content is equivalent. |

---

## Summary

### Counts by Status

| Status | Count | Action Required |
|--------|-------|-----------------|
| ✅ **Valid** | 40 | None - keep ignoring |
| ⚠️ **Verify** | 4 | Check if ignore is correct |
| 🔍 **Review** | 8 | Manual review needed |
| ❌ **Remove** | 0 | N/A |

### Items Needing Attention

#### ⚠️ Needs Verification (4 items)

| # | Field | Concern |
|---|-------|---------|
| 3 | `/item/created_at` | Diffs show 1-second differences. May indicate migration timestamp issue. |
| 8 | `/key_id` | Code has TODO comment. Verify if different API keys could be exposed. |
| 33 | `/amount` | Legacy field. Verify if any active pages use this. |
| 43 | `/item/created_at` (item update) | Should match for existing items. |

#### 🔍 Manual Review Needed (8 items)

| # | Field | Review Question |
|---|-------|-----------------|
| 5 | `/settings` | Does frontend handle extra settings field at root? |
| 6 | `/payment_page_items/\d+/settings` | Is position info causing any frontend issues? |
| 25 | `/merchant/business_registered_address` | Is this extra field used by frontend? |
| 30 | `/payment_page_items/\d+/settings` (create/update) | Same as #6 |
| 42 | `/items/\d+/payment_page_items/\d+/settings` | Same as #6 for list API |
| 44 | `/settings` (item update) | NCA returns settings, monolith doesn't. |

---

## Recommendations

### Immediate Actions

1. **Verify `/key_id` (#8):** Check if this could expose different API credentials between environments.

2. **Investigate `/item/created_at` (#3, #43):** The 1-second timestamp differences suggest a migration or rounding issue. Check migration script.

3. **Verify `/amount` (#33):** Query TiDB to check if any active pages have non-null `amount` field.

### Documentation Actions

1. **Document `/settings` behavior:** If intentional, document that NCA returns additional settings fields for frontend use.

2. **Update entity-mapping.md:** Mark `amount` as definitively ignored if verified.

---

## Related Documentation

- [Entity Mapping](/docs/projects/payment-pages-decomp/entity-mapping.md)
- [Response Body Diffs Task](/docs/projects/payment-pages-decomp/tasks/response-body-diffs.md)
- [PAYMENT_PAGES_DECOMP.md](/docs/projects/payment-pages-decomp/PAYMENT_PAGES_DECOMP.md)
