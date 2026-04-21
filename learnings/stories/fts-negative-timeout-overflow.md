# The Negative Timeout Bug — When Go's time.Second Bites Twice

**Date:** March 2026
**Channel:** `#x-payouts-service`
**Thread:** [Original post](https://razorpay.slack.com/archives/C01698ACDD1/p1772687441080339)
**PR:** [razorpay/fts#4129](https://github.com/razorpay/fts/pull/4129/changes)

---

## STAR Summary

| | |
|---|---|
| **Situation** | FTS webhook timeout monitoring producing massive overflow and negative timeout values in production |
| **Task** | Find and fix the critical bug causing impossible timeout durations that broke monitoring |
| **Action** | Traced to a double multiplication by `time.Second` causing int64 overflow; surgical one-line fix plus comprehensive tests |
| **Result** | Bug fixed, UT coverage improved, error handling hardened |

---

## The Full Story

### What Happened

The Fund Transfer Service (FTS) team had recently added webhook timeout monitoring — a feature that tracks how long webhook deliveries take and alerts when they exceed thresholds. In production, the monitoring started reporting **impossible values**: timeouts of astronomical durations, and in some cases, **negative durations**.

Negative durations in a timeout system is a contradiction — it means the system thinks a timeout happened before the request even started.

### The Bug

Shivam Shah traced the issue to a deceptively simple bug:

```go
// The buggy code (conceptual)
timeout := configuredTimeoutSeconds * time.Second  // Step 1: convert to Duration
// ... later in the code ...
actualTimeout := timeout * time.Second              // Step 2: OOPS, multiplied again
```

In Go, `time.Second` is a `time.Duration` with the value `1,000,000,000` (nanoseconds). The code was multiplying by `time.Second` **twice**:

```
Intended:  30 * 1,000,000,000 = 30,000,000,000 ns = 30 seconds ✓

Actual:    30 * 1,000,000,000 * 1,000,000,000
         = 30,000,000,000,000,000,000 ns
         = 30 quintillion nanoseconds
         > int64 max (9,223,372,036,854,775,807)
         → INTEGER OVERFLOW → wraps to negative ✗
```

**Related learning:** [Go time.Duration overflow and multiplication pitfalls](/learnings/golang/time-and-duration/topics/go_time_duration_overflow.md)

### Why This Bug Survived Testing

The bug likely passed tests for several reasons:

1. **Small test values** — tests with timeout = 1 second: `1 * 1e9 * 1e9 = 1e18`, which is just barely under `int64` max. So unit tests with small values might not overflow.
2. **Unsigned comparison** — depending on how the timeout was checked, a negative duration might still "work" (comparing `elapsed > timeout` where timeout is negative always passes).
3. **The feature was new** — monitoring was just added, so there wasn't historical behavior to compare against.

### The Fix

Shivam's PR removed the duplicate multiplication and added:
- Comprehensive unit tests covering edge cases
- Improved error handling for webhook metric collection
- Defensive checks against invalid duration values

---

## Deep Dive: Go's `time.Duration` Type

This bug is a masterclass in why Go's `time` package requires careful handling.

### `time.Duration` is just an `int64`

```go
type Duration int64  // nanoseconds
```

It's signed, so it can be negative. And it can overflow silently — Go doesn't panic on integer overflow:

```go
var d time.Duration = math.MaxInt64
d += 1  // silently wraps to math.MinInt64 (negative!)
```

### The `time.Second` trap

`time.Second` is `1,000,000,000`. When you multiply:

| Expression | Result | Fits in int64? |
|---|---|---|
| `30 * time.Second` | 30s | Yes |
| `30 * time.Second * time.Second` | ~30 quintillion ns | **No — overflow** |
| `1 * time.Second * time.Second` | 1e18 ns (~31.7 years) | Barely yes |
| `10 * time.Second * time.Second` | 1e19 ns | **No — overflow** |

### How to avoid this

1. **Never multiply a Duration by a Duration** — if you find yourself doing `dur * time.Second`, the value is probably already a Duration
2. **Use `time.Duration(n) * time.Second`** for converting raw numbers
3. **Check types at assignment** — if the config gives you an `int`, multiply once. If it gives you `time.Duration`, don't multiply at all.

**Related learning:** [Safe patterns for Go time.Duration construction](/learnings/golang/time-and-duration/topics/go_time_duration_safe_construction_patterns.md)

---

## Why This Is Interesting

### 1. Silent integer overflow — the quietest disaster

Unlike null pointer dereferences or out-of-bounds panics, integer overflow in Go is **completely silent**. No panic, no error, no log. The value just wraps around. In a timeout context, this means the system thinks timeouts are negative or astronomically large — both of which break the intended behavior in different ways.

### 2. The "it works in tests" false confidence

This is a textbook case of **insufficient boundary testing**. The bug surfaces at specific numeric ranges (`timeout >= 10 seconds` when doubled). A test with `timeout = 1` would pass. This is why property-based testing and fuzzing are valuable — they explore the input space beyond the happy path.

### 3. Type safety as a feature, not a constraint

Go's `time.Duration` type system is actually trying to help. When you see `timeout * time.Second`, the type system allows it because Duration × Duration is a valid Go expression. A stricter type system (like Rust's) would prevent multiplying two Durations. The lesson: **just because the compiler allows it doesn't mean it's correct**.

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Integer overflow in Go** | Go silently wraps on overflow — no panic, no error. Always validate ranges for Duration math. |
| **time.Duration is nanoseconds** | `time.Second = 1e9`. Multiplying durations together creates values that overflow int64 surprisingly fast. |
| **Boundary testing** | Test with realistic production values, not just small test fixtures. A 30-second timeout behaves very differently from a 1-second timeout in overflow scenarios. |
| **Silent bugs in monitoring** | When monitoring itself is broken, you lose the ability to detect other issues. Monitoring systems deserve their own tests. |

---

## Key References

- [Original Slack thread (#x-payouts-service)](https://razorpay.slack.com/archives/C01698ACDD1/p1772687441080339)
- [PR: razorpay/fts#4129](https://github.com/razorpay/fts/pull/4129/changes)
