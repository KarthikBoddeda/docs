# TiDB Data Correction 4x Speed-Up — Optimizing Under Pressure

**Date:** December 2025
**Channel:** `#potential_outages`
**Thread:** [Original post](https://razorpay.slack.com/archives/C02B75CA8V9/p1766474174914679)
**Shoutout:** [Piyush's appreciation](https://razorpay.slack.com/archives/C02B75CA8V9/p1767232107497229)

---

## STAR Summary

| | |
|---|---|
| **Situation** | Reporting credentials issue caused data corruption across TiDB clusters (admin, reporting, prod_white); backfill was running but painfully slow |
| **Task** | Fix corrupted data while simultaneously optimizing the correction job (ETA 4+ hours per cluster per day of data) |
| **Action** | Ran the original job while re-engineering query patterns in parallel; optimized correction from ~20min to ~5min per day |
| **Result** | 4x speed improvement, data corrected across all clusters, optimization applied to all future correction runs |

---

## The Full Story

### What Happened

A reporting credentials issue caused data corruption across multiple TiDB clusters:
- **admin** cluster
- **reporting** cluster
- **prod_white** cluster

The corruption meant reporting data was incorrect, affecting downstream analytics, dashboards, and potentially merchant-facing reports.

### The Initial Response

Sony (aryan.soni) identified and fixed the root cause (credentials issue). Then the data correction job was kicked off. But there was a problem — it was **slow**:

> "Folks.. the data backfill job is relatively slow here. we are working on possible optimisation while the original job is running will update once complete. current ETA is 4 hours for data fix on lake."
> — Himanshu Gangwar

### The Parallel Optimization

Here's what makes this story stand out: Sony didn't just sit and wait for the slow job to finish. He worked on **two tracks simultaneously**:

1. **Track 1:** Let the existing slow job run (it was correct, just slow)
2. **Track 2:** Analyze and optimize the job while it was running

After the data correction for Dec 26 was complete, Sony reported:

> "tidb cluster (admin, reporting, prod_white) data correction complete for 26th Dec. **Also did an optimization for this job, prod_white data correction time for one day reduced from ~20mins to ~5mins.**"

That's a **4x improvement** delivered while the incident was still being managed.

### The Timeline

```
Day 0: Credentials issue identified and fixed
       ↓
       Data corruption discovered across clusters
       ↓
       Slow correction job started (ETA: 4 hours for lake)
       ↓
       Sony starts optimizing in parallel
       ↓
Day 1: Correction complete for Dec 26
       Optimization done: 20min → 5min per day
       ↓
       Remaining days corrected with optimized job (4x faster)
       ↓
       Piyush Goel appreciates "hard work and sincerity"
```

**Related learning:** [TiDB bulk data correction optimization patterns](/learnings/databases/tidb/topics/tidb_bulk_data_correction_optimization.md)

---

## Deep Dive: Why Data Correction Jobs Are Slow (and How to Speed Them Up)

### Common bottlenecks in bulk correction jobs

| Bottleneck | Symptom | Optimization |
|---|---|---|
| **Row-by-row updates** | Job scales linearly with row count | Batch updates (UPDATE with IN clause) |
| **Missing indexes on filter columns** | Full table scans per correction query | Add temporary indexes for correction columns |
| **Transaction overhead** | Each row in its own transaction | Group 100-1000 rows per transaction |
| **Cross-cluster reads** | Reading from prod to correct reporting | Read from a replica or snapshot |
| **No parallelism** | Single-threaded correction | Partition by date/merchant and parallelize |
| **Over-selecting columns** | SELECT * when you only need ID + fix column | Select only required columns |

### The 4x improvement likely came from

Without seeing the exact code, a 20min → 5min improvement (4x) typically comes from:
1. **Batching** — moving from row-by-row to batched updates
2. **Index-aware queries** — ensuring the WHERE clause hits indexes
3. **Reduced transaction boundaries** — fewer commits = less fsync overhead
4. **Parallel execution** — if the data is partitioned by date, multiple days can be corrected concurrently

---

## Why This Is Interesting

### 1. Optimizing under fire — the "two-track" approach

Most engineers in an incident either:
- Run the slow fix and wait (safe but wastes time)
- Try to optimize first and then run (risky — delays the fix)

Sony did **both**: let the safe-but-slow job run while simultaneously building a faster version. This is a mature engineering instinct — it hedges against the optimization failing while capturing the upside if it succeeds.

### 2. The permanent value of incident-driven optimization

The 4x speedup wasn't just for this incident. It became the new baseline for all future data correction runs. This is the difference between "incident response" and "incident-driven improvement" — the optimization outlives the incident.

### 3. Data correction is an underrated skill

We talk about writing data, querying data, and migrating data. But **correcting data at scale** is its own skill:
- You need to understand the corruption pattern
- You need to write idempotent corrections (safe to re-run)
- You need to handle partial failures mid-correction
- You need to verify the correction actually worked

### 4. Stakeholder management while fixing

Himanshu's message ("data backfill job is relatively slow, working on optimization, will update") is good incident communication: transparent about the problem, clear about the action, and sets expectations.

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Two-track incident response** | Run the slow-but-correct fix while optimizing in parallel. You get safety *and* speed. |
| **Batch vs. row-by-row** | Bulk data operations should always be batched — the overhead per-row adds up fast at scale. |
| **Incident-driven optimization** | Optimizations born from incidents should be kept permanently, not discarded after the fix. |
| **Idempotent corrections** | Data correction jobs must be safe to re-run. If it fails halfway, running it again shouldn't double-corrupt. |

---

## Key References

- [Original thread (#potential_outages)](https://razorpay.slack.com/archives/C02B75CA8V9/p1766474174914679)
- [Sony's optimization report](https://razorpay.slack.com/archives/C02B75CA8V9/p1766776286743079)
- [Himanshu's status update on slow backfill](https://razorpay.slack.com/archives/C02B75CA8V9/p1766576032752419)
- [Piyush's shoutout](https://razorpay.slack.com/archives/C02B75CA8V9/p1767232107497229)
