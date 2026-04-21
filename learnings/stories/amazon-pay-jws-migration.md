# Amazon Pay JWS Migration — "The Smoothest Migration I've Ever Worked On"

**Date:** January–February 2026 (6 weeks)
**Channel:** `#amazon-pay`
**Thread:** [Original post](https://razorpay.slack.com/archives/C09HTR65PM3/p1767785487877359)
**Completion:** [Punit's message](https://razorpay.slack.com/archives/C09HTR65PM3/p1770218500684869)

---

## STAR Summary

| | |
|---|---|
| **Situation** | Amazon Pay required migration from legacy G2 certificate auth to JWS (JSON Web Signature) authentication for all traffic |
| **Task** | Implement JWS auth, get Amazon UAT sign-off, migrate 100% of production traffic with zero disruption on a fixed deadline |
| **Action** | Built JWS auth, coordinated UAT with Amazon, executed a textbook gradual ramp-up (1% → 5% → 10% → 25% → 50% → 100%) over 3 weeks |
| **Result** | 100% traffic migrated, 100% success rate, bonus ~100ms latency improvement, zero drama |

---

## The Full Story

### The Problem

Amazon Pay required Razorpay to upgrade from the legacy G2 certificate-based authentication to **JWS (JSON Web Signature) authentication**. This wasn't optional — it was a certification requirement. The old auth mechanism was on borrowed time with a temporary fix deployed on Dec 22.

### The Timeline

This is a masterclass in project execution. Weekly status updates tell the full story:

| Date | Milestone | Status |
|------|-----------|--------|
| Dec 22 | Temp G2 cert fix deployed | Done |
| Jan 7 | JWS auth changes completed (RZP side) | Done |
| Jan 8 | Amazon UAT sign-off (dependency) | Waiting |
| Jan 13 | Target prod release | Target |
| Jan 14 | JWS Auth released to production | Done |
| Jan 21 | Prod sanity confirmed | Done |
| Jan 22 | 1% ramp-up — no issues observed | Done |
| Jan 27 | 5% ramp-up | Done |
| Jan 28 | 10% ramp-up | Done |
| Jan 29 | 25% ramp-up | Done |
| Feb 2 | 50% ramp-up | Done |
| **Feb 4** | **100% ramp-up** | **Done** |

### The Ramp-Up Strategy

```
Jan 22:  ████░░░░░░░░░░░░░░░░  1%   ← "no issues at our end or Amazon end"
Jan 27:  █████░░░░░░░░░░░░░░░  5%
Jan 28:  ██████░░░░░░░░░░░░░░  10%  ← Alerts in place, monitoring clean
Jan 29:  █████████░░░░░░░░░░░  25%
Feb 2:   ██████████████░░░░░░  50%
Feb 4:   ████████████████████  100% ← "Zero drama, clean execution"
```

At every stage:
- Alerts were in place to catch regressions
- Both Razorpay and Amazon independently monitored success rates
- The ramp-up schedule was **agreed upon by both sides** upfront

### The Celebration

Punit Mukherjee's message captures it:

> "We've successfully **migrated 100% of Amazon traffic to JWS** within specified timelines! Amazon has **verified the dashboards**, and everything looks rock solid."
>
> Key highlights:
> - 100% traffic on JWS
> - 100% Success Rate
> - **~100ms latency improvement** (a very nice bonus, though not the primary goal!)
>
> "Most importantly — this was **one of the smoothest migrations I've ever worked on.** Zero drama, clean execution, and great collaboration end-to-end."

Shalini got special thanks for supporting even during non-working hours and OOO days.

---

## Why This Is Interesting

### 1. The art of the boring migration

The most successful migrations are boring. No drama, no 2 AM pages, no rollbacks. This one achieved that through:
- **Dual-side monitoring** — both Razorpay and Amazon watching independently
- **Pre-agreed ramp schedule** — no debates about "should we go faster?"
- **Alerts before traffic** — monitoring was set up before the first 1%
- **Weekly status cadence** — stakeholders always knew where things stood

**Related learning:** [Zero-downtime traffic migration patterns](/learnings/distributed-systems/migrations/topics/zero_downtime_traffic_migration_patterns.md)

### 2. The latency bonus

JWS auth turned out to be **100ms faster** than the old G2 certificate auth. This wasn't the goal, but it's a common pattern: newer, simpler auth mechanisms have lower overhead. In payment processing, 100ms is significant — it directly impacts checkout completion rates.

### 3. Cross-company ramp-up coordination

Amazon controlled the merchant ramp-up schedule on their side. Razorpay deployed the code, but Amazon decided which merchants to migrate when. This required:
- Shared dashboards for success rate monitoring
- Coordinated escalation paths if issues appeared
- Mutual trust that the other side would roll back if needed

### 4. The "Help Needed" discipline

Every weekly update had a clear "Help Needed" section. When Mukesh needed Amazon's UAT sign-off, he didn't just mention it — he called it out as a **named dependency with an ETA**. This kind of explicit dependency management is what prevents projects from silently stalling.

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Gradual ramp-ups** | 1% → 5% → 10% → 25% → 50% → 100% over 2 weeks. Each step validates the previous one. |
| **Dual-side monitoring** | When migrating with an external partner, both sides must independently confirm success rates at each stage. |
| **The boring migration is the best migration** | Zero drama = excellent preparation. The excitement should be in the planning, not the execution. |
| **Weekly status discipline** | Fixed-format status updates (Progress / Next Milestone / Help Needed) keep stakeholders informed and surface blockers early. |
| **Auth protocol performance** | JWS can be faster than certificate-based auth. Modern auth isn't just more secure — it can be more performant. |

---

## Key References

- [Original thread (#amazon-pay)](https://razorpay.slack.com/archives/C09HTR65PM3/p1767785487877359)
- [1% ramp-up confirmation](https://razorpay.slack.com/archives/C09HTR65PM3/p1769085255584709)
- [100% migration complete message](https://razorpay.slack.com/archives/C09HTR65PM3/p1770218500684869)
- [Shalini's appreciation of Punit](https://razorpay.slack.com/archives/C09HTR65PM3/p1770269918388719)
