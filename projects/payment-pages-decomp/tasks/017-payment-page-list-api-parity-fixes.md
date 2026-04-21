# Payment Page List API Parity Fixes

**Discovered from:** Shadow diff analysis (batches post-datafix, Feb 2026)  
**Route:** `payment_page_list` → `GET /v1/payment_pages`  
**Priority:** High — directly affects merchant dashboard experience in NCA read path

---

## Overview

Three independent bugs were identified in NCA's `ListPaymentPages` implementation that cause parity failures against the monolith. They were discovered by analyzing `pages_missing_in_nca`, `pages_extra_in_nca`, and `/count` diffs in shadow traffic logs and confirmed by live API testing on merchant `Ha18e7jHMVjYEb`.

---

## Bug 1 — `status` query parameter is silently ignored

### Severity: HIGH

### Observed symptom

When a client calls `GET /v1/payment_pages?status=inactive&count=25&skip=0`, monolith correctly returns 25 inactive pages. NCA **ignores the `status` param entirely** and returns the 25 most recently created pages regardless of status (usually all active).

This produces a **complete set mismatch** where 0 pages overlap between monolith and NCA:

| params | monolith | NCA | shape |
|---|---|---|---|
| `status=inactive` | 10 inactive pages | 25 most-recent active pages | `(10, 25)` |
| `status=inactive&count=25` | 25 inactive pages | 25 most-recent active pages | `(25, 25)` |
| `status=inactive&count=100` | 100 inactive pages | 100 most-recent active pages | `(100, 100)` |

Live API verification (merchant `Ha18e7jHMVjYEb`, `2026-02-20`):
```
status=inactive&count=25&skip=0
  monolith → 25 inactive pages, first: pl_SII8rH2rHId2QV, pl_SII8aIcb7RJNWs
  nca      → 25 active pages,   first: pl_SIQrjlYiRQc1ZH, pl_SIQrBIRx7TA4ar
  overlap  → 0
```

### Root cause

**Step 1 — Controller doesn't read `status` from the request**

`/internal/controllers/payment_page.go` (function `ncaList`):

```go
// CURRENT — only reads skip, count, title
skip  := utils.LogicalOROnStringCastables(request.Query("skip"),  requestBody["skip"])
count := utils.LogicalOROnStringCastables(request.Query("count"), requestBody["count"])
title := utils.LogicalOROnStringCastables(request.Query("title"), requestBody["title"])

res, berr := controller.core.ListPaymentPages(ctx, skip, count, title)
```

`status` is never extracted and never forwarded to the core.

**Step 2 — Core function signature doesn't accept `status`**

`/internal/modules/payment_page/core.go`:

```go
// CURRENT
func (c *PaymentPageCore) ListPaymentPages(
    ctx context.Context,
    skipStr, countStr, title string,          // ← no status
) ([]PaymentPageResponse, errors.IError)
```

**Step 3 — Repo query has no status filter**

`/internal/modules/payment_page/repo.go` (`FindAllWithPagination`):

```go
// CURRENT — no status WHERE clause
q := r.Db().Instance(ctx).Offset(skip).Limit(count).
    Order("created_at DESC").
    Preload(...).
    Where("merchant_id = ?", merchantId).
    Where("mode = ?", mode).
    Where("type = ?", nocode.PageViewType)
// title is conditionally applied below, but status never is
```

### Fix

**1. Update `FindAllWithPagination` in `/internal/modules/payment_page/repo.go`:**

```go
func (r *PaymentPageRepo) FindAllWithPagination(
    ctx context.Context,
    receiver interface{},
    skip, count int,
    title, status string,  // ← add status
) errors.IError {
    merchantId := app.GetMerchantId(ctx)
    mode := app.GetMode(ctx)

    q := r.Db().Instance(ctx).Offset(skip).Limit(count).
        Order("created_at DESC").
        Preload(constants.AssociationLineItemsPrice).
        Preload(constants.AssociationLineItemsAnalytics).
        Preload(constants.AssociationAnalytics).
        Preload(constants.AssociationConfig).
        Where("merchant_id = ?", merchantId).
        Where("mode = ?", mode).
        Where("type = ?", nocode.PageViewType)

    if title != "" {
        q = q.Where("LOWER(title) LIKE LOWER(?)", fmt.Sprintf("%%%s%%", title))
    }

    if status != "" {
        q = q.Where("status = ?", status)  // ← add this
    }

    q = q.Find(receiver)

    if q.Error != nil {
        return spine.GetDBError(q)
    }

    return nil
}
```

**2. Update the interface in `/internal/modules/payment_page/repo.go`:**

```go
// In the IPaymentPageRepo interface:
FindAllWithPagination(ctx context.Context, receiver interface{}, skip, count int, title, status string) errors.IError
```

**3. Update `ListPaymentPages` in `/internal/modules/payment_page/core.go`:**

```go
// Interface (line ~154):
ListPaymentPages(ctx context.Context, skipStr, countStr, title, status string) ([]PaymentPageResponse, errors.IError)

// Implementation (line ~3044):
func (c *PaymentPageCore) ListPaymentPages(
    ctx context.Context,
    skipStr, countStr, title, status string,  // ← add status
) ([]PaymentPageResponse, errors.IError) {
    skip, err := strconv.Atoi(skipStr)
    if err != nil {
        skip = DefaultPage
    }

    count, err := strconv.Atoi(countStr)
    if err != nil {
        count = DefaultPPListLimit
    }

    var paymentPages []PaymentPageEntity
    err = c.repo.FindAllWithPagination(ctx, &paymentPages, skip, count, title, status)  // ← pass status
    // ... rest unchanged
}
```

**4. Update the controller in `/internal/controllers/payment_page.go`:**

```go
func (controller *PaymentPageController) ncaList(
    request request.IRequest,
    monolithResponse response.IResponse,
) response.IResponse {
    ctx := request.Ctx()
    requestBody := request.GetRequestBody()

    skip   := utils.LogicalOROnStringCastables(request.Query("skip"),   requestBody["skip"])
    count  := utils.LogicalOROnStringCastables(request.Query("count"),  requestBody["count"])
    title  := utils.LogicalOROnStringCastables(request.Query("title"),  requestBody["title"])
    status := utils.LogicalOROnStringCastables(request.Query("status"), requestBody["status"])  // ← add this

    res, berr := controller.core.ListPaymentPages(ctx, skip, count, title, status)  // ← pass status
    // ... rest unchanged
}
```

**5. Update mock in `/internal/modules/payment_page/mock_repo_test.go`:**

The mock's `FindAllWithPagination` signature must also be updated to match the new interface (add `status string` parameter).

### Testing checklist

- [ ] `GET /v1/payment_pages?status=inactive` returns only inactive pages
- [ ] `GET /v1/payment_pages?status=active` returns only active pages
- [ ] `GET /v1/payment_pages` (no status) still returns all pages (unfiltered)
- [ ] `GET /v1/payment_pages?status=inactive&count=25&skip=0` matches monolith result
- [ ] Parity diff checker shows `(0,0)` for status-filtered calls after fix

---

## Bug 2 — Default `count` differs from monolith (NCA=25, monolith=10)

### Severity: MEDIUM

### Observed symptom

When a client calls `GET /v1/payment_pages` with no `count` param, monolith defaults to returning **10** items while NCA defaults to **25**. This causes a `(0, 15)` shape diff (NCA has 15 extra items) plus a `/count` field mismatch.

Live API verification:
```
GET /v1/payment_pages  (no params)
  monolith → count=10, 10 items
  nca      → count=25, 25 items
  overlap  → 10 (all monolith items are in NCA's top 25)
  diff     → (0 missing, 15 extra in NCA), /count: 10 vs 25
```

### Root cause

`/internal/modules/payment_page/constants.go`:

```go
// CURRENT
DefaultPPListLimit = 25   // ← should be 10 to match monolith
DefaultPage        = 0
```

### Fix

Change `DefaultPPListLimit` to `10`:

```go
// /internal/modules/payment_page/constants.go
DefaultPPListLimit = 10   // ← matches monolith default
DefaultPage        = 0
```

### Testing checklist

- [ ] `GET /v1/payment_pages` (no params) returns 10 items
- [ ] `GET /v1/payment_pages?count=25` still returns 25 items
- [ ] Parity diff checker shows no `/count` diff and `(0,0)` shape for default calls

---

## Bug 3 — Title search semantics differ from monolith (DB LIKE vs ES full-text)

### Severity: LOW–MEDIUM

### Observed symptom

When a client calls `GET /v1/payment_pages?title=<search_term>`, NCA and monolith return different page counts and sets. Examples from live traffic:

| merchant | title filter | monolith count | NCA count |
|---|---|---|---|
| `Ha18e7jHMVjYEb` | `y-104` | 25 | 9 |
| `Ha18e7jHMVjYEb` | `g-01` | 25 | 15 |
| `Jm5NuHPOevlGjc` | `Sadhana Tiwari` | 25 | 2 |
| `Nb3LsbAB1ToDoA` | `24` | 1 | 2 |

### Root cause

**NCA** uses a DB LIKE query:
```go
// repo.go
q = q.Where("LOWER(title) LIKE LOWER(?)", fmt.Sprintf("%%%s%%", title))
```

**Monolith** uses Elasticsearch full-text search on the title field, which has different ranking, tokenization, and matching behavior.

Specific divergences:
- ES may match partial words differently than SQL `LIKE`
- ES applies analyzers/tokenizers (e.g., splitting on spaces/hyphens)
- ES has its own pagination/relevance ordering, NCA uses `created_at DESC`

### Fix

This is inherently a search-semantics gap that cannot be 100% fixed with a DB query alone. However there are two paths:

**Option A (Simple, recommended for now):** Keep DB LIKE search in NCA but ensure the `count` response field reflects the total matching count (not just the page size), so pagination works consistently. Also ensure ordering matches monolith (`updated_at DESC` or `created_at DESC` — verify which monolith uses for title searches).

**Option B (Full parity):** Integrate NCA with the same ES index monolith uses for title search. This is a larger change and probably out of scope for now.

For the intern: **implement Option A** — fix the response `count` field to be total matching rows (requires a separate `COUNT(*)` query with the same WHERE clause), not just the requested page size.

In `/internal/modules/payment_page/repo.go`, add a `CountAllWithFilter` function:

```go
func (r *PaymentPageRepo) CountAllWithFilter(ctx context.Context, title, status string) (int64, errors.IError) {
    merchantId := app.GetMerchantId(ctx)
    mode := app.GetMode(ctx)
    var total int64

    q := r.Db().Instance(ctx).
        Model(&PaymentPageEntity{}).
        Where("merchant_id = ?", merchantId).
        Where("mode = ?", mode).
        Where("type = ?", nocode.PageViewType)

    if title != "" {
        q = q.Where("LOWER(title) LIKE LOWER(?)", fmt.Sprintf("%%%s%%", title))
    }
    if status != "" {
        q = q.Where("status = ?", status)
    }

    q = q.Count(&total)
    if q.Error != nil {
        return 0, spine.GetDBError(q)
    }
    return total, nil
}
```

Then update `ListPaymentPages` to return the total count alongside the items, and update the response serialization to include `count = total` (not `len(items)`).

### Testing checklist

- [ ] `GET /v1/payment_pages?title=<term>` returns `count` = total matching pages, not page size
- [ ] `GET /v1/payment_pages?title=<term>&count=5` returns 5 items but `count` = total

---

## Files to change (summary)

| File | Change |
|---|---|
| `/internal/controllers/payment_page.go` | Extract `status` from request, pass to `ListPaymentPages` |
| `/internal/modules/payment_page/core.go` | Add `status` param to `ListPaymentPages` interface + impl |
| `/internal/modules/payment_page/repo.go` | Add `status` WHERE clause to `FindAllWithPagination`; add `CountAllWithFilter` |
| `/internal/modules/payment_page/constants.go` | Change `DefaultPPListLimit` from `25` to `10` |
| `/internal/modules/payment_page/mock_repo_test.go` | Update mock signatures to match new interface |

---

## What NOT to fix here

These are known/expected diffs from the same route — **do not confuse with the above bugs**:

- **Live counter diffs** (`quantity_sold`, `total_amount_paid`) — race condition, both systems queried at slightly different times. Not fixable via code.
- **`expire_by` diff for merchant `IgP1gE3lHWkQFc`** — downstream of the activate-API bug (separate issue). Data fix required.
- **ES lag `(1,1)` diffs** — a page just created via monolith gets indexed in ES with a small delay. NCA reads from DB directly so it appears immediately. Expected transient behavior.
