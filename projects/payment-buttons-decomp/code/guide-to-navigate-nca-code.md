# Guide to Navigate NCA (No-Code-Apps) Code

This guide covers common patterns, utilities, and gotchas in the NCA codebase that you should be aware of before writing or debugging code.

---

## 1. Numeric Types for Flexible JSON Parsing

The monolith (PHP) is flexible with types - it often accepts both strings and integers for numeric fields. NCA (Go) is strict about types, which can cause `json.Unmarshal` to fail silently.

### The Problem

```go
// ❌ BAD: If JSON sends "1768501799" (string), this fails silently
type MyStruct struct {
    Timestamp *int64 `json:"timestamp"`
}
```

### The Solution: Use `datatypes.Numeric*Value` types

Located in `pkg/datatypes/numeric.go`:

```go
import "github.com/razorpay/no-code-apps/pkg/datatypes"

// ✅ GOOD: Handles both string and integer from JSON
type MyStruct struct {
    Timestamp *datatypes.NumericInt64Value `json:"timestamp"`
}
```

### Available Types

| Type | Use Case | Example JSON Values |
|------|----------|---------------------|
| `NumericIntValue` | int values | `123`, `"123"` |
| `NumericInt64Value` | int64 (timestamps) | `1768501799`, `"1768501799"` |
| `NumericUInt64Value` | uint64 values | `999999`, `"999999"` |

### Accessing the Value

```go
if myStruct.Timestamp != nil {
    actualValue := myStruct.Timestamp.Value  // int64
}
```

---

## 2. Debug Logging

When debugging, add `fmt.Println` or `fmt.Printf` statements to trace values:

```go
import "fmt"

// Add debug logging to trace values
fmt.Printf("DEBUG: GoalTracker = %+v\n", settings.GoalTracker)
fmt.Printf("DEBUG: TrackerType = %v (nil=%v)\n", settings.GoalTracker.TrackerType, settings.GoalTracker.TrackerType == nil)
```

**⚠️ IMPORTANT:** Always remove debug logs before committing! They pollute production logs.

---

## 3. MapToStruct and JSON Parsing

`utils.MapToStruct` is used to convert `map[string]interface{}` to structs:

```go
var settings Settings
err := utils.MapToStruct(n.Settings, &settings)
```

**Gotcha:** If any nested field fails to parse (e.g., type mismatch), the error is returned but the struct is partially populated. This can cause confusing nil pointer issues.

**Debug tip:** Always check the error:
```go
err := utils.MapToStruct(n.Settings, &settings)
if err != nil {
    fmt.Printf("DEBUG: MapToStruct error = %v\n", err)
}
```

---

## 4. Common Struct Patterns

### Pointer Fields for Optional Values

```go
type Settings struct {
    Theme *string `json:"theme"`  // nil if not provided
}

// Check before use
if settings.Theme != nil {
    actualTheme := *settings.Theme
}
```

### IsEmpty Pattern for Empty Objects

When monolith skips validation for empty objects (e.g., `goal_tracker: {}`), use this pattern:

```go
func (g *GoalTracker) IsEmpty() bool {
    if g == nil {
        return true
    }
    return g.TrackerType == nil && g.IsActive == nil && g.MetaData == nil
}
```

---

## 5. Error Classes

Use the appropriate error class from `pkg/errorclass`:

```go
import "github.com/razorpay/no-code-apps/pkg/errorclass"

// Validation failure (400)
return errorclass.ErrValidationFailure.New("The field is required.")

// Decode failure (400)
return errorclass.ErrDecodeFailure.New("Failed to parse JSON")

// Internal error (500)
return errorclass.ErrInternalServerError.New("Something went wrong")
```

---

## 6. Key Files Reference

| Area | File Path |
|------|-----------|
| Numeric types | `pkg/datatypes/numeric.go` |
| Settings struct | `internal/modules/nocode/settings.go` |
| Validation | `internal/modules/nocode/validation.go` |
| Request parsing | `internal/modules/nocode/request.go` |
| Payment Page core | `internal/modules/payment_page/core.go` |
| Utility functions | `internal/utils/` |

---

## 7. Before Writing Code Checklist

- [ ] Check if a similar pattern already exists in the codebase
- [ ] Use `datatypes.Numeric*Value` for fields that monolith accepts as string/int
- [ ] Add nil checks for pointer fields
- [ ] Test with actual production request from Coralogix (don't guess payloads)
- [ ] Add debug logs while developing (remove before commit)

## 8. After Writing Code Checklist

- [ ] **Add unit tests** for new utility functions/types (see `pkg/datatypes/numeric_test.go` for examples)
- [ ] Run `go test ./...` to ensure no regressions
- [ ] Remove debug logs before commit
- [ ] Test at least 4 requests:
  - TC1: Request from one date file (e.g., `2025-12-29.csv`)
  - TC2: Different request from same diff type (e.g., `2025-12-28.csv`)
  - TC3: Another request from same diff type (different date/entry)
  - TC4: Standard request from `payment-pages-api.http` (regression test)

