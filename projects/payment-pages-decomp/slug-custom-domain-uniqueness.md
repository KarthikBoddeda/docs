# Slug + Custom Domain Uniqueness (Payment Pages)

## Monolith vs NCA: Why a page can have short_url in both but only NCA has a custom_url row

### Two different tables

| System   | Table               | Column for product type |
|----------|---------------------|--------------------------|
| Monolith | `nocode_custom_urls` | `product`                |
| NCA      | `custom_urls`        | `product_type`           |

Both store **(slug, domain)** (+ product id) so that `https://rzp.io/rzp/<slug>` and hosted URLs can resolve to the right page.

### How the short URL (Gimli) is set

- **Monolith** (`api/app/Models/PaymentLink/Core.php`):
  - On create: `createAndSetShortUrl()` calls Elfin/Gimli to shorten the URL (with optional alias/slug). The result is stored in `payment_links.short_url` (e.g. `https://rzp.io/rzp/llj-ga-v1`).
  - In the **same** create flow, `createCustomUrl()` is called (LIVE mode, slug present, view_type PAGE/PAYMENT_HANDLE) and **upserts** into `nocode_custom_urls` (slug, domain from hosted URL, product_id, etc.).
  - Slug resolution: `ElfinWrapper.expandAndGetMetadata()` first looks up **nocode_custom_urls** by (slug, domain); if not found, falls back to **Gimli expand**.

- **NCA** (`no-code-apps/internal/modules/payment_page/core.go`):
  - On create/update: `generateShortUrl()` calls Gimli with alias = slug and stores the returned URL in the nocode entity’s `short_url`.
  - Separately, `upsertSlugInCustomUrlModule()` **upserts** into NCA’s `custom_urls` (slug, domain from `GetHostedUrlWithSlug` → `StripURLParts`, product_id, product_type).

So in both systems, **Gimli** is used to produce the short URL; the **custom_url / nocode_custom_url** table is an application-level mapping (slug + domain → product_id) used for resolution and uniqueness.

### Why monolith can have no `nocode_custom_urls` row for a given page

Even when `payment_links.short_url` is set (e.g. `https://rzp.io/rzp/llj-ga-v1`) and the same slug exists in NCA’s `custom_urls`, monolith’s `nocode_custom_urls` may have **no** row for that slug/domain. Common reasons:

1. **Page was created in monolith before the custom-URL flow existed** – only `payment_links.short_url` was set (via Gimli); `createCustomUrl` didn’t exist or wasn’t called, so nothing was written to `nocode_custom_urls`.
2. **Test mode** – In `createAndSetShortUrl()`, in test mode the slug is forced to `null`, so no custom slug is stored and `createCustomUrl` may not run for the slug path.
3. **createCustomUrl failed and was swallowed** – `createCustomUrl()` is in a try/catch that only traces and does not rethrow; so `short_url` can be set but the nocode_custom_url upsert can fail (e.g. duplicate, validation) and monolith will have no row.
4. **Page was created/updated via NCA** – NCA writes to `custom_urls` and dual-writes to monolith. If the dual-write payload did not include `nocode_custom_url` (e.g. old code path, or payload built when CustomUrl was nil), monolith would not get the row even though NCA has it.

So it is **normal** for some legacy or edge-case pages to have `payment_links.short_url` set and the slug present in NCA’s `custom_urls`, but **no** corresponding row in monolith’s `nocode_custom_urls`.

### Why “duplicate slug” on data migration for such a page

For a page like `QAcfLXkTr4Ei3o`:

- **Monolith**: `payment_links` has the row with `short_url = https://rzp.io/rzp/llj-ga-v1`; `nocode_custom_urls` has **no** row for slug `llj-ga-v1` (for the reason above).
- **NCA**: The page already exists in `nocode` and **already has** a `custom_urls` row (e.g. slug `llj-ga-v1`, domain `pages.razorpay.com`, `product_id` = `QAcfLXkTr4Ei3o`) from a previous NCA create/update that called `upsertSlugInCustomUrlModule`.

When a **data migration** runs for this page:

1. It typically reads from monolith (payment_links + optionally nocode_custom_urls).
2. For custom URL it may derive (slug, domain) from `short_url` or from monolith’s `nocode_custom_urls` (which is empty here).
3. It then tries to **insert** a `custom_urls` row in NCA for this page with the same (slug, domain, product_type).

Because NCA **already** has that (slug, domain, product_type) for this product_id, the migration either:

- Hits an **application-level** “slug already exists” (if the migration path uses the same validation as create/update), or  
- Hits a **DB duplicate key** if the DB has a unique constraint on (slug, domain, product_type).

So the duplicate slug error is expected when the page already exists in NCA with that slug and the migration does a plain insert instead of an upsert or “skip if already exists”.

**Migration fix:** For custom_urls, either (a) **skip** inserting a custom_url row when a row for this `product_id` (and optionally same slug/domain) already exists in NCA, or (b) use an **upsert** (by product_id or by slug+domain+product_type) instead of insert-only.

---

## When does a slug + custom domain insert/update fail?

Uniqueness for **(slug, domain, product_type)** is enforced **only at application level**. There is **no DB-level unique constraint** on the `custom_urls` table in the no-code-apps-datafixes codebase.

---

## Application-level checks

### 1. Where it runs

- **Payment page create/update**: `internal/modules/payment_page/validation.go` calls `n.ValidateSlug()`.
- **Nocode (payment page) slug validation**: `internal/modules/nocode/validation.go` → `ValidateSlug()` runs only when **custom domain is set** (and in live mode). It then calls `custom_url.ValidateUniqueSlugDomain(hostedUrlSuffix, entityId, merchantId, productType)`.
- **Custom URL uniqueness**: `internal/modules/custom_url/validation.go` → `ValidateUniqueSlugDomain` uses `GetUniqueEntity(ctx, slug, domain, productType)` to see if a row already exists.

### 2. How uniqueness is determined

- **Key**: `(slug, domain, product_type)`.
- **Domain**: For custom-domain pages, `hostedUrlSuffix = "https://" + CustomDomain + "/stores"`; `domain` is derived from that (e.g. via `utils.StripURLParts`), so it is effectively the **custom domain**.
- **Lookup**: `custom_url.repo.GetUniqueEntity()` does an **Unscoped** query (includes soft-deleted rows) on `custom_urls` with `WHERE slug = ? AND domain = ? AND product_type = ?`.

### 3. Cases when insert/update fails (validation error)

| Case | Result |
|------|--------|
| **Create**: Another **non-deleted** row already exists with same (slug, domain, product_type) | Fail with **"slug already exists"** (`SlugExistsErrorMessage`). |
| **Create**: Same (slug, domain) exists but row is **deleted** | Allowed (reuse of slug+domain). |
| **Update**: Same (slug, domain) exists for a **different product_id** (different page) and that row is non-deleted | Fail with **"slug already exists"** (via `IntegrityCheck`). |
| **Update**: Same (slug, domain) exists for the **same product_id** (same page) | Allowed (no change). |
| **Update**: Same (slug, domain) exists for a different product_id but that row is **deleted** | Allowed (IntegrityCheck allows when the existing row is deleted). |

Additional validation (not uniqueness):

- **Custom domain set but slug missing/empty**: Fail with **"slug required for page with custom domain."**
- **Slug format/length**: When slug is explicitly provided, length 4–30 and format rules apply; blacklisted slugs can also cause failure.

### 4. Code references

- Uniqueness rule: `internal/modules/custom_url/validation.go` → `ValidateUniqueSlugDomain`, `IntegrityCheck`, `DetermineShoudCreate`.
- DB read: `internal/modules/custom_url/repo.go` → `GetUniqueEntity(ctx, slug, domain, productType)`.
- Error message: `internal/modules/custom_url/constants.go` → `SlugExistsErrorMessage = "slug already exists"`.

---

## DB-level unique constraint?

- **No.** The `custom_url.Entity` model has no GORM unique index on (slug, domain, product_type), and there are no migrations in this repo that add a unique constraint on `custom_urls`.
- So a duplicate (slug, domain, product_type) could theoretically be inserted by another client or script that bypasses the app; the DB will not reject it. Enforcement is **application-only**.

---

## TiDB data migration API (batch migration)

### What it does

- **Insert only, no upsert.** The TiDB data migration API (`POST /v1/payment_pages/tidb_data_migration`) does **not** check (slug, domain) uniqueness before writing. It:
  1. Fetches payment link entities (and nocode_custom_urls) from TiDB by the given `payment_link_ids`.
  2. When `deleteExistingEntities` is true (it is for this API), **deletes** NCA entities for **those same pl_ids only** (nocode, custom_urls where `product_id` in those ids, etc.).
  3. **Bulk-creates** nocode, line_items, custom_urls, configs, etc. via plain **INSERT** (`BulkCreateCustomUrls` → `tx.Create(&customUrls)`). There is no upsert or replace by (slug, domain).

So for each requested pl_id it: deletes NCA rows for that pl_id, then inserts new rows from TiDB. It does **not** touch or replace another page's custom_url row that already has the same (slug, domain).

### If a custom_url row for that (slug, domain) already exists (another page)

- **No application-level check.** The migration path does **not** call `ValidateSlug()` or `ValidateUniqueSlugDomain`. So the API does not fail with "slug already exists" from app validation.
- **DB behaviour:**
  - If the **DB** has a **unique constraint** on `(slug, domain, product_type)` (e.g. in another schema/migration repo): the second INSERT for the same (slug, domain) will hit a **duplicate key** error and the transaction will fail → API returns 5xx.
  - If the DB has **no** such constraint: the INSERT succeeds and you get **two** rows with the same (slug, domain) → hosted page resolution can break or be ambiguous.

### Why those IDs are in the exclude list (corrected from data)

From production data, the situation is **not** "another page took that (slug, domain)". For example for `QAcfLXkTr4Ei3o` (slug `llj-ga-v1`):

- **Monolith**: The page exists in `payment_links`; the slug may or may not appear in monolith’s `nocode_custom_urls` (schema/table can differ).
- **NCA**: The **same** page is already migrated: both `nocode` and `custom_urls` have a row for `product_id = QAcfLXkTr4Ei3o` with `(slug, domain) = (llj-ga-v1, pages.razorpay.com)`.

So the exclude list is for pages that **already have** their (slug, domain) row in NCA for **that same** `product_id`. If you run the **TiDB migration-by-IDs** API again for that pl_id:

1. The API **does not** use the exclude list (only the cursor-based migration uses `getFilteredPaymentLinks`).
2. It **soft-deletes** the existing custom_url for that pl_id (`BulkDeleteCustomUrlsByNocodeIds` → GORM `Delete` sets `deleted_at`).
3. It then **inserts** a new custom_url with the same (slug, domain, product_type).
4. If the DB has a **unique constraint** on `(slug, domain, product_type)` that **does not** exclude soft-deleted rows (e.g. no `WHERE deleted_at IS NULL`), the soft-deleted row still holds the unique slot → the INSERT hits a **duplicate key** → "duplicate slug" error.

So the failure when re-running data migration for these IDs is: **same page, already in NCA; soft-delete + insert conflicts with the unique index**. The exclude list is used in the **cursor-based** migration so those pl_ids are never fetched; the **TiDB-by-IDs** API does not skip them, so calling it with an ignored id can still cause this duplicate slug error.

### So for these ignored pages, should the API fail?

Ideally **no**: if the page and its (slug, domain) already exist in NCA for that pl_id, re-running migration for that pl_id should not be required, and if run it should not fail. To achieve that, one of:

1. **TiDB-by-IDs API** skips pl_ids that are in `excludePaymentLinkIds` (same as cursor-based migration), so those requests never do delete+insert and never hit the unique constraint; or  
2. **DB**: use a **partial unique index** on `(slug, domain, product_type)` with `WHERE deleted_at IS NULL`, so soft-deleted rows do not block the new insert; or  
3. **Migration**: **hard-delete** custom_urls in this flow (e.g. `Unscoped().Delete(...)`) so the row is removed and the unique slot is free before insert.

---

## Summary

| Question | Answer |
|----------|--------|
| When does slug + custom domain insert fail? | When the app finds an existing **non-deleted** `custom_urls` row with the same (slug, domain, product_type) and it's not the same page (or IntegrityCheck fails). |
| DB-level unique constraint? | **Not in this repo.** May exist in the actual NCA DB (other repo/schema). |
| Application-level check? | **Yes** for normal create/update. **No** for TiDB data migration API. |
| TiDB migration: upsert or insert? | **Insert only.** No upsert; no slug/domain check before insert. |
| TiDB migration: fail if (slug, domain) already taken? | Only if the DB has a unique constraint on that combination; otherwise it would insert a duplicate. |
