# PR Review Action Items

This task tracks all action items identified during PR review for the Payment Pages Decomposition changes.

## Status Legend
- ⬜ Not Started
- 🟡 In Progress  
- ✅ Completed
- ❌ Won't Fix

---

## 🚨 CRITICAL - Must Remove Before Merge

| # | Subtask | Status | Notes |
|---|---------|--------|-------|
| 1 | Remove currency validation bypass in `internal/modules/payment_page/core.go:1017-1021` | ⬜ | `ValidateCurrency` returns nil unconditionally - marked "DO NOT COMMIT" |
| 2 | Restore `PassportPrivateAuth()` middleware in `internal/router/payment_page_private_routes.go` | ⬜ | Auth middleware commented out - marked "BYPASSED for devstack testing" |

---

## ⚠️ Potential Nil Pointer Fix

| # | Subtask | Status | Notes |
|---|---------|--------|-------|
| 3 | Fix `NocodeRequest.GetNotes()` panic risk in `internal/modules/nocode/request.go:390-406` | ⬜ | Final fallback `return n.Notes.(map[string]interface{})` can panic if Notes is unexpected type. Add default case returning nil. |

---

## 🔍 Code Review Items

| # | Subtask | Status | Notes |
|---|---------|--------|-------|
| 4 | Verify error class change impact: `ErrorNCANotSupported` and `ErrorSkippingDualWrite` changed from `RecoverableError` to `BadRequestError` | ⬜ | Check if this affects monitoring/alerting/metrics |

---

## 🧪 HIGH PRIORITY - Extensive Testing Required

| # | Subtask | Status | Notes |
|---|---------|--------|-------|
| 5 | Test UTF8MB3 validation (emoji rejection) for title, description, terms, payment_success_message | ⬜ | Test: emojis (🚀,🔐) reject; Japanese/Chinese chars accept; ₹ symbol accept |
| 6 | Test GoalTracker Create vs Update logic in `validateAndUpdateGoalTracker` | ⬜ | Test: update with/without existing goal_tracker; partial updates; goal_end_timestamp future validation |
| 7 | Test String "0" validation (`IsStringZero()`) for min_amount, max_amount, min_purchase, max_purchase, stock | ⬜ | Test: int 0 accept; string "0" reject; string "5" accept; null accept |
| 8 | Test `ValidateItemPrice` feature flag logic inversion | ⬜ | Changed from `IsEnableCustomerAmountEnabled()` to `!IsEnableCustomerAmountEnabled()` - verify matches monolith |

---

## 🧪 MEDIUM PRIORITY - Testing Required

| # | Subtask | Status | Notes |
|---|---------|--------|-------|
| 9 | Test Notes as `interface{}` type (was `map[string]interface{}`) | ⬜ | Test: empty object `{}`; empty array `[]`; normal map; null |
| 10 | Test `ValidateForUpdate` relaxation - removed settings.Validate(), terms length, support_contact validation | ⬜ | Test: short terms (<5 chars); invalid support_contact; settings that fail create validation |
| 11 | Test slug validation with `wasSlugExplicitlyProvided()` | ⬜ | Test: update page with short existing slug (e.g., "eng") without changing; explicit new slug |
| 12 | Test stock validation change - only validates when stock != 0 | ⬜ | Test: set stock to 0/null when items sold |
| 13 | Test dual write ID extraction with nil items | ⬜ | Test: create PP where monolith returns items with `item: null` |

---

## Test Case Details

### 5. UTF8MB3 Validation Test Cases
```http
# Should REJECT - contains 4-byte UTF-8 (emojis)
POST /payment_pages
{"title": "Test 🚀"}
{"title": "🔐 Secure Payment"}
{"description": "Get access 🎉"}

# Should ACCEPT - valid utf8mb3 (3-byte or less)
POST /payment_pages
{"title": "Test こんにちは"}
{"title": "Price: ₹1,999"}
{"title": "café résumé"}
```

### 6. GoalTracker Create vs Update Test Cases
```http
# TC1: Update page WITH existing goal_tracker - should UPDATE
PATCH /payment_pages/{id}
{"settings": {"goal_tracker": {"tracker_type": "donation_amount_based"}}}

# TC2: Update page WITHOUT existing goal_tracker - should CREATE
PATCH /payment_pages/{id}  # page has no goal_tracker
{"settings": {"goal_tracker": {"tracker_type": "donation_amount_based", "meta_data": {"goal_amount": "10000"}}}}

# TC3: Partial update preserving existing values
PATCH /payment_pages/{id}
{"settings": {"goal_tracker": {"is_active": "1"}}}

# TC4: goal_end_timestamp must be in future when is_active="1"
PATCH /payment_pages/{id}
{"settings": {"goal_tracker": {"is_active": "1", "meta_data": {"goal_end_timestamp": "1609459200"}}}}  # past timestamp - should reject
```

### 7. String "0" Validation Test Cases
```http
# Should ACCEPT - integer 0
POST /payment_pages
{"payment_page_items": [{"min_purchase": 0}]}

# Should REJECT - string "0"
POST /payment_pages
{"payment_page_items": [{"min_purchase": "0"}]}

# Should ACCEPT - string "5"
POST /payment_pages
{"payment_page_items": [{"min_purchase": "5"}]}

# Should ACCEPT - null
POST /payment_pages
{"payment_page_items": [{"min_purchase": null}]}
```

### 9. Notes as interface{} Test Cases
```http
# TC1: Empty object - should work
POST /payment_pages/{id}/order
{"notes": {}}

# TC2: Empty array (monolith format) - should work
POST /payment_pages/{id}/order
{"notes": []}

# TC3: Normal map - should work
POST /payment_pages/{id}/order
{"notes": {"key": "value"}}

# TC4: Null - should work
POST /payment_pages/{id}/order
{"notes": null}
```

---

## Files Modified in PR (Reference)

- `internal/modules/payment_page/core.go`
- `internal/modules/nocode/request.go`
- `internal/modules/nocode/validation.go`
- `internal/modules/nocode/settings.go`
- `internal/router/payment_page_private_routes.go`
- `internal/modules/line_item_price/validation.go`
- `internal/modules/goal_tracker/validation.go`
- `internal/utils/extended_validation/custom_rules.go`
- `internal/utils/extended_validation/init.go`
- `pkg/datatypes/numeric.go`
- `pkg/errorclass/errors.go`
- `internal/modules/payment_page/dual_write.go`
- `internal/monolith_decomp/diffs/comparator.go`
- `internal/monolith_decomp/diffs/configs.go`

---

## Completion Checklist

- [ ] All CRITICAL items (1-2) resolved
- [ ] Nil pointer fix (3) applied
- [ ] Code review item (4) verified
- [ ] HIGH priority tests (5-8) passed
- [ ] MEDIUM priority tests (9-13) passed
- [ ] PR approved

