# RDS to Aurora Migration — Wallet Service Database Upgrade

**Date:** February 2026
**Channel:** `#performance_qa`
**Thread:** [Original thread](https://razorpay.slack.com/archives/C01GU4BRCBG/p1753774805176889)
**Completion:** [prod-wallet-live](https://razorpay.slack.com/archives/C01GU4BRCBG/p1771357689191219), [prod-wallet-test + prod-gcoms](https://razorpay.slack.com/archives/C01GU4BRCBG/p1770320094144259)

---

## STAR Summary

| | |
|---|---|
| **Situation** | Wallet service production databases (wallet-live, wallet-test, gcoms) needed migration from RDS MySQL to Aurora |
| **Task** | Execute live database engine migration for a financial service with zero downtime and verified data integrity |
| **Action** | Migrated in phases — wallet-test and gcoms first (validation), then wallet-live; app sanity + DE pipeline sanity after each |
| **Result** | All three databases migrated successfully with confirmed application and data engineering pipeline sanity |

---

## The Full Story

### What is RDS to Aurora Migration?

Amazon Aurora is a MySQL/PostgreSQL-compatible relational database built for the cloud. Migrating from standard RDS MySQL to Aurora provides:
- **Up to 5x throughput improvement** over standard MySQL
- **Storage auto-scaling** up to 128TB
- **6-way replication** across 3 AZs
- **Automated failover** in <30 seconds
- **Backtrack** (point-in-time recovery without restoring from backup)

For a wallet service handling financial transactions, these reliability and performance improvements are significant.

### The Migration Strategy: Lower Environments First

The team didn't migrate everything at once. They used a **progressive validation** approach:

```
Phase 1: prod-wallet-test + prod-gcoms
    ↓ Application sanity confirmed (Harsh Kaswan)
    ↓ DE pipeline sanity confirmed (Nikit)
    ↓
Phase 2: prod-wallet-live
    ↓ Application sanity confirmed (Raghav)
    ↓ DE pipeline sanity confirmed (Nikit)
    ↓
Migration complete ✓
```

Prateek Jain coordinated the migrations and confirmations:

> "We have successfully completed the migration of prod-wallet-test and prod-gcoms. Sanity is confirmed by Harsh Kaswan and Raghav."

Then, after gaining confidence:

> "RDS to Aurora Migration is completed successfully for prod-wallet-live. Raghav has confirmed the application sanity and Nikit has completed the sanity for DE pipelines."

### Why Two Types of Sanity Checks?

| Check | Who | What they verify |
|---|---|---|
| **Application sanity** | App team (Raghav, Harsh) | Wallet operations work: balance reads, credits, debits, settlements |
| **DE pipeline sanity** | Data Engineering (Nikit) | Data pipelines (ETL, CDC, reporting feeds) still produce correct data post-migration |

Both are essential because:
- Application sanity confirms the **write path** and **read path** work
- DE sanity confirms the **replication/CDC path** works — Aurora's binlog format may differ slightly from RDS MySQL, which can break downstream consumers

---

## Why This Is Interesting

### 1. Database engine migration for a live financial service

Migrating the database engine for a wallet service is like changing the engine of an airplane mid-flight:
- Transactions are flowing continuously
- Balances must remain accurate to the penny
- Downstream systems (reporting, reconciliation, settlements) depend on data consistency
- Any hiccup means real money is at risk

### 2. The progressive validation pattern

Rather than migrating everything at once and hoping for the best, the team built confidence iteratively:
- **Low-risk first** (test environment) — catch obvious issues
- **Medium-risk next** (gcoms) — catch integration issues
- **High-risk last** (wallet-live) — migrate with proven confidence

This is the database equivalent of a canary deployment.

### 3. The DE pipeline dependency most people forget

Many teams validate application sanity and call it done. But modern data architectures have **downstream consumers** that read from the database via CDC (Change Data Capture), binlog replication, or ETL jobs. Aurora's storage engine (custom, InnoDB-based) may produce slightly different binlog events or have different replication characteristics than standard RDS MySQL.

Forgetting to validate DE pipelines can lead to:
- Stale reporting dashboards
- Missing data in data warehouses
- Broken reconciliation jobs

The team explicitly validated both — a sign of maturity.

**Related learning:** [Database engine migration with CDC validation](/learnings/databases/migrations/topics/database_engine_migration_cdc_validation.md)

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Progressive validation** | Migrate low-risk environments first to build confidence before touching production |
| **Dual sanity checks** | Database migrations need both application sanity AND data pipeline sanity — forgetting either causes silent failures |
| **Aurora advantages** | 5x throughput, 6-way replication, auto-failover, backtrack — material improvements for financial workloads |
| **CDC compatibility** | Database engine changes can break CDC/binlog consumers. Always validate downstream data pipelines. |

---

## Key References

- [Original performance_qa thread](https://razorpay.slack.com/archives/C01GU4BRCBG/p1753774805176889)
- [prod-wallet-test + prod-gcoms completion](https://razorpay.slack.com/archives/C01GU4BRCBG/p1770320094144259)
- [prod-wallet-live completion](https://razorpay.slack.com/archives/C01GU4BRCBG/p1771357689191219)
