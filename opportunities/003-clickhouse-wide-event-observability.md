# ClickHouse / Wide Event Observability ("Olly 2.0")

**Projects**: [ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse), [open-telemetry/opentelemetry-collector](https://github.com/open-telemetry/opentelemetry-collector)
**Status**: Active POC at Razorpay, Payouts team adopted, expanding to more teams
**Difficulty**: High
**Impact**: High — core infra for Razorpay's next-gen observability

## What Razorpay Is Building

Razorpay's "Olly 2.0" is a fundamental shift from traditional logging to **wide event observability**:
- Replace individual log lines with rich, structured wide events
- Store everything in ClickHouse (columnar OLAP database)
- Use OpenTelemetry for standardized instrumentation
- HyperDX as the visualization layer

From Alok in `#payments_upi`:
> "OTEL is not the main aim. OTEL for standardization + Wide Event Observability is the main aim. You need to prove in the POC when wide event is their individual log lines are redundant, they are not needed."

He referenced [loggingsucks.com](https://loggingsucks.com/) as the philosophical foundation.

## Production Pain Points (Contribution Opportunities)

### 1. ClickHouse Operator for Kubernetes

Razorpay runs ClickHouse on Kubernetes. From Dhairya:
> "To use clickhouse official operator, we would also need to use clickhouse official keeper. So it requires changing the entire clickstack (excluding OTEL)."

The [Altinity ClickHouse Operator](https://github.com/Altinity/clickhouse-operator) and [ClickHouse's own operator](https://github.com/ClickHouse/clickhouse-operator) both have gaps. Contributing k8s operator improvements for production ClickHouse workloads would be valuable.

### 2. OTEL Collector Performance at Scale

Razorpay's pipeline: `K8s Pods → OTEL Agents (DaemonSet) → OTEL Collector → ClickHouse`

Issues encountered:
- Data not reaching ClickHouse intermittently
- Need SLO metrics for data pipeline reliability
- GitOps conflicts overwriting ClickHouse credentials

From Alok:
> "Ask this question to claude: Team is maintaining clickhouse for o11y and app data keeps not reaching there since some or other issue in between — what should be the slo metric?"

### 3. ClickHouse Query Optimization for Observability

From Razvi:
> "There will be hell lot of optimisations needed to make sure [cost stays manageable]. A bad query makes things slow AND expensive."

Cost bombs from unoptimized wide event queries are a real concern. Contributing query optimization features (better PREWHERE pushdown, materialized view patterns for SLO calculations, etc.) to ClickHouse itself would have massive impact.

### 4. Managed ClickStack Cost Optimization

From Alok:
> "The optimization they are doing in managed offering would make it cheaper to use their managed solution than running it on our own. Their compute and storage separation..."

ClickHouse is actively working on [managed ClickStack](https://clickhouse.com/blog/introducing-managed-clickstack-beta). Contributing to the open-source portions of compute/storage separation would benefit everyone.

### 5. goutils/telemetry Package — OTEL Adoption Skill

Alok created a Claude Code skill for OTEL adoption:
> "Skill: Telemetry for OTEL adoption with design of connected wide event o11y — Observability 2.0. How to observe and telemit: guideline on how to do observability right using goutils/telemetry package."

PR: [razorpay/claude-skills#28](https://github.com/razorpay/claude-skills/pull/28)

## Architecture

```
                    Razorpay Services
                          │
                    OTEL SDK (Go)
                          │
                    goutils/telemetry
                          │
                    ┌──────┴──────┐
                    │             │
              OTEL Agent     OTEL Agent
              (DaemonSet)    (DaemonSet)
                    │             │
                    └──────┬──────┘
                           │
                    OTEL Collector
                           │
                    ClickHouse Cluster
                           │
                      HyperDX UI
```

## Slack Threads

| Thread | Channel | What's Discussed |
|--------|---------|-----------------|
| [p1772553607](https://razorpay.slack.com/archives/C05L8PNL1MF/p1772553607227819) | #payments_upi | Wide event architecture philosophy |
| [p1773280984](https://razorpay.slack.com/archives/C05L8PNL1MF/p1773280984036449) | #observability_at_razorpay | Chirag integrating ClickHouse for claude code logs |
| [p1773301530](https://razorpay.slack.com/archives/C05L8PNL1MF/p1773301530951939) | #observability_at_razorpay | Alok on DB spans with business attributes |
| [p1771490493](https://razorpay.slack.com/archives/C05L8PNL1MF/p1771490493106939) | #mission-reliability-week | Cost tradeoff discussion for ClickStack |
| [p1767979687](https://razorpay.slack.com/archives/C05L8PNL1MF/p1767979687170449) | #observability_at_razorpay | SLO metrics for ClickHouse data pipeline |
| [p1766120385](https://razorpay.slack.com/archives/C05L8PNL1MF/p1766120385506209) | #observability_at_razorpay | ClickHouse down / credential overwrite incident |
| [p1767966923](https://razorpay.slack.com/archives/C05L8PNL1MF/p1767966923911549) | #observability_at_razorpay | ClickHouse operator management |
| [p1765914826](https://razorpay.slack.com/archives/C05L8PNL1MF/p1765914826026169) | #observability_at_razorpay | HyperDX running with ClickHouse manually |

## Key People

- **Alok S** (@alok.s) — Vision and direction for Olly 2.0
- **Dhairya Mehta** (@dhairya.jaykermehta) — ClickHouse operator and infra
- **Razvi** (@m.razvi) — Cost and risk analysis
- **Manas Saxena** (@manasajay.saxena) — Payouts adoption
- **Chirag Chiranjib** (@chirag.chiranjib) — Cloud agent ClickHouse integration

## Teams Using ClickHouse

- **Payouts** — First adopter for observability
- **Magic/Retargeting** — Event analytics (37L unique sessions/month)
- **Analytics Self-Serve** — Data platform (Pinot replacement)
- **Agentic SDLC** — Claude Code thinking logs
- **Security** — Event schema enrichment
