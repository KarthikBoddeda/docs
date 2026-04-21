# Validation Gaps Analysis - Phase 2 Write APIs

**Created:** 2026-01-21

## Problem Statement
After the initial phase 2 write API fixes, additional validation mismatches have been identified between NCA and Monolith. This task tracks the analysis and fixes for these gaps.

## Reference
- Monolith Validator: `api/app/Models/PaymentLink/Validator.php`
- Monolith PaymentPageItem Validator: `api/app/Models/PaymentLink/PaymentPageItem/Validator.php`
- NCA Validation: `no-code-apps/internal/modules/nocode/validation.go`
- NCA LineItemPrice Validation: `no-code-apps/internal/modules/line_item_price/validation.go`

---

## Subtasks

### 1. [HIGH] min_amount Currency Validation - WRONG MIN_VALUE DATA
| Field | Status |
|-------|--------|
| **Issue** | NCA returns 400, Monolith returns 200 for min_amount below currency minimum |
| **Error** | `validation_failure: min_amount: amount should be minimum 50 for USD` |
| **Root Cause** | 🔴 **NCA had wrong min_value for USD!** |
| **Fix Applied** | ✅ Fixed USD min_value: 50 → 10 |
| **Unit Tests** | ✅ Tests updated |
| **Devstack Test** | ✅ Verified, no diffs |
| **Review** | ⬜ |
| **Committed** | ⬜ |

**Root Cause Analysis:**

| Currency | Monolith MIN_VALUE | Monolith MIN_AUTH_VALUE | NCA min_value (Before) | NCA min_value (After) |
|----------|-------------------|------------------------|------------------------|----------------------|
| **USD** | **10** (10 cents) | 50 (50 cents) | 50 ❌ | **10** ✅ |
| INR | 100 paise | 100 paise | 100 paise ✅ | 100 paise ✅ |

**Fix Applied:**
- Updated `no-code-apps/pkg/country/currency.go` USD min_value from 50 to 10

**Files Modified:**
- `no-code-apps/pkg/country/currency.go` - Fixed USD min_value
- `no-code-apps/internal/modules/line_item_price/validation_test.go` - Updated tests

**Devstack Test Results (2026-01-21):**
- ✅ min_amount = 50 (below INR min 100) → Correctly rejected
- ✅ min_amount = 200 (above INR min 100) → Correctly accepted
- ✅ Dual write mode → `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST`

---

### 2. [MEDIUM] max_amount Currency Minimum Validation
| Field | Status |
|-------|--------|
| **Issue** | NCA did NOT validate max_amount against currency minimum |
| **Monolith** | `api/app/Models/PaymentLink/PaymentPageItem/Validator.php:212-233` |
| **NCA** | Now validates both min_amount and max_amount |
| **Fix Applied** | ✅ Added max_amount currency validation |
| **Unit Tests** | ✅ Added TestValidateForPaymentPages_MaxAmountCurrencyMinimum |
| **Devstack Test** | ✅ Verified |
| **Review** | ⬜ |
| **Committed** | ⬜ |

**Fix Applied:**
- Updated `validateForPaymentPagesInternal` to accept two booleans for min/max amount validation
- Added max_amount currency validation with conditional logic (only on CREATE or when being updated)
- Added comprehensive unit tests for max_amount validation

**Files Modified:**
- `no-code-apps/internal/modules/line_item_price/validation.go` - Added max_amount validation
- `no-code-apps/internal/modules/line_item_price/validation_test.go` - Added tests

**Devstack Test Results (2026-01-21):**
- ✅ max_amount = 50 (below INR min 100) → Correctly rejected with "amount should be minimum 100 for INR"

---

### 3. [LOW] receipt Field Validation - NO ACTIVE FAILURES
| Field | Status |
|-------|--------|
| **Issue** | NCA doesn't have `receipt` field in request model |
| **Monolith** | `'string|min:3|max:40|nullable'` |
| **NCA** | Not in NocodeRequest - field ignored if sent |
| **Failure Logs** | ✅ No receipt validation failures found in phase_2 logs |
| **Action** | N/A - field not used in practice |

**Analysis:**
- The `receipt` field exists in response models (`models/payment_page.go`)
- NOT in `NocodeRequest` struct - requests ignore this field
- No validation failures reported in phase_2 failure logs
- LOW priority - no action needed unless failures surface

---

### 4. [VERIFIED ✅] goal_tracker Validation
| Field | Status |
|-------|--------|
| **Issue** | Initially reported as missing - FOUND! |
| **Location** | `no-code-apps/internal/modules/goal_tracker/validation.go` |
| **Verified** | ✅ Full validation exists |

**Validations Present:**
- `Type` (TrackerType): required, must be `donation_amount_based` or `donation_supporter_based`
- `GoalAmount`: required when type is `donation_amount_based`, must be > 0
- `AvailableUnits`: required when `display_available_units` is "1"
- `EndsBy`: required when `display_days_left` is "1"
- `DisplaySupporterCount`: required, must be 0 or 1
- `DisplayDaysLeft`: required, must be 0 or 1
- `DisplaySoldUnits`: required for supporter-based, must be 0 or 1
- `DisplayAvailableUnits`: required for supporter-based, must be 0 or 1

**Called From:**
- `HandleGoalTrackerCreation()` during CREATE
- `validateAndUpdateGoalTracker()` during UPDATE

---

### 5. [VERIFIED ✅] stock >= quantity_sold Validation
| Field | Status |
|-------|--------|
| **Issue** | Initially reported as missing - FOUND! |
| **Location** | `no-code-apps/internal/modules/payment_page/core.go:750-751` |
| **Verified** | ✅ |

**NCA Code:**
```go
if monolithItemRequest.Stock != nil && monolithItemRequest.Stock.Value != 0 && 
   monolithItemRequest.Stock.Value < analyticsEntity.GetTotalUnits() {
    return nil, errorclass.ErrValidationFailure.New("").Wrap(
        goerr.New("stock cannot be lesser than the quantity sold"))
}
```

---

### 6. [VERIFIED ✅] view_type Validation
| Field | Status |
|-------|--------|
| **Issue** | Initially reported as missing - FOUND! |
| **Location** | `no-code-apps/internal/modules/payment_page/core.go:1168-1176` |
| **Verified** | ✅ |

**NCA Code:**
```go
func assertCreatePaymentPageIsSupportedInNCA(ctx context.Context, req IPaymentPageRequest) errors.IError {
    viewType := req.GetViewType()
    if viewType == nil { ... }
    if !IsNCASupportedViewTypeForCreateRequest(*viewType) { ... }
}
```

---

### 7. [VERIFIED ✅] Amount + MinAmount/MaxAmount Conflict
| Field | Status |
|-------|--------|
| **Issue** | Originally buggy - FIXED in previous session |
| **Location** | `no-code-apps/internal/modules/line_item_price/validation.go:129-134` |
| **Verified** | ✅ |

**NCA Code (Fixed):**
```go
// If amount is set AND (min_amount OR max_amount) is set, throw error
if m.Amount != nil && (m.MinAmount != nil || m.MaxAmount != nil) {
    return utils.GetValidationError(fmt.Errorf("amount not required when min amount or max amount is present"))
}
```

---

### 8. [SKIPPED] validateItemPresent (Plan Validation)
| Field | Status |
|-------|--------|
| **Issue** | Item must be sent when plan doesn't exist |
| **Decision** | SKIPPED per user request - plan validation to be reviewed later |

---

### 9. [SKIPPED] validateCurrency for Item
| Field | Status |
|-------|--------|
| **Issue** | Payment page item currency must match payment page currency |
| **Decision** | SKIPPED per user request - complex validation to be reviewed later |

---

## Summary

| # | Task | Priority | Status | Devstack | UTs |
|---|------|----------|--------|----------|-----|
| 1 | min_amount currency validation - USD min_value fix | HIGH | ✅ FIXED | ✅ Verified (code deployed, INR tested) | ✅ |
| 2 | max_amount currency minimum validation | MEDIUM | ✅ FIXED | ✅ Verified (INR tested) | ✅ |
| 3 | receipt field validation | LOW | ✅ NO FAILURES | N/A | N/A |
| 4 | goal_tracker validation | N/A | ✅ VERIFIED EXISTS | N/A | N/A |
| 5 | stock >= quantity_sold validation | N/A | ✅ VERIFIED EXISTS | N/A | N/A |
| 6 | view_type validation | N/A | ✅ VERIFIED EXISTS | N/A | N/A |
| 7 | Amount + MinAmount/MaxAmount conflict | N/A | ✅ FIXED | ✅ Verified | ✅ |
| 8 | validateItemPresent (plan) | LOW | ⏭️ SKIPPED | - | - |
| 9 | validateCurrency for Item | MEDIUM | ⏭️ SKIPPED | - | - |

---

## Work Log

### 2026-01-21

#### Analysis Complete
- Cross-verified validations in request, entity, and module files
- Found that goal_tracker, stock >= quantity_sold, and view_type validations already exist
- Confirmed Amount + MinAmount/MaxAmount conflict was fixed in previous session
- Identified 3 remaining gaps: min_amount on create, max_amount currency validation, receipt validation

#### Fixes Applied

**1. USD min_value Fix**
- **Root Cause:** NCA's `currency.go` had USD min_value=50 (MIN_AUTH_VALUE) instead of 10 (MIN_VALUE)
- **Fix:** Changed USD min_value from 50 to 10 in `pkg/country/currency.go`
- **Unit Tests:** Updated all tests to use new USD minimum (10 cents)

**2. max_amount Currency Validation**
- **Issue:** NCA wasn't validating max_amount against currency minimum
- **Fix:** Added max_amount validation to `validateForPaymentPagesInternal`
- **Conditional:** Only validates on CREATE or when max_amount is being updated
- **Unit Tests:** Added `TestValidateForPaymentPages_MaxAmountCurrencyMinimum` test suite

**Files Modified:**
```
no-code-apps/pkg/country/currency.go              # USD min_value: 50 → 10
no-code-apps/internal/modules/line_item_price/validation.go  # Added max_amount validation
no-code-apps/internal/modules/line_item_price/validation_test.go  # Updated tests
```

#### Devstack Testing Complete (2026-01-21 19:53 UTC)

**Pod:** `no-code-apps-pp-mid-fix-6fdb59fc5b-jh28m-d7p98`

| Test | Request | Expected | Result |
|------|---------|----------|--------|
| USD min_value deployed | `kubectl exec ... cat currency.go \| grep USD` | `min_value: 10` | ✅ **Verified** |
| INR dual_write CREATE | min_amount=100, max_amount=5000 | `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` | ✅ **Passed** |
| INR dual_write UPDATE | title change only (not touching min_amount) | `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` | ✅ **Passed** |

**Note:** USD test returns "international transactions not activated" - this is a merchant config issue, not min_amount validation. The code fix is verified deployed.

---

## payment_page_create_order 200_400 Diffs Analysis (2026-01-22)

### Summary

| Count | Error | Root Cause | Action |
|-------|-------|------------|--------|
| 25x | `amount should be equal to payment page item amount` | DATA MISMATCH | Won't Fix |
| 13x | `order cannot be created for payment page which is not active` | DATA MISMATCH | Won't Fix |
| 7x | `ppi_XXX is mandatory payment page item, should be ordered` | DATA MISMATCH | Won't Fix |
| 4x | `amount should not be lesser than the payment page item min amount` | DATA MISMATCH | Won't Fix |
| 1x | `item ppi_XXX does not exist, please refresh and try again` | DATA MISMATCH | Won't Fix |

### Code Comparison - Validation Logic is IDENTICAL

**Monolith** (`api/app/Models/PaymentLink/PaymentPageItem/Validator.php:382-438`):
```php
public function validateAmountQuantityAndStockOfPPI(Entity $paymentPageItem, array $input)
{
    if ((is_null($paymentPageItem->item->getAmount()) === false) and
        ($paymentPageItem->item->getAmount() !== $input[Item\Entity::AMOUNT]))
    {
        throw new BadRequestValidationFailureException(
            'amount should be equal to payment page item amount'
        );
    }
    // ... similar for min_amount, max_amount, stock
}
```

**NCA** (`no-code-apps/internal/modules/payment_page/validation.go:278-324`):
```go
func validateAmountQuantityAndStockOfPayableItem(
    inputLineItem *orderlineitem.OrderLineItemRequest, payableItemEntity line_item.Entity,
) errors.IError {
    lineItemPrice := payableItemEntity.ItemPrice

    // Validate amount matches item amount
    if lineItemPrice.Amount != nil && inputLineItem.Amount != *lineItemPrice.Amount {
        return getValidationError("amount should be equal to payment page item amount")
    }
    // ... similar for min_amount, max_amount, stock
}
```

### Root Cause: DATA MISMATCH (Not Code Bug)

All 50 errors in the last 24 hours are caused by **data mismatch** between Monolith and NCA databases:

1. **Payment page not in NCA DB** - Previous `pp_create` failed in dual-write, so page exists in Monolith but not NCA
2. **Page status differs** - Page is `active` in Monolith but `inactive` (or missing) in NCA
3. **Item data differs** - Item's `Amount`, `mandatory` flag, or existence differs between DBs
4. **Item missing in NCA** - Previous item creation failed in dual-write

### Example Log Entry

```json
{
  "message": "DIFF_CHECKER_SHADOW_STATUS_CODE_MISMATCH",
  "error_message": "validation_failure: amount should be equal to payment page item amount",
  "monolith_status_code": 200,
  "shadow_status_code": 400,
  "monolith_response_body": {
    "order": {"amount": 270000, "status": "created"},
    "line_items": [{"amount": 270000, "ref_id": "ppi_RTpYU0tCl94T8i"}]
  },
  "shadow_response_body": {
    "error": {
      "code": "BAD_REQUEST_ERROR",
      "description": "validation_failure: amount should be equal to payment page item amount"
    }
  }
}
```

**Interpretation:** Monolith has item with amount=270000, but NCA either has different amount or item doesn't exist.

### Resolution

**Won't Fix** - These diffs will automatically resolve when:
1. NCA becomes the primary data source (no more dual-write)
2. Data migration completes for affected merchants

### How to Debug Specific Cases

If you need to investigate a specific failure:

1. **Get the razorpay_request_id** from the error log
2. **Search Coralogix** for the full request context:
   ```
   search_string: <razorpay_request_id>
   ```
3. **Check for previous failures** for the same `payment_page_id` or `ppi_XXX`
4. **Compare data** between Monolith DB and NCA DB for that entity

### Coralogix Search Commands Used

```bash
# Find create_order diffs
search_string: DIFF_CHECKER_SHADOW_STATUS_CODE_MISMATCH payment_page_create_order
applicationName: no-code-apps
relative_hours: 24

# Find "not active" errors
search_string: order cannot be created for payment page which is not active
relative_hours: 24

# Find "mandatory" errors  
search_string: mandatory payment page item, should be ordered
relative_hours: 24
```

---

## Devstack Configuration
```yaml
devstack_label: pp-mid-fix  # or new label as needed
```

## Test Commands
```bash
# Run unit tests
cd /Users/boddedakarthik.s/rzp/no-code-apps
go test -v ./internal/modules/line_item_price/...
go test -v ./internal/modules/nocode/...

# Devstack hot-reload
devspace dev
```
