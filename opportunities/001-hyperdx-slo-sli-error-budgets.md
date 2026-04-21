# HyperDX — SLO/SLI/Error Budgets

**Project**: [hyperdxio/hyperdx](https://github.com/hyperdxio/hyperdx) (9K stars, TypeScript, ClickHouse + OpenTelemetry)
**Issue**: [#1453 — Feature Request: SLOs, SLIs, and Error Budgets](https://github.com/hyperdxio/hyperdx/issues/1453)
**Status**: Open, unclaimed. HyperDX team acknowledged but has not committed to building it.
**Difficulty**: High
**Impact**: Very High — Razorpay's observability team desperately wants this
**Filed by**: Alok S (Razorpay observability lead, GitHub: [@alok87](https://github.com/alok87))

## Why This Matters to Razorpay

Razorpay deployed HyperDX as their observability UX layer on top of ClickHouse (their "Olly 2.0" / wide event architecture). HyperDX is running in production serving the Payouts team and expanding to other teams. SLO/SLI support is the #1 missing feature for SRE workflows.

Alok has been actively pushing for this since Dec 2025 and pinged the maintainers multiple times:
- Dec 8, 2025: Filed the issue with full spec
- Dec 11: Asked if it'll be open source
- Dec 15: Asked again
- Jan 5, 2026: Offered to co-build with maintainers
- Mar 12, 2026: Pinged again — "Are we building this?"

HyperDX maintainer response (MikeShi42):
> "Sorry we haven't had time to evaluate this request... We'll try to find some time to discuss internally."

## What Needs to Be Built

This is a full-stack feature spanning backend, ClickHouse queries, and UI:

### Backend (TypeScript/Node.js)

1. **SLI Definition Engine** — Allow defining SLIs using the existing query builder (latency, availability, custom expressions)
2. **SLO Configuration** — Target percentage, rolling time window (7d/14d/30d/90d), associated services
3. **Error Budget Tracking** — Calculate remaining budget, burndown visualization, historical consumption
4. **Burn Rate Calculation** — `actual_error_rate / expected_error_rate`, multi-window burn detection
5. **Background Tasks** — Periodic SLO compliance calculation (every 1-5 min), burn alert triggering
6. **New MongoDB Models** — `ISLI` and `ISLO` entities with relationships

### ClickHouse Queries

```sql
-- SLI success rate over rolling window
SELECT
  countIf(duration_ms < 500) as successful_events,
  count(*) as total_events,
  successful_events / total_events * 100 as success_rate
FROM events
WHERE timestamp >= now() - INTERVAL 30 DAY
  AND service_name = 'my-service'
```

### UI (React)

1. **SLO List Page** — Overview with current status, error budget remaining, filters
2. **SLO Detail Page** — Real-time compliance %, burndown chart, burn rate over time, drill-down
3. **SLO Creation Wizard** — Step-by-step SLI/SLO config with preview
4. **BubbleUp Integration** — Click through from violations to root cause

### Alerting

- Burn alerts when budget depletes faster than expected
- Configurable thresholds with severity levels
- Webhook notifications (Phase 2: Slack, PagerDuty, email)

## Slack Threads

| Thread | Channel | What's Discussed |
|--------|---------|-----------------|
| [p1773335832](https://razorpay.slack.com/archives/C05L8PNL1MF/p1773335832670699) | #observability_at_razorpay | Gyan's name in ClickHouse blog (celebration) |
| [p1767685289](https://razorpay.slack.com/archives/C7CFVBLF2/p1767685289466489) | #tech_articles | Alok pointing Gyan to SLO issue as opportunity |
| [p1767629907](https://razorpay.slack.com/archives/C7CFVBLF2/p1767629907809939) | #tech_articles | Dec 2025 ClickStack update, contribution discussion |

## GitHub Activity

- **Issue created**: Dec 8, 2025 by @alok87
- **Last activity**: Mar 12, 2026 — Alok pinged again
- **Maintainer stance**: Acknowledged, not prioritized, open to community PRs
- **Related issues**: [#1452 — AI Route should use Vercel AI SDK](https://github.com/hyperdxio/hyperdx/issues/1452) (partially addressed by Gyan's PR)
- **External interest**: @dofinn, @sgarfinkel, @kentan88 all commented with interest

## References

- [Honeycomb SLO Documentation](https://docs.honeycomb.io/notify/slos/) — Alok's inspiration
- [Google SRE Book — SLOs](https://sre.google/sre-book/service-level-objectives/)
- [The Art of SLOs](https://sre.google/workbook/implementing-slos/)
- [Nobl9 SLO Platform](https://nobl9.com/) — Suggested as UX reference by @dofinn
