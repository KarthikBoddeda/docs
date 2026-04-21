# Database Engine Migration with CDC Validation

## What is it?

The process of migrating from one database engine to another (e.g., RDS MySQL → Aurora MySQL) while ensuring that all downstream data consumers — CDC pipelines, ETL jobs, reporting feeds — continue to function correctly.

## Why it matters

Modern architectures don't just read from databases via application queries. They also consume database changes via:
- **CDC (Change Data Capture)** — real-time change streams from binlog/WAL
- **ETL jobs** — periodic batch extracts for data warehouses
- **Replication feeds** — streaming to read replicas or analytics clusters

A database engine migration that breaks application queries is caught immediately. A migration that breaks CDC is often caught **days later** when a report is wrong or a dashboard is stale.

## The Two-Sanity-Check Pattern

Every database migration should validate two things:

```
Database Migration
    │
    ├── Application Sanity (immediate check)
    │   ├── Reads work correctly
    │   ├── Writes work correctly
    │   ├── Transactions commit/rollback correctly
    │   └── Connection pooling works
    │
    └── Data Engineering Sanity (lagging check)
        ├── CDC events are flowing
        ├── Event format hasn't changed
        ├── Downstream consumers process events
        └── End-to-end data matches source
```

**Example:** In the [RDS to Aurora wallet migration](/learnings/stories/rds-to-aurora-wallet-migration.md), Raghav confirmed application sanity while Nikit confirmed DE pipeline sanity — both were explicitly tracked.

## RDS MySQL → Aurora MySQL: Key Differences

While Aurora is "MySQL-compatible," there are subtle differences that can affect CDC consumers:

| Aspect | RDS MySQL | Aurora MySQL |
|---|---|---|
| Storage engine | InnoDB on EBS | Custom Aurora storage |
| Binlog format | Configurable | Same options, but Aurora-specific nuances |
| Replication | Standard MySQL replication | Aurora-specific replication protocol |
| Failover behavior | DNS TTL-based | Endpoint stays same, faster failover |
| Transaction IDs | Standard GTID | Aurora GTID |

These differences can cause:
- CDC tools to lose position after failover
- Binlog consumers to encounter unexpected event types
- Replication lag behavior to change

## Validation Checklist

| Step | How to validate |
|---|---|
| CDC events flowing | Check consumer lag metrics post-migration |
| Event format correct | Compare sample events pre/post migration |
| No data loss | Row counts in source vs. sink |
| Ordering preserved | Verify event ordering for key entities |
| Downstream reporting | Check dashboard values match source queries |

## Progressive Validation Strategy

Don't migrate all databases at once:

```
Phase 1: Test/staging database → validate both sanity checks
Phase 2: Low-traffic production database → validate both sanity checks
Phase 3: High-traffic production database → validate both sanity checks
```

**Example:** The wallet team migrated prod-wallet-test and prod-gcoms first, confirmed both sanity checks, then migrated prod-wallet-live — building confidence at each step.

## Related Stories

- [RDS to Aurora Wallet Migration](/learnings/stories/rds-to-aurora-wallet-migration.md) — progressive validation with dual sanity checks
