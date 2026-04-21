# Entity Mapping - Payment Pages Decomposition

> **IMPORTANT:** This is a critical reference document for the Payment Pages Decomposition project.

---

## 1. Purpose of this Document

This doc is meant as an accompaniment to the [NoCodeApps Decomp Spec: Payment Pages API Decomposition Tech Spec](./PAYMENT_PAGES_DECOMP.md) which contains mainly the high level details of the migration.

### Overview of the Document

1. **Section 2** - Existing Payment Page Entities in Monolith (detailed schema documentation)
2. **Section 3** - Entity Mapping from Monolith to NCA Service
3. **Section 4** - Diff Checker Configuration (fields ignored during comparison)
4. **Section 5** - Parity Scripts Configuration (fields ignored during parity checks)

> **Note:** Since payment handles and buttons are just different views of payment pages, we'll refer to them as "payment pages" for convenience.

---

## 2. Existing Payment Page Entities

### 2.1. Base Entity (payment_link)

Payment pages in the current form have 3 distinct types: **Pages**, **Buttons**, and **Payment Handle**.

The main entity used internally is called `payment_link` (no relation to the current Payment Links product - this naming was a historical choice when payment pages were thought to be a v2 of payment links).

The high-level details of a page like title, description, contact info, terms and conditions etc. live in this table. Some analytics like `total_amount_paid` are also stored here.

#### Table: payment_links

| Field | Type | Notes |
|-------|------|-------|
| id | char(14) | Primary key |
| merchant_id | char(14) | FK to merchants |
| amount | bigint | Used by early versions (2018/2019), ~500 payments/month |
| currency | char(3) | INR, USD, etc. |
| expire_by | int | Unix timestamp |
| times_payable | bigint | Not currently used (null for all) |
| times_paid | bigint | Not currently used (0 for all) |
| total_amount_paid | bigint | Analytics - incremented after each payment |
| status | varchar(40) | active/inactive |
| status_reason | varchar(40) | deactivated/expired/completed/null |
| short_url | varchar(255) | razorpay.me/... URL |
| user_id | char(14) | Dashboard user who created the page |
| receipt | varchar(40) | null for all since 2018 - can be ignored |
| title | text | Page title |
| description | text | Rich text JSON description |
| notes | text | JSON key-value pairs |
| hosted_template_id | varchar(255) | Custom hosted template (only ~4 pages use this) |
| udf_jsonschema_id | varchar(255) | Used with hosted_template_id |
| support_contact | varchar(255) | Merchant support phone |
| support_email | varchar(255) | Merchant support email |
| terms | text | Terms and conditions |
| type | varchar(30) | Always "payment" - can be ignored |
| created_at | int | Unix timestamp |
| updated_at | int | Unix timestamp |
| deleted_at | int | Soft delete timestamp |
| view_type | varchar(255) | page/button/payment_handle |

---

### 2.2. Payable Line Items

Payable line items are the actual items for which the total amount of an order is calculated.

#### Three Types of Payable Items:

1. **Fixed Amount** - Item with a fixed price
2. **Item with Quantity** - Merchants can specify stock and min/max purchase quantities
3. **Customer Decided Amount** - Usually for donations where payer enters any amount

#### Table: payment_page_items

| Field | Type | Notes |
|-------|------|-------|
| id | char(14) | Primary key (maps to line_items.id in NCA) |
| merchant_id | char(14) | FK to merchants |
| payment_link_id | char(14) | FK to payment_links |
| item_id | char(14) | FK to items table |
| plan_id | char(14) | Used for subscription_buttons - can be ignored |
| mandatory | tinyint(1) | Whether item is required |
| image_url | varchar(512) | Item image |
| stock | bigint | Available stock (maps to line_items_price.available_units) |
| quantity_sold | bigint | Analytics - updated after each payment |
| total_amount_paid | bigint | Analytics |
| min_purchase | bigint | Minimum quantity to purchase |
| max_purchase | bigint | Maximum quantity to purchase |
| min_amount | bigint | Minimum amount (for customer decided) |
| max_amount | bigint | Maximum amount (for customer decided) |
| created_at | int | Unix timestamp |
| updated_at | int | Unix timestamp |
| deleted_at | int | Soft delete timestamp |
| product_config | json | Used for subscription_buttons - can be ignored |

#### Table: items (common monolith table)

| Field | Type | Notes |
|-------|------|-------|
| id | char(14) | Primary key |
| active | tinyint(1) | Only 1 page has active=0 (anomaly) |
| merchant_id | char(14) | FK to merchants |
| name | varchar(512) | Item name (maps to line_items.title) |
| description | varchar(2048) | Item description |
| amount | bigint unsigned | Item amount (maps to line_items_price.amount) |
| currency | char(3) | Currency code |
| type | char(16) | Always "payment_page" |
| unit | varchar(512) | null for all PP entities - can be ignored |
| tax_inclusive | tinyint(1) | null for all PP entities - can be ignored |
| hsn_code | varchar(20) | null for all PP entities - can be ignored |
| sac_code | varchar(20) | null for all PP entities - can be ignored |
| tax_rate | int unsigned | null for all PP entities - can be ignored |
| tax_id | char(14) | null for all PP entities - can be ignored |
| tax_group_id | char(14) | null for all PP entities - can be ignored |
| created_at | int | Unix timestamp |
| updated_at | int | Unix timestamp |
| deleted_at | int | Soft delete timestamp |

#### 2.2.1. Differentiating Payable Line Item Types

| Type | Condition |
|------|-----------|
| **Fixed Amount** | `item.amount` is non-null AND `payment_page_item.min_purchase` is null |
| **Item with Quantity** | `item.amount` is non-null AND `payment_page_item.min_purchase` is non-null (can be 0) |
| **Customer Decided Amount** | `item.amount` is null |

---

### 2.3. Settings Table

The settings table is a key-value store used for various configurations.

#### Table: settings

| Field | Type | Notes |
|-------|------|-------|
| id | char(14) | Primary key |
| entity_type | varchar(100) | e.g., "payment_link" |
| entity_id | char(14) | FK to the entity |
| module | varchar(100) | Feature module name |
| key | varchar(255) | Setting key |
| value | text | Setting value (often JSON) |
| created_at | int | Unix timestamp |
| updated_at | int | Unix timestamp |

#### 2.3.1. Input Line Items (udf_schema)

Stored as JSON against key `udf_schema`:

```json
[
  {
    "name": "email",
    "required": true,
    "title": "Email",
    "type": "string",
    "pattern": "email",
    "settings": { "position": 3 }
  },
  {
    "name": "phone",
    "title": "Phone",
    "required": true,
    "type": "number",
    "pattern": "phone",
    "minLength": "8",
    "options": [],
    "settings": { "position": 4 }
  }
]
```

#### 2.3.2. Receipt Settings

| Key | Type | Description |
|-----|------|-------------|
| enable_custom_serial_number | 1/0 | Manual receipt serial number |
| selected_udf_field | string | Input line item to show on receipt |
| enable_80g_details | 1/0 | Enable 80G tax details |
| image_url_80g | s3 url | Signature image |
| text_80g_12a | string | 80G text |

#### 2.3.3. Payment Page Settings

| Key | Type | Description |
|-----|------|-------------|
| theme | light/dark | Page theme |
| allow_social_share | 0/1 | Enable social sharing |
| custom_domain | string | Custom domain (e.g., mydomain.com) |
| payment_success_redirect_url | url | Redirect after payment |
| payment_success_message | string | Custom success message |
| payment_button_label | string | Pay button text |
| goal_tracker.is_active | 0/1 | Goal tracker enabled |
| enable_receipt | 1/0 | Send invoice receipt (default: 1) |

#### 2.3.4. Facebook and Google Analytics

| Key | Description |
|-----|-------------|
| pp_fb_event_add_to_cart_enabled | FB add to cart tracking |
| pp_fb_event_initiate_payment_enabled | FB initiate payment tracking |
| pp_fb_event_payment_complete_enabled | FB payment complete tracking |
| pp_fb_pixel_tracking_id | FB pixel ID |
| pp_ga_pixel_tracking_id | GA pixel ID |

#### 2.3.5. Partner Webhook Settings

| Key | Description |
|-----|-------------|
| partner_webhook_settings.partner_shiprocket | 0/1 - send webhook to Shiprocket |

#### 2.3.6. Checkout Options

| Key | Description |
|-----|-------------|
| checkout_options.phone | Custom phone label |
| checkout_options.email | Custom email label |

#### 2.3.7. Goal Tracking

**Module: payment_link**

| Key | Description |
|-----|-------------|
| goal_tracker.is_active | Feature flag |
| goal_tracker.tracker_type | supporter_based/amount_based |
| goal_tracker.meta_data.goal_amount | Target amount |
| goal_tracker.meta_data.goal_end_timestamp | End timestamp |
| goal_tracker.meta_data.display_days_left | Show days left |
| goal_tracker.meta_data.display_supporter_count | Show supporter count |
| goal_tracker.meta_data.display_available_units | Show available units |
| goal_tracker.meta_data.display_sold_units | Show sold units |
| goal_tracker.meta_data.available_units | Available units |

**Module: payment_link_computed** (updated after payments)

| Key | Description |
|-----|-------------|
| captured_payments_count | Total captured payments |
| goal_tracker.meta_data.collected_amount | Amount collected |
| goal_tracker.meta_data.sold_units | Units sold |
| goal_tracker.meta_data.supporter_count | Number of supporters |

#### 2.3.8. Payment Handle Settings

| Key | Description |
|-----|-------------|
| default_payment_handle.default_payment_handle_page_id | Payment page ID |
| default_payment_handle.default_payment_handle | Default handle slug (@username) |

#### 2.3.9. Payment Button Settings

| Key | Description |
|-----|-------------|
| payment_button_text | Custom button label |
| payment_button_theme | Color code/name |
| payment_button_template_type | quick-pay/custom/buy-now/donation |

#### 2.3.10. Version

| Key | Description |
|-----|-------------|
| version | v1/v2 - backward compatibility for multi-item pages |

---

### 2.4. NoCode Custom URLs Table

**Table: nocode_custom_urls**

| Field | Type |
|-------|------|
| id | char(14) |
| slug | varchar(128) |
| domain | varchar(256) |
| merchant_id | char(14) |
| product | char(100) |
| product_id | char(14) |
| meta_data | json |

---

## 3. Entity Mapping

### 3.1. Base Entity Mapping (payment_links → nocode)

| payment_links (Monolith) | nocode (NCA) | Notes |
|--------------------------|--------------|-------|
| id | nocode.id | Direct mapping |
| merchant_id | nocode.merchant_id | Direct mapping |
| amount | line_items_price.amount | Legacy field - create single line item for backward compat |
| currency | nocode.currency | Direct mapping |
| expire_by | nocode.expire_by | Direct mapping |
| times_payable | line_items_price.max_units | Legacy field |
| times_paid | analytics.total_payments | Legacy field |
| total_amount_paid | analytics.total_amount | Async update after payments |
| status | nocode.status | active/inactive |
| status_reason | nocode.status_reason | **New column needed** |
| short_url | nocode.short_url | Direct mapping |
| user_id | nocode.meta_data | Stored in meta_data |
| receipt | - | **Can be ignored** (null since 2018) |
| title | nocode.title | Direct mapping |
| description | nocode.description | varchar→text conversion OK |
| notes | nocode.notes | text→json conversion |
| hosted_template_id | configs (payment_page_config.hosted_template_id) | Only ~4 pages use this |
| udf_jsonschema_id | configs (payment_page_config.udf_jsonschema_id) | Used with hosted_template_id |
| support_contact | configs (base_config.support_contact) | Moved to configs |
| support_email | configs (base_config.support_email) | Moved to configs |
| terms | nocode.terms | **New column needed** |
| type | - | **Can be ignored** (always "payment") |
| view_type | nocode.type | Same use-case, name change |
| - | nocode.mode | **New** - test/live differentiation |
| - | nocode.meta_data | **New** - additional metadata |
| - | nocode.expired_at | **New** - when page expired |

---

### 3.2. Payable Line Items Mapping (payment_page_items → line_items)

| payment_page_items (Monolith) | line_items (NCA) | Notes |
|-------------------------------|------------------|-------|
| id | line_items.id | IDs maintained same during migration |
| merchant_id | line_items.merchant_id | Direct mapping |
| payment_link_id | nocode.id | Parent entity |
| item_id | - | **Can be ignored** |
| plan_id | - | **Can be ignored** (subscription_buttons only) |
| mandatory | line_items.mandatory | Direct mapping |
| image_url | images.original | Moved to images table |
| stock | line_items_price.available_units | **New column needed** |
| quantity_sold | analytics.total_units | Moved to analytics |
| total_amount_paid | analytics.total_amount | Moved to analytics |
| min_purchase | line_items_price.min_units | Direct mapping |
| max_purchase | line_items_price.max_units | Direct mapping |
| min_amount | line_items_price.min_amount | Direct mapping |
| max_amount | line_items_price.max_amount | Direct mapping |
| product_config | - | **Can be ignored** (subscription_buttons only) |

---

### 3.3. Items Mapping (items → line_items + line_items_price)

| items (Monolith) | NCA | Notes |
|------------------|-----|-------|
| name | line_items.title | Direct mapping |
| description | line_items.description | Direct mapping |
| amount | line_items_price.amount | Direct mapping |
| currency | line_items_price.currency | Direct mapping |
| active | - | **Can be ignored** (only 1 anomaly) |
| unit | - | **Can be ignored** (null for PP) |
| tax_inclusive | - | **Can be ignored** (invoices only) |
| hsn_code | - | **Can be ignored** |
| sac_code | - | **Can be ignored** |
| tax_rate | - | **Can be ignored** |
| tax_id | - | **Can be ignored** |
| tax_group_id | - | **Can be ignored** |
| type | - | **Can be ignored** (derived from nocode_id) |

---

### 3.4. Settings Mapping

Settings are moved to different tables based on use case:

| Settings Category | NCA Location |
|-------------------|--------------|
| Input Line Items (udf_schema) | configs (key: udf_schema) - stored as JSON |
| Receipt Settings | configs (key: receipt_config) |
| Payment Page Settings | configs (key: base_config) |
| Tracking Settings (FB/GA) | configs (key: tracking_config) |
| Partner Webhook Settings | configs (key: webhook_config) |
| Checkout Options | configs (key: checkout_config) |
| Goal Tracking | **New table: goal_tracker** |
| Analytics (captured_payments_count) | analytics.total_payments |

---

### 3.5. Custom URLs Mapping

| nocode_custom_urls (Monolith) | custom_urls (NCA) | Notes |
|-------------------------------|-------------------|-------|
| id | id | Direct mapping |
| slug | slug | Direct mapping |
| domain | domain | Direct mapping |
| merchant_id | merchant_id | Direct mapping |
| product | product_type | Key name different |
| product_id | product_id | Direct mapping |
| meta_data | meta_data | Direct mapping |

---

## 4. Diff Checker - Ignored Fields

The diff checker in `no-code-apps/internal/monolith_decomp/diffs/diff_checker.go` ignores certain diffs during response comparison.

### 4.1. Diff Ignore Reasons

| Reason | Description | Valid? |
|--------|-------------|--------|
| `DIFF_IGNORE_REASON_NCA_NOT_SUPPORTED` | NCA doesn't support this operation (create APIs for unsupported view types) | **Valid** - NCA only handles page view type |
| `DIFF_IGNORE_REASON_RECORD_NOT_FOUND_AND_NOT_SUPPORTED_VIEW_TYPE` | Record not found + unsupported view type | **Valid** - Expected for buttons/handles not yet migrated |
| `DIFF_IGNORE_REASON_RECORD_NOT_FOUND` | Record not found in NCA (both error cases) | **Valid** - Data not yet migrated |

### 4.2. Fields Skipped in Response Comparison

From `no-code-apps/internal/monolith_decomp/diffs/configs.go`:

#### Global Skip Patterns

| Field/Pattern | Reason for Ignoring |
|---------------|---------------------|
| `/created_at` | Timestamps differ slightly between systems |
| `/updated_at` | Timestamps differ slightly between systems |
| `/item/created_at` | Item timestamps |
| `/order/created_at` | Order timestamps |
| `/settings` | Extra field from NCA |
| `/payment_page_items/\d+/settings` | PPI settings extra field |

#### Hosted Page Response Skip Patterns

| Field/Pattern | Reason for Ignoring | Valid? |
|---------------|---------------------|--------|
| `/keyless_header` | Auth header - internal | **Valid** |
| `/key_id` | API key - internal | **TODO: Verify** |
| `/payment_link/times_paid` | Analytics field - async update | **Valid** |
| `/payment_link/settings/shipping_fee_rule` | Unused setting | **Valid** |
| `/payment_link/settings/one_click_checkout` | Abandoned feature (only 1 test page) | **Valid** |
| `/payment_link/settings/checkout_options/alphabets` | Unused setting | **Valid** |
| `/payment_link/settings/allow_multiple_units` | Unused setting | **Valid** |
| `/cross_origin_enabled` | Derived field for template | **Valid** |
| `/enable_optimized_web_vitals` | Derived field | **Valid** |
| `/environment` | Derived field (prod/dev) | **Valid** |
| `/error_description` | Derived field | **Valid** |
| `/error_description_in_request_params` | Derived field | **Valid** |
| `/is_error_view` | Derived field | **Valid** |
| `/is_preview` | Derived field | **Valid** |
| `/meta_description` | Derived field for SEO | **Valid** |
| `/meta_image` | Derived field for SEO | **Valid** |
| `/theme` | Derived field | **Valid** |
| `/request_params` | Request params passed to template | **Valid** |
| `/merchant/business_registered_address` | Extra field from NCA | **Valid** |

#### Payment Page Details Skip Patterns

| Field/Pattern | Reason | Valid? |
|---------------|--------|--------|
| `/times_paid` | Analytics - async | **Valid** |
| `/amount` | Legacy field, derived | **Valid** |
| `/settings/shipping_fee_rule` | Unused | **Valid** |
| `/settings/one_click_checkout` | Abandoned | **Valid** |
| `/settings/checkout_options/alphabets` | Unused | **Valid** |
| `/settings/allow_multiple_units` | Unused | **Valid** |

#### Normalization Before Comparison

| Field | Reason |
|-------|--------|
| `/settings/udf_schema` | JSON formatting differences |
| `/description` | Rich text JSON formatting |
| `/payment_link/settings/udf_schema` | JSON formatting |
| `/payment_link/description` | Rich text JSON formatting |

---

## 5. Parity Scripts - Ignored Fields

From `/pythonscripts/decomp-scripts/parity/ignore.py`:

### Fields Ignored in Parity Checks

| Field Path | Reason for Ignoring | Valid? |
|------------|---------------------|--------|
| `/captured_payments_count` | Analytics - updated async after payments | **Valid** - Not synced in real-time |
| `/payment_page_items//quantity_sold` | Analytics - updated async | **Valid** - Not synced in real-time |
| `/payment_page_items//total_amount_paid` | Analytics - updated async | **Valid** - Not synced in real-time |
| `/total_amount_paid` | Analytics - updated async | **Valid** - Not synced in real-time |
| `/times_payable` | Legacy field - null for all | **Valid** - Not used |
| `/description` | JSON formatting differences | **Valid** - Normalized separately |
| `/settings/udf_schema` | JSON formatting differences | **Valid** - Normalized separately |

### Analysis

All ignored fields fall into two categories:

1. **Analytics Fields** - Updated asynchronously after payments, not synced in real-time
2. **Formatting Differences** - JSON/text that has equivalent content but different formatting

**These ignores are valid and should remain in place.**

---

## 6. Summary of Fields Safe to Ignore

### Can Be Completely Ignored (Not Migrated)

| Field | Table | Reason |
|-------|-------|--------|
| receipt | payment_links | null since 2018, no usage |
| type | payment_links | Always "payment" |
| plan_id | payment_page_items | subscription_buttons only |
| product_config | payment_page_items | subscription_buttons only |
| unit | items | null for PP entities |
| tax_inclusive | items | invoices only |
| hsn_code | items | invoices only |
| sac_code | items | invoices only |
| tax_rate | items | invoices only |
| tax_id | items | invoices only |
| tax_group_id | items | invoices only |
| one_click_checkout | settings | abandoned feature |

### Needs Migration But Can Have Diff (Analytics)

| Field | Reason |
|-------|--------|
| captured_payments_count | Async update |
| total_amount_paid | Async update |
| quantity_sold | Async update |
| times_paid | Async update |

### Needs New Columns in NCA

| Field | Target Table | New Column |
|-------|--------------|------------|
| status_reason | nocode | status_reason |
| terms | nocode | terms |
| stock | line_items_price | available_units |

---

## Related Documentation

- [PAYMENT_PAGES_DECOMP.md](./PAYMENT_PAGES_DECOMP.md) - High-level decomposition spec
- [code/guide-to-navigate-nca-code.md](./code/guide-to-navigate-nca-code.md) - NCA codebase guide
- [code/monolith-navigation-guide.md](./code/monolith-navigation-guide.md) - Monolith codebase guide
- [data-migration-scripts-guide.md](./data-migration-scripts-guide.md) - Data migration scripts

---

## Code References

- **Diff Checker:** `no-code-apps/internal/monolith_decomp/diffs/diff_checker.go`
- **Comparator Configs:** `no-code-apps/internal/monolith_decomp/diffs/configs.go`
- **Parity Ignore Script:** `pythonscripts/decomp-scripts/parity/ignore.py`
- **Input Line Item Schema (FE):** [Dashboard Code Ref]
