# Topic: Safe Go time.Duration Construction Patterns

## The Problem

Go's `time.Duration` is `int64` nanoseconds. Multiplying durations together or applying `time.Second` twice causes silent integer overflow. See [time.Duration overflow](./go_time_duration_overflow.md).

## Safe Patterns

### Pattern 1: Convert raw int to Duration exactly once

```go
// Config gives you an int (seconds)
timeoutSec := viper.GetInt("webhook.timeout_seconds")

// Convert ONCE — never multiply a Duration by time.Second
timeout := time.Duration(timeoutSec) * time.Second
```

**Rule:** If the source is an `int` (seconds), multiply by `time.Second` once. If the source is already a `time.Duration`, don't multiply at all.

### Pattern 2: Use time.ParseDuration for string configs

```go
// Config: "30s", "5m", "100ms"
timeout, err := time.ParseDuration(viper.GetString("webhook.timeout"))
if err != nil {
    timeout = 30 * time.Second // fallback
}
```

**Advantage:** No manual multiplication, handles units automatically, returns an error for invalid values.

### Pattern 3: Type-check at the boundary

```go
// Make the type explicit in the function signature
func NewWebhookClient(timeout time.Duration) *Client {
    // timeout is already a Duration — never multiply by time.Second here
    return &Client{timeout: timeout}
}

// Caller converts:
client := NewWebhookClient(30 * time.Second)
```

**Rule:** Functions that accept `time.Duration` should never multiply by time units internally. The caller is responsible for conversion.

### Pattern 4: Constants for common durations

```go
const (
    defaultWebhookTimeout = 30 * time.Second
    maxRetryDelay         = 5 * time.Minute
    healthCheckInterval   = 10 * time.Second
)
```

**Advantage:** Multiplication happens at compile time with constants, so overflow would be caught by the compiler for unreasonable values.

## Anti-Patterns

### Never multiply Duration × Duration

```go
// BAD: time.Second is a Duration, timeout is a Duration
actualTimeout := timeout * time.Second  // Duration × Duration = overflow risk

// GOOD: timeout is already in the right units
actualTimeout := timeout
```

### Never re-convert an already-converted value

```go
// BAD: double conversion
d := time.Duration(seconds) * time.Second  // first conversion
d = d * time.Second                          // second conversion → overflow

// GOOD: convert once, use directly
d := time.Duration(seconds) * time.Second
```

### Beware of intermediate variables losing type info

```go
// Risky: 'val' is int64, but represents nanoseconds (a Duration)
val := config.GetInt64("timeout_ns")
// Later, someone thinks 'val' is seconds:
timeout := time.Duration(val) * time.Second  // WRONG if val is already nanoseconds
```

**Tip:** Name variables to include the unit: `timeoutSec`, `timeoutMs`, `timeoutDur`.

## Linting

Consider using `go vet` or custom linters to flag `Duration * Duration` expressions. The `durationcheck` linter specifically catches this:

```bash
go install github.com/charithe/durationcheck/cmd/durationcheck@latest
durationcheck ./...
```

## Related

- [time.Duration overflow](./go_time_duration_overflow.md)
- [Story: FTS Negative Timeout Overflow](/learnings/stories/fts-negative-timeout-overflow.md)
