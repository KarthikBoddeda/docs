# Topic: Go time.Duration Overflow

## Definition

`time.Duration` in Go is a type alias for `int64`, representing nanoseconds. Because it's a signed 64-bit integer, it can overflow **silently** — Go does not panic or error on integer overflow.

## The Type

```go
// From the Go standard library
type Duration int64

const (
    Nanosecond  Duration = 1
    Microsecond          = 1000 * Nanosecond
    Millisecond          = 1000 * Microsecond
    Second               = 1000 * Millisecond  // = 1,000,000,000
    Minute               = 60 * Second
    Hour                 = 60 * Minute
)
```

## Maximum representable duration

```
int64 max = 9,223,372,036,854,775,807 nanoseconds
          ≈ 292.47 years
```

This seems like plenty — until you start multiplying Durations together.

## The Double-Multiplication Trap

The most common overflow scenario:

```go
// Config gives you seconds as an int
timeoutSec := 30

// First conversion: correct
timeout := time.Duration(timeoutSec) * time.Second  // 30 seconds ✓

// Later in the code, someone "converts" again:
actualTimeout := timeout * time.Second  // OVERFLOW!
// = 30,000,000,000 * 1,000,000,000
// = 30,000,000,000,000,000,000 > int64 max
// = wraps to NEGATIVE value
```

### Overflow table

| Expression | Value | Fits in int64? |
|---|---|---|
| `1 * time.Second * time.Second` | 1e18 ns (~31.7 years) | Barely yes |
| `9 * time.Second * time.Second` | 9e18 ns (~285 years) | Yes |
| `10 * time.Second * time.Second` | 1e19 ns | **No — overflow** |
| `30 * time.Second * time.Second` | 3e19 ns | **No — overflow** |

**Critical insight:** values 1-9 seconds don't overflow when doubled, but 10+ seconds do. This is why unit tests with small values pass but production (with realistic timeouts like 30s) fails.

## Why Go Doesn't Help You

Go's design philosophy: integer overflow is **defined behavior** (wraps around). Unlike Rust (which panics in debug mode) or Java (which also wraps but has `Math.addExact`), Go gives no indication that overflow occurred.

```go
var d time.Duration = math.MaxInt64
d += 1
// d is now math.MinInt64 (negative!) — no error, no panic
```

## Detection

You can't detect overflow after the fact (the value just looks like a normal negative number). Instead, **prevent it**:

```go
// Defensive check before multiplication
func safeDuration(seconds int64) time.Duration {
    if seconds > int64(math.MaxInt64/int64(time.Second)) {
        return time.Duration(math.MaxInt64) // cap at max
    }
    return time.Duration(seconds) * time.Second
}
```

## Related

- [Safe Duration construction patterns](./go_time_duration_safe_construction_patterns.md)
- [Story: FTS Negative Timeout Overflow](/learnings/stories/fts-negative-timeout-overflow.md)
