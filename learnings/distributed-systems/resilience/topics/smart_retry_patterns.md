# Topic: Smart Retry Patterns in Payment Systems

## Definition

**Smart retry** is a failure-aware retry strategy that classifies the type of failure and selects the optimal retry behavior (different path, different timing, or no retry at all), as opposed to "dumb retry" which blindly repeats the same request.

## Why Dumb Retry Is Dangerous in Payments

```
Payment fails → retry same gateway → fails again → retry again
                ↓
  If gateway is down: you're hammering a dead service
  If it was a transient error that partially succeeded:
    you might DOUBLE-CHARGE the customer
```

In payment systems, the cost of a wrong retry is:
- **Duplicate charges** — customer charged twice (refund required, trust damaged)
- **Thundering herd** — all clients retry simultaneously, overwhelming the recovering service
- **Cascading failure** — retries consume resources that could serve new requests

## Failure Classification

The key insight of smart retry: **not all failures are the same**.

| Failure Type | Example | Retry Strategy |
|---|---|---|
| **Transient** | Timeout, 503, connection reset | Retry same path with exponential backoff |
| **Path-level** | Gateway down, partner maintenance | Retry via **alternate gateway** |
| **Rate-limited** | 429 Too Many Requests | Backoff with jitter, respect `Retry-After` header |
| **Client error** | Invalid card number, bad request | **Don't retry** — fail fast |
| **Ambiguous** | Timeout after request sent (did it process?) | Check status first, then decide |

## Key Design Principles

### 1. Idempotency keys are non-negotiable

Every payment retry MUST carry the same idempotency key as the original request. The downstream system uses this to deduplicate:

```
Request 1: {idempotency_key: "abc123", amount: 500} → Processed ✓
Request 2: {idempotency_key: "abc123", amount: 500} → Already processed, return same result
```

Without idempotency: `Request 2` would charge the customer again.

### 2. Retry budget

Set a maximum number of retries per transaction (e.g., 3). Each retry has a cost:
- Latency added to the customer experience
- Resource consumption on your side
- Risk of confusing downstream state machines

### 3. Exponential backoff with jitter

```
retry_delay = min(base_delay * 2^attempt + random_jitter, max_delay)
```

The jitter prevents **thundering herd**: if 1000 requests fail at the same time, you don't want all 1000 retrying at `base_delay * 2^1` simultaneously.

### 4. Circuit breaking at the path level

If a gateway has N consecutive failures, stop routing traffic to it:

```
Healthy → N failures → Open (no traffic) → Timer → Half-open (probe) → Healthy
```

This prevents wasting retry budget on a known-broken path.

## Alternate Path Failover

```
Primary gateway fails
    ↓
Smart retry selects alternate gateway
    ↓
Factors:
  - Gateway health score (recent success rate)
  - Supported payment methods
  - Cost per transaction
  - Latency characteristics
    ↓
Route to best available alternative
```

## The Three Layers of Payment Resilience

```
Layer 1: Single-request (timeouts, retries with backoff)
Layer 2: Path-level (failover to alternate gateways)   ← Smart retry
Layer 3: System-level (circuit breakers, load shedding)
```

## Related

- [Story: Smart Retry Saves Cross-Border](/learnings/stories/smart-retry-saves-cross-border.md)
