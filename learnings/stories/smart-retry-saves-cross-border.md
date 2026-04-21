# Smart Retry Saves Cross-Border Payments During Outage

**Date:** December 2025
**Channel:** `#cross-border-alerts`
**Thread:** [Original post](https://razorpay.slack.com/archives/C033XHUNAUW/p1765698843092529)
**Key message:** [Krishna's observation](https://razorpay.slack.com/archives/C033XHUNAUW/p1765783735187279)

---

## STAR Summary

| | |
|---|---|
| **Situation** | A significant outage hit a cross-border payment processing path, threatening transaction failures for international merchants |
| **Task** | Minimize payment failures during the outage window while the underlying issue was being resolved |
| **Action** | No heroic code fix needed — a previously implemented "smart retry" mechanism automatically retried failed payments through alternate paths |
| **Result** | Payments that would have failed were retried successfully, significantly reducing merchant impact during the outage |

---

## The Full Story

### What Happened

An outage hit one of the cross-border payment processing paths. International payment transactions started failing. The cross-border alerts channel lit up.

### The Non-Story That Is The Story

What makes this interesting is what *didn't* happen:
- No war room was needed for payment recovery
- No emergency code was deployed
- No manual intervention to retry failed payments

Instead, a **smart retry mechanism** that had been built and enabled earlier kicked in automatically. Krishna Ravavarapu observed:

> "it appears that keeping smart retry on was very useful during this outage."

The system was designed to detect payment failures and automatically retry them — either through alternate paths, after brief delays, or with adjusted parameters. During the outage, it did exactly that.

---

## Deep Dive: Smart Retry Patterns

### Basic retry vs. smart retry

**Basic retry:** Try the same request again after a delay.
- Problems: hammers a down service harder, doesn't help if the path itself is broken

**Smart retry:** Analyze the failure type and choose the optimal retry strategy.

```
Payment attempt fails
    ↓
Classify failure:
├── Transient (timeout, 503) → retry same path with backoff
├── Path-level (gateway down) → retry via alternate gateway
├── Rate-limited (429)        → retry with exponential backoff
├── Permanent (invalid card)  → don't retry, fail fast
└── Unknown                   → retry once, then fail
```

**Related learning:** [Smart retry patterns in payment systems](/learnings/distributed-systems/resilience/topics/smart_retry_patterns.md)

### Key design decisions in payment retry systems

| Decision | Trade-off |
|---|---|
| **Retry budget** | Too many retries = duplicate charges risk. Too few = lost revenue. |
| **Idempotency keys** | Essential to prevent duplicate payments. Every retry must carry the same idempotency key. |
| **Alternate path selection** | How do you pick which alternate gateway to try? Round-robin? Success-rate based? Latency based? |
| **Timeout tuning** | Short timeouts = faster failover but more false-positive retries. Long timeouts = slower detection. |
| **Circuit breaking** | When a path has N consecutive failures, stop sending traffic to it entirely. |

### The three layers of payment resilience

```
Layer 1: Single-request resilience (timeouts, retries)
    ↓
Layer 2: Path-level resilience (failover to alternate gateways)
    ↓
Layer 3: System-level resilience (circuit breakers, load shedding)
```

Smart retry operates at **Layer 1 and 2** — it handles individual failures and can failover to alternate paths. Circuit breakers (Layer 3) prevent cascade failures.

---

## Why This Is Interesting

### 1. The boring hero

This story has no 48-hour debugging sessions, no clever root cause analysis, no last-minute production hotfix. The "hero" is a feature that was built weeks or months earlier, sitting quietly in production, waiting for exactly this scenario. **Resilience engineering is unglamorous but high-impact.**

### 2. Preparedness vs. reaction

There are two ways to handle outages:
- **Reactive:** Detect failure → page on-call → debug → fix → deploy → recover
- **Proactive:** Build resilience → failure happens → system self-heals → monitor → no human intervention needed

The cross-border team chose the proactive path. The investment in smart retry converted a "we need to scramble" moment into a "the system handled it" moment.

### 3. "Keeping it on" — the discipline of not disabling safety nets

Krishna's phrasing is revealing: "keeping smart retry **on** was very useful." This implies there was a decision at some point to enable (or keep enabled) the retry mechanism. Safety features get disabled for many reasons: performance concerns, debugging noise, false positives, or "we don't need it anymore." The discipline of **keeping safety nets active** is what made this work.

### 4. The ROI of resilience is invisible

When smart retry works, you see... nothing. No alerts, no incidents, no war rooms. The outage happened, payments succeeded anyway, and nobody panicked. This makes it hard to justify the engineering investment *before* it pays off. But the alternative — a full outage with manual recovery — would have been extremely visible and expensive.

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Resilience is proactive, not reactive** | The best incident response is the incident that never escalates because the system self-healed |
| **Smart retry > dumb retry** | Classify failures and choose the right strategy. Not all failures should be retried the same way. |
| **Idempotency is non-negotiable** | In payment systems, retries without idempotency keys risk duplicate charges — worse than the original failure |
| **Don't disable safety nets** | The temptation to turn off resilience features for "simplicity" or "performance" erodes exactly the safety they provide |
| **Invisible ROI** | Resilience engineering's ROI is measured in incidents that *didn't* happen — which makes it hard to justify but incredibly valuable |

---

## Key References

- [Original alert thread (#cross-border-alerts)](https://razorpay.slack.com/archives/C033XHUNAUW/p1765698843092529)
- [Krishna's observation about smart retry](https://razorpay.slack.com/archives/C033XHUNAUW/p1765783735187279)
