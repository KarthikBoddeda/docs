# payment_page_create Code Reference

**API:** `POST /payment_pages`  
**Route Name:** `payment_page_create`

> **⚠️ IMPORTANT:** NCA code is written to **exactly mimic monolith behavior**. Any mismatch is a bug. Monolith is the source of truth.

---

## Route Definition

**File:** `internal/router/payment_page_private_routes.go`

```go
{
    constants.PaymentPageCreateRouteName,  // "payment_page_create"
    http.MethodPost,
    "",                                    // Route: /v1/payment_pages
    controllers.PaymentPageCtrl.Create,
}
```

---

## NCA Code Flow

### 1. Controller Entry
**File:** `internal/controllers/payment_page.go`  
**Function:** `PaymentPageController.Create()` → calls `standardDualWriteHandler.Handle(request, ncaCreate)`

### 2. Dual Write Handler
**File:** `internal/monolith_decomp/dual_write_handlers/base.go`  
**Function:** `GenericDualWriteHandler.Handle()`

Based on proxy_state:
- `dual_write_*`: Proxy to monolith → Execute NCA → Compare responses
- `nca_only`: Execute NCA only
- `monolith_only`: Proxy to monolith only

### 3. NCA Create Logic
**File:** `internal/controllers/payment_page.go`  
**Function:** `PaymentPageController.ncaCreate()`

Steps:
1. Bind request body → `PaymentPageRequest`
2. Set monolith response (for dual write ID extraction)
3. `SetDefaultFieldsInRequest()`
4. `SetMerchantId()`, `SetMode()`
5. **`req.ValidateForCreate()`** ← VALIDATION HAPPENS HERE
6. `core.CreatePaymentPage(ctx, &req, &res)`
7. Return JSON response

### 4. Payment Page Request Validation
**File:** `internal/modules/payment_page/validation.go`  
**Function:** `PaymentPageRequest.ValidateForCreate()`

Steps:
1. **`n.NocodeRequest.ValidateForCreate()`** ← BASE VALIDATION
2. `ValidateForBlackListedSlug()`
3. `ValidateSlug()`
4. Validate `settings.CheckoutOptions` (phone, email required)
5. Validate `payment_page_items` (1-25 items required)

### 5. Base Nocode Validation
**File:** `internal/modules/nocode/validation.go`  
**Function:** `NocodeRequest.ValidateForCreate()`

Steps:
1. Validate `SupportContact` (contact number syntax)
2. Validate `SupportEmail` (email format)
3. Validate `Notes` (key-value format)
4. Validate `TemplateType` (length 0-20)
5. Validate Settings via `settings.Validate()`
6. **TrackerType required check** ← Most common diff source!

### 6. Core Business Logic
**File:** `internal/modules/payment_page/core.go`  
**Function:** `PaymentPageCore.CreatePaymentPage()`

Steps:
1. `embedMonolithIdsIntoCreateRequestIfApplicable()`
2. `assertCreatePaymentPageIsSupportedInNCA()`
3. `assertIsWriteRequestAllowed()`
4. `GetMerchantDetails()`, `GetMerchantFeatures()`
5. `ValidateCreateRequestBasedOnMerchantDetails()`
6. Create `PaymentPageEntity` from request
7. Generate/Set ID (or use monolith ID for dual write)
8. Generate short URL (if not dual write)
9. `createPaymentPageEntitiesWithTransaction()` → DB write
10. `BuildHostedPayloadAndUpdateCache()`
11. `DualWriteSyncToMonolith()` (async)
12. Push async jobs (risk, ES, etc.)

---

## Validation Points (Where Diffs Can Occur)

### 1. NocodeRequest.ValidateForCreate()

**File:** `internal/modules/nocode/validation.go:496-538`

| Field | Validation | Potential Diff |
|-------|------------|----------------|
| `SupportContact` | Contact number syntax | Regex differences |
| `SupportEmail` | Email format | Format validation |
| `Notes` | Key-value format | Structure validation |
| `TemplateType` | Length 0-20 | Length check |
| `Settings.GoalTracker.TrackerType` | **Required if GoalTracker exists** | ⚠️ Most common diff |

**TrackerType Validation (Line 533-535):**
```go
if settings.GoalTracker != nil && settings.GoalTracker.TrackerType == nil {
    return errorclass.ErrValidationFailure.New("The tracker type field is required.")
}
```

### 2. PaymentPageRequest.ValidateForCreate()

**File:** `internal/modules/payment_page/validation.go:113-152`

| Field | Validation | Potential Diff |
|-------|------------|----------------|
| `Slug` | Blacklist, format, uniqueness | Slug validation rules |
| `settings.CheckoutOptions.Phone` | Required | |
| `settings.CheckoutOptions.Email` | Required | |
| `payment_page_items` | 1-25 items required | Count validation |

### 3. ValidateCreateRequestBasedOnMerchantDetails()

**File:** `internal/modules/payment_page/core.go` (search for this function)

Validates based on merchant settings:
- Currency validation
- Amount limits
- Feature flags

### 4. Entity Validation

**File:** `internal/modules/payment_page/validation.go:39-73`

| Field | Validation |
|-------|------------|
| `Title` | Required, 3-80 chars, UTF-8 |
| `Description` | 0-65535 chars, UTF-8, JSON format |
| `Terms` | 5-2048 chars if present, UTF-8 |

---

## Key Request Structs

### PaymentPageRequest

**File:** `internal/modules/payment_page/request.go`

Embeds `NocodeRequest` and adds Payment Page specific fields.

### NocodeRequest

**File:** `internal/modules/nocode/request.go:93+`

```go
type NocodeRequest struct {
    PublicId       string
    Title          string
    Description    string
    Currency       string
    Notes          interface{}
    ExpireBy       *nulls.Int64
    Type           string
    ViewType       *string
    Status         string
    StatusReason   *string
    Settings       map[string]interface{}  // Contains GoalTracker, CheckoutOptions, etc.
    Terms          string
    TemplateType   *string
    SupportContact *string
    SupportEmail   *string
    Slug           interface{}
    // ... more fields
}
```

### Settings.GoalTracker

**File:** `internal/modules/nocode/settings.go:84-88`

```go
type GoalTracker struct {
    TrackerType *string              `json:"tracker_type,omitempty"`
    IsActive    *string              `json:"is_active,omitempty"`
    MetaData    *GoalTrackerMetaData `json:"meta_data,omitempty"`
}
```

---

## Common Diffs and Where to Look

| Diff Type | Where to Look |
|-----------|---------------|
| `tracker_type required` | `nocode/validation.go:533-535` |
| `description contains invalid characters` | `payment_page/validation.go` - UTF-8 validation |
| `title contains invalid characters` | `payment_page/validation.go` - UTF-8 validation |
| `slug already exists` | `nocode/validation.go` - slug uniqueness |
| `payment_success_message invalid` | Settings validation |
| `min_purchase validation` | Line item validation |
| `contact number validation` | `nocode/validation.go` - contact syntax |
| `udf_schema max items` | Settings validation |

---

## Dual Write ID Extraction

For dual writes, NCA reuses IDs from monolith response.

**File:** `internal/modules/payment_page/core.go`

**Function:** `embedMonolithIdsIntoCreateRequestIfApplicable()`

Extracts:
- `payment_page_id` from monolith response
- `payment_page_item_id` for each item
- `short_url` if available

---

## Related Files

| File | Purpose |
|------|---------|
| `internal/controllers/payment_page.go` | HTTP handler (`Create`, `ncaCreate`) |
| `internal/modules/payment_page/validation.go` | PP-specific validations |
| `internal/modules/nocode/validation.go` | Base validations (TrackerType check here!) |
| `internal/modules/payment_page/core.go` | Business logic (`CreatePaymentPage`) |
| `internal/modules/payment_page/request.go` | Request structs |
| `internal/modules/nocode/settings.go` | Settings struct (GoalTracker definition) |
| `internal/monolith_decomp/dual_write_handlers/base.go` | Dual write handler |

---

## Debugging Tips

1. **For validation diffs:** Start at `ncaCreate()` in controller, trace through `ValidateForCreate()` calls
2. **For business logic diffs:** Check `CreatePaymentPage()` in core
3. **Check proxy state:** Is NCA even executing? Check proxy state in logs
4. **Compare with monolith:** Remember, NCA should match monolith exactly

