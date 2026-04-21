# Unit Test Coverage Gaps

**Created:** 2026-01-14

## Overview
This task tracks remaining uncovered lines in the PR diff that need unit test coverage.

**Priority**: Medium  
**Type**: Testing  
**Status**: In Progress

---

## Subtasks

### 1. Settings.ValidateForUpdate Error Paths
**File**: `internal/modules/nocode/validation.go`  
**Status**: 🟢 Done (98.4% coverage)

Cover the error return paths for Settings.ValidateForUpdate(). Currently tests cover happy paths, but need to trigger validation failures for:
- Invalid theme value
- Invalid UDF schema JSON / max items exceeded (>15)
- Invalid boolean fields (AllowMultipleUnits, AllowSocialShare, FB events, EnableReceipt)
- Invalid URL format for PaymentSuccessRedirectUrl
- Invalid email format for SupportEmail
- Length violations for PaymentButtonLabel (>20), PaymentButtonText (>16), pixel tracking IDs (>32)
- PaymentSuccessMessage with emoji (UTF8MB3 failure)

<details>
<summary><b>Uncovered Lines</b></summary>

```
Line 191: return utils.GetValidationError(err)
Line 210: if n.wasSlugExplicitlyProvided() {
Line 222: validation.Key(SlugKey, slugValidationRules...),
Line 241: if customDomain != "" {
Line 242: if slugInf == nil {
Line 245: val := fmt.Sprint(slugInf)
Line 246: if val == "" {
Line 250: return ValidateSlugRegex(val)
Line 451: const MaxUdfSchemaItems = 15
Line 452: if len(*udfSchemaStruct) > MaxUdfSchemaItems {
Line 472: func (s *Settings) ValidateForUpdate() error {
Line 474: if s.Theme != nil {
Line 475: if err := validation.Validate(s.Theme, validation.By(s.validateTheme)); err != nil {
Line 481: if s.UdfSchema != nil {
Line 482: if err := validation.Validate(s.UdfSchema, is.JSON.Error(...)); err != nil {
Line 486: udfSchemaStruct, err := GetUdfSchemaFromString(*s.UdfSchema)
Line 487: if err != nil {
Line 490: const MaxUdfSchemaItems = 15
Line 491: if len(*udfSchemaStruct) > MaxUdfSchemaItems {
Line 494: for _, field := range *udfSchemaStruct {
Line 495: if err := field.Validate(); err != nil {
Line 502: if s.AllowMultipleUnits != nil {
Line 503: if err := validation.Validate(s.AllowMultipleUnits, validation.By(s.validateSettingsBool)); err != nil {
Line 509: if s.AllowSocialShare != nil {
Line 510: if err := validation.Validate(s.AllowSocialShare, validation.By(s.validateSettingsBool)); err != nil {
Line 516: if s.PaymentSuccessRedirectUrl != nil && *s.PaymentSuccessRedirectUrl != "" {
Line 517: if err := validation.Validate(s.PaymentSuccessRedirectUrl, is.URL); err != nil {
Line 523: if s.PaymentSuccessMessage != nil && *s.PaymentSuccessMessage != "" {
Line 524: if err := validation.Validate(s.PaymentSuccessMessage, validation.Length(5, 2048), extended_validation.Utf8MB3...); err != nil {
Line 530: if s.PaymentButtonLabel != nil {
Line 531: if err := validation.Validate(s.PaymentButtonLabel, validation.Length(0, 20)); err != nil {
Line 537: if s.PaymentButtonTheme != nil {
Line 538: if err := validation.Validate(s.PaymentButtonTheme, validation.Length(0, 32)); err != nil {
Line 544: if s.PaymentButtonText != nil {
Line 545: if err := validation.Validate(s.PaymentButtonText, validation.Length(0, 16)); err != nil {
Line 551: if s.PaymentButtonTemplateType != nil {
Line 552: if err := validation.Validate(s.PaymentButtonTemplateType, validation.Length(0, 32)); err != nil {
Line 558: if s.FbPixelTrackingId != nil {
Line 559: if err := validation.Validate(s.FbPixelTrackingId, validation.Length(0, 32)); err != nil {
Line 565: if s.GaPixelTrackingId != nil {
Line 566: if err := validation.Validate(s.GaPixelTrackingId, validation.Length(0, 32)); err != nil {
Line 572: if s.FbEventAddToCartEnabled != nil {
Line 573: if err := validation.Validate(s.FbEventAddToCartEnabled, validation.By(s.validateSettingsBool)); err != nil {
Line 579: if s.FbEventInitiatePaymentEnabled != nil {
Line 580: if err := validation.Validate(s.FbEventInitiatePaymentEnabled, validation.By(s.validateSettingsBool)); err != nil {
Line 586: if s.FbEventPaymentCompletedEnabled != nil {
Line 587: if err := validation.Validate(s.FbEventPaymentCompletedEnabled, validation.By(s.validateSettingsBool)); err != nil {
Line 593: if s.EnableReceipt != nil {
Line 594: if err := validation.Validate(s.EnableReceipt, validation.By(s.validateSettingsBool)); err != nil {
Line 600: if s.SupportEmail != nil && *s.SupportEmail != "" {
Line 601: if err := validation.Validate(s.SupportEmail, is.EmailFormat); err != nil {
Line 606: return nil
```

</details>

---

### 2. MaxUInt32 Boundary Validation
**File**: `internal/modules/line_item_price/validation.go`  
**Status**: 🟢 Done (86.2% coverage)

Add tests for MySQL unsigned int overflow checks:
- MaxAmount > 4294967295
- MinAmount > 4294967295  
- Amount > 4294967295
- MinUnits > 4294967295
- MaxUnits > 4294967295
- AvailableUnits > 4294967295

These protect against values exceeding MySQL's unsigned int limit.

<details>
<summary><b>Uncovered Lines</b></summary>

```
Line 122: if m.MaxAmount != nil && *m.MaxAmount > MaxUInt32 {
Line 125: if m.MinAmount != nil && *m.MinAmount > MaxUInt32 {
Line 128: if m.Amount != nil && *m.Amount > MaxUInt32 {
Line 131: if m.MinUnits != nil && *m.MinUnits > MaxUInt32 {
Line 134: if m.MaxUnits != nil && *m.MaxUnits > MaxUInt32 {
Line 137: if m.AvailableUnits != nil && *m.AvailableUnits > MaxUInt32 {
```

</details>

---

### 3. MonolithItemSettings.UnmarshalJSON All Branches
**File**: `internal/modules/nocode/request.go`  
**Status**: 🟢 Done (100% coverage)

All JSON unmarshaling branches are now covered:
- Empty array `[]` input ✅
- Empty string `""` input ✅
- Invalid JSON (malformed) - lenient handling ✅
- Position as float64 (number) ✅
- Position as string with valid number ✅
- Position as string with invalid number (non-numeric) ✅
- Position as empty string ✅
- Missing position key ✅

<details>
<summary><b>Originally Uncovered Lines (Now Covered)</b></summary>

```
Line 175: strData := string(data)
Line 181: }
Line 195: var rawMap map[string]interface{}
Line 200: }
Line 203: if posVal, ok := rawMap["position"]; ok && posVal != nil {
Line 211: if err == nil {
Line 215: }
```

</details>

---

### 4. Slug and UDF Schema Validation
**File**: `internal/modules/nocode/validation.go`  
**Status**: 🟢 Done

**Coverage Achieved:**
- `wasSlugExplicitlyProvided()`: **100%** ✅
- `ValidateSlugWithCustomDomain()`: **100%** ✅
- `ValidateSlugRegex()`: **87.5%** ✅

All key slug validation paths covered:
- Custom domain with nil slug ✅
- Custom domain with empty slug ✅
- Custom domain with invalid slug format ✅
- No custom domain scenarios ✅
- Slug regex validation (alphanumeric, special chars) ✅

UDF schema validation (>15 items) covered in Task 1.

<details>
<summary><b>Uncovered Lines</b></summary>

```
Line 210: if n.wasSlugExplicitlyProvided() {
Line 222: validation.Key(SlugKey, slugValidationRules...),
Line 241: if customDomain != "" {
Line 242: if slugInf == nil {
Line 245: val := fmt.Sprint(slugInf)
Line 246: if val == "" {
Line 250: return ValidateSlugRegex(val)
Line 451: const MaxUdfSchemaItems = 15
Line 452: if len(*udfSchemaStruct) > MaxUdfSchemaItems {
Line 486: udfSchemaStruct, err := GetUdfSchemaFromString(*s.UdfSchema)
Line 487: if err != nil {
Line 490: const MaxUdfSchemaItems = 15
Line 491: if len(*udfSchemaStruct) > MaxUdfSchemaItems {
Line 494: for _, field := range *udfSchemaStruct {
Line 495: if err := field.Validate(); err != nil {
```

</details>

---

### 5. ValidateEmptyStringForIntegerFields
**File**: `internal/modules/nocode/validation.go`  
**Status**: 🟢 Done (100% coverage)

PHP `empty("0")` quirk validation is fully covered:
- min_amount as string "0" ✅
- max_amount as string "0" ✅
- min_purchase as string "0" ✅
- max_purchase as string "0" ✅
- stock as string "0" ✅

All fields correctly reject string "0" matching monolith's behavior.

<details>
<summary><b>Originally Uncovered Lines (Now Covered)</b></summary>

```
Line 754: if n.MonolithPaymentPageItems != nil {
Line 755: for _, item := range *n.MonolithPaymentPageItems {
Line 769: func (item *MonolithPaymentPageItem) ValidateEmptyStringForIntegerFields() errors.IError {
Line 772: }
Line 775: }
Line 778: }
Line 781: }
Line 784: }
Line 855: for _, item := range *n.MonolithPaymentPageItems {
```

</details>

---

### 6. Extended Validation Remaining Branches
**Files**: 
- `internal/utils/extended_validation/custom_rules.go`
- `internal/utils/extended_validation/init.go`  
**Status**: 🟢 Done

**Coverage Achieved**:
- `isValidKeyValueNotes`: **100%** ✅
  - Empty array `[]interface{}{}` branch ✅
  - Non-empty array branch ✅
  - JSONMap type branch ✅
- `isValidContactNumberSyntax`: **76.2%** (key branches covered)
  - Plus sign not at start ✅
  - Non-digit characters ✅
  - Remaining uncovered: libphonenumber edge cases (integration-level)
- `IsValidUtf8MB3`: **100%** ✅
- `ValidateEmptyStringForInteger`: **100%** ✅

<details>
<summary><b>Tests Added</b></summary>

```go
// custom_rules_test.go - Test_ValidateKeyValueNotes_InterfaceTypes
- "empty array is valid (monolith format)"
- "non-empty array is invalid" 
- "array with single element is invalid"
- "JSONMap is valid"  // NEW - covers line 63-64
- "empty JSONMap is valid"  // NEW

// custom_rules_test.go - Test_ValidateContactNumberSyntax_EdgeCases
- "plus sign in middle is invalid"  // covers line 93
- "letters in number is invalid"  // covers line 97
- "special characters are invalid"
```

</details>

---

### 7. Dual Write Nil Item Handling
**File**: `internal/modules/payment_page/dual_write.go`  
**Status**: 🟢 Done

**Coverage Achieved**:
- `getResponsePPItemKey`: **100%** ✅
- `EmbedMonolithItemIdsInCreateItemRequests`: **77.3%** (key branches covered)
- `EmbedMonolithIdsIntoCreateOrderRequest`: **62.1%** (line 445 now covered)

All key nil item handling branches are covered:
- nil Item returns empty key ✅
- Empty key causes item to be skipped ✅ (line 162)
- Effective response count with skipped items ✅ (line 182-183)
- Empty response line items warning ✅ (line 445)

<details>
<summary><b>Tests Added</b></summary>

```go
// dual_write_nil_items_test.go
- TestGetResponsePPItemKey_NilItem
  - "nil_item_returns_empty_key" ✅
  - "valid_item_returns_composite_key" ✅
  
- TestEmbedMonolithItemIdsInCreateItemRequests_NilItems
  - "single_nil_item_in_response_skipped" ✅
  - "all_items_nil_causes_count_mismatch" ✅
  - "empty_request_with_nil_response_items_ok" ✅
  - "mixed_valid_and_nil_items_matched_correctly" ✅

- TestCountMismatchWithNilItems
  - "request_count_exceeds_effective_response_count" ✅
  - "request_count_equal_to_effective_response_count" ✅
  - "request_count_less_than_effective_response_errors_for_leftover" ✅

- TestEmbedMonolithIdsIntoCreateOrderRequest_EmptyLineItems  // NEW
  - "empty_response_line_items_with_request_items_returns_nil" ✅ (covers line 445)
  - "empty_request_and_response_line_items" ✅
```

</details>

---

### 8. Numeric Datatypes Edge Cases
**File**: `pkg/datatypes/numeric.go`  
**Status**: 🟢 Done (97.6% coverage)

Unmarshal branches are covered:
- `NumericInt64Value.UnmarshalJSON`: 100% ✅
- `NumericUInt64Value.UnmarshalJSON`: 93.8% ✅
- `IsStringZero()`: 100% ✅

Remaining 6.2% is edge case in error path - acceptable coverage.

<details>
<summary><b>Originally Uncovered Lines (Mostly Covered)</b></summary>

```
Line 47: var intVal int64
Line 54: var strVal string
Line 56: parsedInt, err := strconv.ParseInt(strVal, 10, 64)
Line 59: }
Line 78: isStringZero bool // true if value came from string "0" (for validation)
Line 94: if strVal == "" {
Line 95: return fmt.Errorf("invalid numeric string: empty")
```

</details>

---

### 9. GoalTracker and Settings Helpers
**Files**:
- `internal/modules/nocode/settings.go`
- `internal/modules/nocode/request.go`  
**Status**: 🟢 Done (100% coverage)

All helper functions are fully covered:
- `GoalTracker.IsEmpty()`: 100% ✅
- `GroupedConfigs.GetVersion()`: 100% ✅
- `WasExpireByExplicitlyProvided()`: 100% ✅
- `wasSlugExplicitlyProvided()`: 100% ✅
- `GetNotes()` (request.go:388): 100% ✅
- `GetNotesAsMap()` (order.go, payment_page/request.go): 100% ✅

<details>
<summary><b>Originally Uncovered Lines (Now Covered)</b></summary>

```
# settings.go
Line 92: func (g *GoalTracker) IsEmpty() bool {
Line 93: if g == nil {
Line 96: return g.TrackerType == nil && g.IsActive == nil && g.MetaData == nil
Line 163: func (gc *GroupedConfigs) GetVersion() string {
Line 164: if gc.BaseConfig == nil || gc.BaseConfig.Version == nil {
Line 167: return *gc.BaseConfig.Version

# request.go
Line 352: func (n *NocodeRequest) WasExpireByExplicitlyProvided() bool {
Line 353: if n.noCodeRequestMap == nil {
Line 357: _, exists := n.noCodeRequestMap["expire_by"]
Line 363: func (n *NocodeRequest) wasSlugExplicitlyProvided() bool {
Line 364: if n.noCodeRequestMap == nil {
Line 368: _, exists := n.noCodeRequestMap["slug"]
Line 397: }
Line 401: }
Line 446: if ppi.MonolithItemSettings != nil {
Line 455: Position: position,

# order.go
Line 44: }
Line 48: func (o *Order) GetNotesAsMap() map[string]interface{} {

# payment_page/request.go
Line 94: func (n *PaymentPageCreateOrderRequest) GetNotesAsMap() map[string]interface{} {
Line 99: switch v := n.Notes.(type) {
Line 101: return v
Line 108: return nil
```

</details>

---

### 10. Integration-Heavy Paths (Done)
**Files**:
- `internal/modules/payment_page/core.go`
- `internal/modules/image/core.go`
- `internal/modules/line_item/core.go`
- `internal/monolith_decomp/diffs/comparator.go`
- `internal/monolith_decomp/diffs/diff_checker.go`
- `internal/monolith_decomp/dual_write_handlers/base.go`
- `internal/modules/payment_page/monolith_dual_write.go`
- `internal/modules/payment_page/validation.go`  
**Status**: 🟢 Done

**Coverage Achieved:**
- `validation.go` (payment_page):
  - `validateShouldActivationBeAllowed`: **100%** ✅ (stock exhaustion + expire_by validation)
  - `isTimesPayableExhausted`: **100%** ✅
  - `isStockAvailable`: **100%** ✅
  - `MIN_EXPIRY_SECS` constant verified ✅
- `diff_checker.go`:
  - `tryGettingViewTypeFromSuccessfulMonolithResponseMap`: **100%** ✅
  - `tryGettingViewTypeFromMonolithHeaders`: **100%** ✅
  - `isSuccessResponse`: **100%** ✅ (with mocks for HTML/JSON responses)
  - `getViewTypeFromMonolithResponse`: **95.2%** ✅ (with ProxyResponse mocking)
  - `shouldIgnoreDiff`: **95.0%** ✅ (with error class mocking)
- `comparator.go`:
  - `filterSkipPathMatches`: **97.1%** ✅ (diff normalization paths)
  - `sortArraysByKeys`: **100%** ✅
  - `sortTargetArrayByKeyRecursive`: **100%** ✅
  - `sortArrayByKey`: **92.3%** ✅
- `validation.go` (nocode):
  - `ValidateSlugRegex`: **87.5%** ✅
  - `ValidateSlugWithCustomDomain`: **100%** ✅
- `image/core.go`:
  - `UpdateExistingEntity`: **100%** ✅
  - `UpdateExistingEntityWithValidator`: **66.7%** ✅
  - `getUpdateParamsList`: **87.5%** ✅

**Remaining (deferred to integration tests):**
- `HandleComparisonAndSendMetrics` - orchestrates entire comparison flow with metrics
- `payment_page/core.go` business logic - requires full database mocks
- `line_item/core.go` line 296 - requires image module dependencies
- `dual_write_handlers/base.go` line 75 - requires metrics infrastructure

**Note**: The remaining uncovered functions are deeply integrated with external systems (database, metrics, HTTP handlers) and are best covered via integration tests or shadow traffic validation.

<details>
<summary><b>Uncovered Lines</b></summary>

```
# payment_page/core.go
Line 668: if _, ok = settingsMap["position"]; ok {
Line 1050: if req.WasExpireByExplicitlyProvided() {
Line 1055: }
Line 1645: if er := req.ValidateForUpdate(); er != nil {
Line 1866: if metaData.GoalEndTimestamp != nil {
Line 1874: now := time.Now().Unix()
Line 1900: "paymentPageId": paymentPageEntity.GetID(),
Line 1904: logger.CtxLog(ctx).WithError(err).Error("GOAL_TRACKER_CREATE_FAILED")
Line 1905: return err
Line 1911: }
Line 2574: order.SetNotes(req.GetNotesAsMap())
Line 2597: Notes: req.GetNotesAsMap(),
Line 2735: if settings.GoalTracker.MetaData != nil && settings.GoalTracker.MetaData.GoalAmount != nil {
Line 2748: if settings.GoalTracker.MetaData != nil && settings.GoalTracker.MetaData.GoalEndTimestamp != nil {
Line 2749: endsBy = settings.GoalTracker.MetaData.GoalEndTimestamp.Value
Line 2756: displayDaysLeft = utils.SafeString(settings.GoalTracker.MetaData.DisplayDaysLeft)
Line 2773: DisplaySupporterCount: displaySupporterCount,
Line 2775: DisplaySoldUnits: displaySoldUnits,
Line 3182: PaymentPage: c.getPaymentPageDetailsForHosted(ctx, paymentPageEntity, merchantDetails),
Line 3632: SupportMobile: converters.StringToStringPtrWhereEmptyIsNil(merchantSupportDetails.SupportMobile),
Line 3666: func (c *PaymentPageCore) getPaymentPageDetailsForHosted(...)
Line 3686: } else {
Line 3709: paymentPageDetailsForHosted.UserId = nil

# payment_page/monolith_dual_write.go
Line 181: TotalAmountPaid: uint64(utils2.SafeInt64(resp.TotalAmountPaid)),

# payment_page/validation.go
Line 435: message := "at least one of the payment page item's stock should be left to activate payment page"
Line 448: minExpireBy := currentTime + MIN_EXPIRY_SECS

# image/core.go
Line 141: return c.UpdateExistingEntityWithValidator(ctx, entity, GenericImageValidator)
Line 147: func (c *Core) UpdateExistingEntityWithValidator(...)
Line 157: if er := validator(entity); er != nil {

# line_item/core.go
Line 296: if err := image.ImgModule.GetCore().UpdateExistingEntityWithValidator(...)

# monolith_decomp/diffs/comparator.go
Line 210: if diff.Path == "/description" && diff.OldValue == nil {
Line 214: if diff.Path == "/merchant/support_mobile" && diff.OldValue == "" {
Line 218: if diff.Path == "/payment_link/settings/selected_udf_field" && diff.OldValue == "" {
Line 222: if diff.Path == "/payment_link/description" && diff.OldValue == nil {
Line 226: if itemPositionRegex.MatchString(diff.Path) && diff.OldValue == nil {

# monolith_decomp/diffs/diff_checker.go
Line 138: if comparatorConfig.IsHtmlResponse {

# monolith_decomp/dual_write_handlers/base.go
Line 75: metrics.UnexpectedErrorCounter.WithLabelValues(routeName, "diff_checker_error", err.Error()).Inc()

# utils/init.go (NOW COVERED)
Line 414: func SafeInt64(s *int64) int64 {
Line 415: if s == nil {
Line 418: return *s
```

</details>

---

## Progress Tracker

| Subtask | Status | Notes |
|---------|--------|-------|
| 1. Settings.ValidateForUpdate Error Paths | 🟢 | **98.4% covered** |
| 2. MaxUInt32 Boundary Validation | 🟢 | **86.2% covered** |
| 3. MonolithItemSettings.UnmarshalJSON | 🟢 | **100% covered** |
| 4. Slug and UDF Schema Validation | 🟢 | **ValidateSlugWithCustomDomain=100%, ValidateSlugRegex=87.5%** |
| 5. ValidateEmptyStringForIntegerFields | 🟢 | **100% covered** |
| 6. Extended Validation Remaining | 🟢 | **isValidKeyValueNotes=100%, key branches covered** |
| 7. Dual Write Nil Item Handling | 🟢 | **Key branches covered, line 445 added** |
| 8. Numeric Datatypes Edge Cases | 🟢 | **97.6% covered** |
| 9. GoalTracker and Settings Helpers | 🟢 | **100% covered** |
| 10. Integration-Heavy Paths | 🟢 | **Done** - validation 100%, diff_checker 95-100%, comparator 92-100%, image 66-100% |

---

## Notes
- Subtasks 1-9 are unit-testable without major infrastructure changes
- Subtask 10 requires mocking infrastructure or should be covered by shadow traffic validation
- Focus on covering validation error paths first (subtasks 1, 2, 4) as they protect against breaking changes
