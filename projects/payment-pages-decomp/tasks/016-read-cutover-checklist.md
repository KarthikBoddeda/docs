# Read cutover checklist: `shadow_read` → `read`

Moving from `dual_write_shadow_read_no_external` to `dual_write_read_no_external`.

## What changes

### Read APIs (`GenericDualReadHandler`)

| | shadow_read (current) | read (target) |
|---|---|---|
| Monolith called? | Yes | **No** |
| NCA called? | Yes | Yes |
| Diff checked? | Yes | No |
| Response returned to user | **Monolith** | **NCA** |
| Fallback if NCA errors? | Monolith response | **None** |

Affected handlers:
- `standardDualReadHandler` → Get, GetDetails, List
- `hostedHandler` → HostedPaymentPageView, HostedPaymentPageViewPost
- `hostedSlugHandler` → HostedPaymentPageViewBySlug, HostedPaymentPageViewBySlugPost

### Write APIs (`GenericDualWriteHandler`)

| | shadow_read (current) | read (target) |
|---|---|---|
| Monolith called? | Yes | Yes |
| NCA called? | Yes | Yes |
| Diff checked? | Yes | Yes |
| Response returned to user | **Monolith** | **Monolith** |

Write APIs behave **identically** in both states — monolith response is always returned, both backends are called, diffs are calculated. This was changed from the original behavior (which returned NCA response in `read` state) because 4xx errors from the monolith cause the NCA write to be skipped, resulting in bad/empty error messages from NCA.

Affected handlers:
- `standardDualWriteHandler` → Create, Update, Activate, Deactivate, ItemUpdate, SetReceiptDetails
- `createOrderDualWriteHandler` → CreateOrder

### Not affected

- `invoiceHandler` (uses `GenericExternalEntityHandler`, still proxies to monolith in this state)
- GetPayments, SlugExists, FetchMerchantDetails (always proxy to monolith)

---

## A. Shadow read diffs must be zero or accepted

- [ ] Check Coralogix for shadow diff metrics over the last 7+ days. Zero diffs on:
  - `payment_page_get`
  - `payment_page_get_details`
  - `payment_page_list`
  - `hosted_page_view` / `hosted_page_view_post`
  - `hosted_page_view_by_slug` / `hosted_page_view_by_slug_post`
- [ ] If any diffs remain, document and confirm they're acceptable

## B. Data completeness

- [ ] All `type = 'page'` entities are in NCA — run count comparison:
  ```sql
  -- Monolith (Redash)
  SELECT COUNT(*) FROM payment_links WHERE view_type = 'page';
  -- NCA (Redash)
  SELECT COUNT(*) FROM nocode WHERE type = 'page';
  ```
- [ ] Dual writes are working — any page created/updated after migration is in both DBs
- [ ] Soft deletes consistent — `deleted_at` values match between monolith and NCA

## C. Known bugs to fix BEFORE moving

- [ ] **Deploy the `view_type` proxy fix** — without this, `view_type=button` list requests go to NCA and return pages instead of buttons
- [ ] **List title filter not implemented** — in shadow_read, user gets monolith response (filtered). In read, user gets NCA response (unfiltered). Decision needed: is this acceptable? (~256 requests/week from heaviest merchant use title filter)

## D. NCA panic returns wrong status code

- [ ] **NCA panic recovery sends 400 instead of 500** — In `executeNCAOperationWithPanicRecovery` (`/no-code-apps/internal/monolith_decomp/dual_write_handlers/base.go:191`), if NCA panics, the response is wrapped as a 400 Bad Request even though it should be a 500 Internal Server Error. In `shadow_read` this doesn't matter (monolith response is returned for reads). In `read` state, read APIs return NCA response directly, so a panic would surface this wrong status code to the user. Fix or accept the risk (panics should be rare).

## E. Composite index on nocode table

- [ ] `idx_nocode_merchant_id_created_at (merchant_id, created_at)` must be created before cutover
- [ ] Without it, list queries on heavy merchants (~85k rows) take ~12s due to filesort
- [ ] Gandalf JIRA: (add ticket link here)

## F. Hosted pages (payer-facing, highest severity)

- [ ] Hosted page view renders HTML for end-user payers — if NCA returns wrong data, payers see a broken payment page
- [ ] Verify hosted page rendering works correctly from NCA data for a sample of pages
- [ ] Hosted handler gets proxy state per payment page ID (not from Splitz) — verify this returns the right state for all migrated pages

## G. Performance

- [ ] NCA DB can handle the read load alone (currently both monolith and NCA are called; after cutover only NCA)
- [ ] Verify NCA DB replica latency is acceptable
- [ ] List query performance is acceptable (depends on composite index being created)

## H. Alerting

- [ ] **Create alert on `MONOLITH_DUAL_WRITE_ERROR`** — In `nca_only`, NCA syncs order line items to monolith via `DualWriteSyncToMonolith` (`/no-code-apps/internal/modules/payment_page/monolith_dual_write.go:83-90`). If this fails, monolith has the order but no line items, breaking reporting. The sync is async with no retry, so failures are silent. Alert on the `monolith_dual_write_error` label of `UnexpectedErrorCounter` metric or the `MONOLITH_DUAL_WRITE_ERROR` log trace code.
- [ ] **Create alert on `PAYMENT_ON_NON_PAYABLE_PAGE`** — When the monolith's `remove_pp_validations_on_payment_create` experiment is on, payment page payability/stock validations are skipped during payment creation. If a payment is captured on a non-payable page (expired, completed, etc.), NCA logs `PAYMENT_ON_NON_PAYABLE_PAGE` and increments `UnexpectedErrorCounter` with label `payment_on_non_payable_page_to_be_refunded`. Auto-captured payments are refunded automatically; non-auto-captured ones need manual refund. Alert on this metric to catch and refund these payments. (`/no-code-apps/internal/modules/payments/payment_page.go`)

## I. Rollback plan

- [ ] Rollback = move back to `shadow_read` in Splitz → immediately restores monolith responses for reads
- [ ] Verify rollback doesn't require a deploy (just Splitz config change)
- [ ] Have monitoring dashboards ready (error rates, latency, diff metrics)
- [ ] Write APIs are unaffected by rollback (monolith response in both states)

## J. Rollout strategy

- [ ] Roll out per merchant via Splitz — don't move all merchants at once
- [ ] Start with low-traffic merchants, monitor for a day
- [ ] Then add high-traffic merchants one by one
- [ ] Monitor for at least 24h with full traffic before declaring stable
