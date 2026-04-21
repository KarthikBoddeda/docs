# TiDB — Character Set Incompatibility in v8.1

**Project**: [pingcap/tidb](https://github.com/pingcap/tidb) (Go, 38K+ stars)
**Status**: Critical infrastructure blocker for Razorpay's TiDB v8.1 migration
**Difficulty**: High (database internals, charset handling)
**Impact**: Very High — blocks a major migration

## The Problem

From Himanshu Gangwar in `#tidb-migration` (Feb 2026):
> "Critical Infrastructure Blocker: Character Set Incompatibility in TiDB v8.1. The migration to TiDB v8.1 has revealed a fundamental incompatibility between our legacy data..."

Razorpay uses TiDB extensively as a warm/hot storage layer. The v8.1 upgrade exposed character set handling issues with legacy data that was written under older charset configurations.

## Context: TiDB at Razorpay

TiDB serves as a critical data layer across multiple teams:
- **Payouts** — Had P0 use case dependency (now being reconsidered)
- **Settlements** — Reporting APIs
- **UPI Payments** — Transaction records in `fiscal`, `transactions`, `payments` tables
- **Admin** — Core admin database
- **Data Platform** — CDC connectors for data replication

### Scale Concerns

From Himanshu:
> "Each TiKV addition requires about 15 days of data rebalancing, thus further increasing cluster stress each time we add capacity."

### Operational Issues

1. **Data sync issues** — TiDB and Datalake have inconsistent data
2. **High-write table performance** — Questions about recommended practices
3. **Hot-to-warm storage latency** — Impact on real-time use cases
4. **No foreign key constraints** — Referential integrity is application-level only

## What Could Be Contributed

### 1. Character Set Migration Tooling
TiDB needs better tooling for migrating data between character sets (e.g., `latin1` → `utf8mb4`) without downtime. This is a known pain point for any MySQL-compatible database handling legacy data.

### 2. TiKV Rebalancing Performance
15 days for data rebalancing per TiKV node addition is extremely slow. Contributing optimizations to TiKV's region rebalancing algorithm would benefit all TiDB users at scale.

### 3. Data Consistency Verification
Tools to verify data consistency between TiDB and downstream systems (datalake, CDC) are needed. From multiple threads, teams discovered out-of-sync data between TiDB and their datalake.

## Slack Threads

| Thread | Channel | What's Discussed |
|--------|---------|-----------------|
| [p1770589490](https://razorpay.slack.com/archives/C05L8PNL1MF/p1770589490923639) | #tidb-migration | Critical charset incompatibility blocker |
| [p1773309556](https://razorpay.slack.com/archives/C05L8PNL1MF/p1773309556067339) | #tidb-migration | Admin TiDB stability, TiKV rebalancing |
| [p1773399169](https://razorpay.slack.com/archives/C05L8PNL1MF/p1773399169281329) | #tidb-migration | Ops/Analytics access concerns |
| [p1772554561](https://razorpay.slack.com/archives/C05L8PNL1MF/p1772554561315499) | #tidb-migration | Deprecation of temporary TiDB onboarding |
| [p1772092045](https://razorpay.slack.com/archives/C05L8PNL1MF/p1772092045879589) | #mission-reliability-week | TiDB should not have P0 use case |
| [p1771583805](https://razorpay.slack.com/archives/C05L8PNL1MF/p1771583805941849) | #payments_upi | Production DB exposure concerns |

## Key People

- **Himanshu Gangwar** (@himanshu.gangwar) — TiDB migration lead, DBA
- **Narendra Kumar** (@narendra.kumar) — Data platform, TiDB governance
- **Nitesh Jain** (@nitesh.jain) — TiDB cluster management
- **Anuj Jain** (@anuj.jain) — TiDB operations
