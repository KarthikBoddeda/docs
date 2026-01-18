# PR Review Action Items - Payment Pages Decomp

**PR Branch:** `pp-fixes` (no-code-apps)  
**Proxy State:** `dual_write_shadow_read`  
**Created:** 2026-01-10

---

## 🚨 CRITICAL - Must Remove Before Merge

| # | Item | File | Status | Notes |
|---|------|------|--------|-------|
| 1 | **Currency Validation Bypass** - `ValidateCurrency` returns nil immediately | `internal/modules/payment_page/core.go` | ⚠️ PENDING | DO NOT COMMIT - remove bypass |
| 2 | **Auth Middleware Bypass** - `PassportPrivateAuth()` commented out | `internal/router/payment_page_private_routes.go` | ⚠️ PENDING | Restore auth middleware |

---

## ⚠️ Nil Pointer Fixes

| # | Item | File | Status | UT Status | Notes |
|---|------|------|--------|-----------|-------|
| 3 | `NocodeRequest.GetNotes()` final fallback | `internal/modules/nocode/request.go` | ✅ DONE | ✅ DONE | Added handling for `nil`, `map`, `[]interface{}` |
| 4 | Ensure type assertion safety | Various | ✅ DONE | ✅ DONE | Covered in GetNotes tests |

---

## 🔍 Code Review

| # | Item | File | Status | Notes |
|---|------|------|--------|-------|
| 5 | Error Class Changes - `ErrorNCANotSupported`, `ErrorSkippingDualWrite` changed from `RecoverableError` to `BadRequestError` | `pkg/errorclass/errors.go` | 🔍 REVIEW | Verify this doesn't impact monitoring/alerting |

---

## 🧪 HIGH Priority Testing

| # | Item | File | Status | UT Status | Notes |
|---|------|------|--------|-----------|-------|
| 6 | UTF8MB3 Validation - `IsValidUtf8MB3` function | `internal/utils/extended_validation/custom_rules.go` | ✅ DONE | ✅ DONE | 53+ test cases added |
| 7 | GoalTracker Logic - `validateAndUpdateGoalTracker`, `HandleGoalTrackerCreation` | `internal/modules/payment_page/core.go` | ✅ DONE | ✅ DONE | 40+ test cases in `core_goal_tracker_test.go` |
| 8 | String "0" Validation - `IsStringZero()` and `ValidateEmptyStringForIntegerFields()` | `pkg/datatypes/numeric.go`, `internal/modules/nocode/validation.go` | ✅ DONE | ✅ DONE | 21+ test cases |
| 9 | ValidateItemPrice Feature Flag Logic | `internal/modules/payment_page/core.go` | ✅ DONE | ✅ DONE | 13 test cases in `core_unit_test.go` |
| 10 | Notes as `interface{}` Type Handling | `internal/modules/nocode/request.go` | ✅ DONE | ✅ DONE | 15 test cases in `request_test.go` |
| 11 | ValidateForUpdate Relaxations - Terms, SupportContact, Settings.Validate() | `internal/modules/nocode/validation.go` | ✅ DONE | ✅ DONE | 29 test cases in `validation_test.go` |
| 12 | Settings.ValidateForUpdate() - Field-level validation matching monolith | `internal/modules/nocode/validation.go` | ✅ DONE | ✅ DONE | 45+ test cases in `settings_test.go` |

---

## 🧪 MEDIUM Priority Testing

| # | Item | File | Status | UT Status | Notes |
|---|------|------|--------|-----------|-------|
| 13 | Slug Validation with `wasSlugExplicitlyProvided()` | `internal/modules/payment_page/core.go` | ⏳ PENDING | ⏳ PENDING | Test updating page with short existing slug |
| 14 | Stock Validation Change | `internal/modules/payment_page/core.go` | ✅ DONE | ⚠️ API TEST | See stock validation notes below |
| 15 | Dual Write ID Extraction with nil Items | `internal/modules/payment_page/dual_write.go` | ✅ DONE | ✅ DONE | 10 test cases in `dual_write_nil_items_test.go` |

---

## Devstack Testing Summary (2026-01-10)

**Devstack Label:** `pp-settings-val`
- **API:** ad2b19c17fc974d9b42c393205173e252fc73bbd
- **NCA:** 1cad8afc003aa5c2f5632f3dc814b39cb4dd9148

### Settings Validation Tests ✅

| Test | Input | Expected | Result |
|------|-------|----------|--------|
| Valid theme update | `theme: "dark"` | ✅ Success | ✅ PASS |
| Invalid theme | `theme: "blue"` | ❌ Error | ✅ PASS |
| button_text > 16 chars | 44 chars | ❌ Error | ✅ PASS |
| button_label > 20 chars | 52 chars | ❌ Error | ✅ PASS |
| Emoji in success_message | `...🎉` | ❌ Error (UTF8MB3) | ✅ PASS |
| Invalid URL | `not-a-url` | ❌ Error | ✅ PASS |
| Valid URL | `https://...` | ✅ Success | ✅ PASS |

**Test Page:** `pl_S2D7S9KfYBprUg` (Merchant: `LJ3P0FyFtOULha`)

---

## Key Implementation Notes

### ValidateForUpdate Relaxations
The following validations are intentionally relaxed on update to match monolith's Laravel validation behavior:

1. **Terms length validation (5, 2048)** - REMOVED on update
   - Monolith: `'nullable|string|min:5|max:2048|utf8'` with `sometimes` rule
   - NCA: Only validates UTF8MB3, not length

2. **SupportContact validation** - REMOVED on update
   - Monolith doesn't validate `support_contact` on update
   - NCA: Skipped entirely

3. **Settings.Validate()** - NOT called on update
   - Would validate ALL settings fields including existing DB data
   - NCA: Only validates fields explicitly present in request via `Settings.ValidateForUpdate()`

### Stock Validation Test Results (Task 14)

**Devstack Tests:**
| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| stock=null | ✅ Allowed | ✅ Allowed | ✅ PASS |
| stock=5 | ✅ Allowed | ✅ Allowed | ✅ PASS |
| stock=0 | ✅ Allowed (PHP empty()) | ❌ Rejected | ⚠️ INVESTIGATE |

**Issue Found:** `stock=0` is rejected by `line_item_price/validation.go:64-68` which has `MinUInt64Ptr(1)` validation.
The core.go stock validation (lines 744-755) correctly allows stock=0 due to PHP empty() behavior, but the entity validation rejects it.

**Action Required:** Verify if monolith allows stock=0. If yes, the `MinUInt64Ptr(1)` validation needs to be removed or changed to `Min(0)`.

### Dual Write Nil Items Test Results (Task 15)

**Unit Tests Added:** `dual_write_nil_items_test.go` with 10 test cases:
- `TestGetResponsePPItemKey_NilItem/nil_item_returns_empty_key` ✅
- `TestGetResponsePPItemKey_NilItem/valid_item_returns_composite_key` ✅
- `TestEmbedMonolithItemIdsInCreateItemRequests_NilItems/single_nil_item_in_response_skipped` ✅
- `TestEmbedMonolithItemIdsInCreateItemRequests_NilItems/all_items_nil_causes_count_mismatch` ✅
- `TestEmbedMonolithItemIdsInCreateItemRequests_NilItems/empty_request_with_nil_response_items_ok` ✅
- `TestEmbedMonolithItemIdsInCreateItemRequests_NilItems/mixed_valid_and_nil_items_matched_correctly` ✅
- `TestCountMismatchWithNilItems/request_count_exceeds_effective_response_count` ✅
- `TestCountMismatchWithNilItems/request_count_equal_to_effective_response_count` ✅
- `TestCountMismatchWithNilItems/request_count_less_than_effective_response_errors_for_leftover` ✅

**Behavior Verified:**
- When monolith returns items with `item: null`, they are skipped during ID extraction
- Count mismatch is checked against "effective" response count (excluding nil items)
- All response items must match request items (leftover items cause error)

### Settings.ValidateForUpdate() Rules (matching monolith editRules)

| Field | Rule |
|-------|------|
| `theme` | `in:light,dark` |
| `udf_schema` | valid JSON, max 15 items |
| `payment_success_redirect_url` | valid URL |
| `payment_success_message` | min:5, max:2048, UTF8MB3 |
| `payment_button_label` | max:20 |
| `payment_button_text` | max:**16** (not 20!) |
| `payment_button_theme` | max:32 |
| `fb_pixel_tracking_id` | max:32 |
| `ga_pixel_tracking_id` | max:32 |
| boolean fields | `in:0,1` |
| `support_email` | valid email |
