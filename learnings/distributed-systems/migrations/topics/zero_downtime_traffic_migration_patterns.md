# Zero-Downtime Traffic Migration Patterns

## What is it?

A set of strategies for moving production traffic from one system (auth protocol, service, database, gateway) to another without any customer-facing impact — not even a blip in success rates or latency.

## Why it matters

In payment processing, downtime = lost revenue. A 1-minute outage during peak hours can affect thousands of transactions. Migrations are the most common source of self-inflicted outages because they change critical-path behavior.

## Core Patterns

### 1. Gradual Percentage Ramp-Up

Route a small percentage of traffic to the new system, validate, then increase.

```
Day 1:   1%  → Validate for 24h
Day 3:   5%  → Validate for 24h
Day 5:   10% → Validate for 24h
Day 7:   25% → Validate for 24h
Day 10:  50% → Validate for 48h
Day 14:  100%
```

**When to use:** When you can split traffic at the routing layer and both old/new systems can serve the same request.

**Example:** [Amazon Pay JWS Migration](/learnings/stories/amazon-pay-jws-migration.md) — 1% → 5% → 10% → 25% → 50% → 100% over 2 weeks with both Razorpay and Amazon independently monitoring.

### 2. Forward-Fill + Backfill

Stop new entities from using the old system (forward-fill), then migrate existing entities in batches (backfill).

```
Step 1: New merchants onboard on new model (forward-fill)
Step 2: Existing merchants migrated in batches (backfill)
Step 3: Old model deprecated when backfill = 100%
```

**When to use:** When the migration involves a data model change (not just a routing change). Common for balance migrations, schema changes, and account model updates.

**Example:** [Merchant Balance Segregation](/learnings/stories/merchant-balance-segregation.md) — new merchants auto-onboarded to segregated balances while existing merchants were backfilled.

### 3. Shadow Traffic / Dual-Write

Send traffic to both old and new systems, compare results, only serve from old. Once confident, switch to serving from new.

```
Phase 1: Both systems process, old system serves (shadow mode)
Phase 2: Compare results, fix discrepancies
Phase 3: New system serves, old system shadows (reverse shadow)
Phase 4: Old system decommissioned
```

**When to use:** When correctness is more important than performance cost. Common for financial calculations, fraud detection, and settlement systems.

### 4. Feature Flag with Merchant-Level Granularity

Migrate specific merchants by ID, starting with internal/test merchants, then low-risk, then high-value.

```
Cohort 1: Internal test merchants
Cohort 2: Low-traffic merchants
Cohort 3: Medium-traffic merchants
Cohort 4: High-traffic (whale) merchants
```

**When to use:** When different merchants have different risk profiles or when you need partner approval per-merchant.

## Monitoring Requirements

At each migration stage, validate:

| Metric | Threshold |
|---|---|
| Success rate | No degradation from baseline |
| Latency (p50, p95, p99) | No increase >10% |
| Error rate | Zero new error types |
| Downstream pipeline health | CDC/ETL jobs producing correct data |

## Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Big-bang cutover | One chance to get it right; no rollback path |
| Skipping the 1% phase | Small traffic catches obvious bugs cheaply |
| Monitoring only success rate | Latency regressions and downstream failures are equally important |
| Declaring victory at 100% | Keep monitoring for 1-2 weeks after full rollout before decommissioning old system |

## Related Stories

- [Amazon Pay JWS Migration](/learnings/stories/amazon-pay-jws-migration.md) — textbook gradual ramp-up
- [Merchant Balance Segregation](/learnings/stories/merchant-balance-segregation.md) — forward-fill + backfill
- [YesBank ACS/FRM Migration](/learnings/stories/yesbank-acs-frm-two-quarter-migration.md) — multi-quarter banking migration
