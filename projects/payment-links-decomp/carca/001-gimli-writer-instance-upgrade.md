# CARCA: Gimli Aurora MySQL Writer Instance Upgrade

**Date**: 2026-03-10
**Requested by**: No-Code Apps / Payment Links team
**Instance**: `prod-aurora-mysql-gimli-new-1b` (Aurora MySQL Writer)
**Service**: Gimli (Payment Links backend DB)

> **Note:** Payment Links is the primary traffic contributor for the Gimli database. While Gimli serves other no-code products (Payment Pages, Payment Buttons), the dominant write workload comes from Payment Link creation, updates, and status changes.

---

## Details Required for Cost Approval

### Projected Monthly Impact

1. If the expenditure is approved, what will be the projected monthly cost increment?

   **~$299/month** (from ~$348/month to ~$647/month on-demand)

   | | Current | Proposed |
   |---|---|---|
   | Instance Class | `db.r6g.xlarge` | `db.r6g.2xlarge` |
   | vCPUs | 4 | 8 |
   | Memory | 32 GB | 64 GB |
   | Hourly Rate (ap-south-1) | ~$0.483/hr | ~$0.899/hr |
   | Monthly Cost | ~$348 | ~$647 |

2. What will be the cost impact on the remainder of the current month?

   ~$199 (prorated for ~20 remaining days in March 2026)

### Duration of Impact

**Permanent.** This is a capacity upgrade to handle sustained traffic growth in payment links creation. Payment links traffic has been growing and the current instance is consistently saturated during daily peak hours (see metrics below). This is not a temporary spike.

Additionally, there are **two major traffic increases** already committed:

1. **Meta (WhatsApp Pay)** is demanding Enhanced Payment Links (EPL) APIs scale to **300 TPS** ([Slack thread](https://razorpay.slack.com/archives/C01FCB94K6V/p1772085775609699)). Meta has escalated that low TPS limits are preventing them from moving EPL out of Alpha. Impacted merchants include **CredCollect** (10K+ PL / 5 min peak), **CASHe** (3K+ PL / 5 min), **Adda247**, **Iztri**, and **Explorex**. Meta currently routes only ~10% of volumes to Razorpay due to throttling. If we don't scale, we risk losing **Rs 100 Cr in GMV** to PayU and Cashfree.

2. **Omni team (Amazon + Reliance Jio migration)** is ramping up **+6-7 lakh transactions/day** by month-end as they migrate enterprise merchants from the Ezetap stack to Razorpay Omni stack ([Slack thread](https://razorpay.slack.com/archives/C6QPQKVLZ/p1756707976007009)). Amazon alone generates **~5-10 lakh PL creation requests daily**, with peaks of **70-140 TPS at 4-6 AM**. We flagged in the thread that Gimli's DB is already under pressure during peak hours and would need to be scaled up for this traffic increase.

**Current traffic reality**: Payment Links traffic today peaks at **~100-135 RPS**, well below Meta's requested 300 RPS. The DB is already choking at this level -- scaling to 300 RPS without an upgrade is not feasible.

<!-- TODO - insert traffic-by-route-rps.png -->


### Reason for Cost Increase

The Gimli Aurora MySQL **writer instance is choking during peak payment links traffic hours**, causing **5xx errors on payment link creations** (`POST /v1/payment_links`).

**Root cause**: The `db.r6g.xlarge` instance (4 vCPUs, 32 GB RAM) is undersized for current traffic levels. Multiple CloudWatch metrics confirm saturation across CPU, I/O, and connections.

#### CloudWatch Metrics Analysis (March 4-10, 2026)

**1. DiskQueueDepth (CRITICAL -- primary bottleneck)**

<!-- TODO - insert disk-queue-depth.png -->

- Peak: **23**, regularly sustained at **11-17** during traffic hours
- **A healthy database should have DiskQueueDepth < 2-3**
- This is the single biggest red flag -- the storage subsystem is persistently backlogged, meaning every DB query (read or write) waits behind a queue of 20+ I/O operations
- Upgrading doubles the memory (larger InnoDB buffer pool = fewer disk reads) and increases I/O throughput, directly addressing this

**2. DatabaseConnections (confirms connection exhaustion)**

<!-- TODO - insert database-connections.png -->

- Baseline: **100-180 connections**, spikes up to **728** (March 4, March 6)
- Connection spikes correlate directly with the 5xx error windows
- Gimli uses `MaxOpenConnections = 120` per pod; 728 connections ≈ 6 pods all maxed out simultaneously
- When queries are slow due to I/O queueing, connections are held open longer, causing the pool to fill up across all pods

**3. FreeableMemory (explains why DiskQueueDepth is high)**

<!-- TODO - insert freeable-memory.png -->

- Range: **2.5 - 4.0 GB free** out of 32 GB total
- InnoDB buffer pool is nearly full, forcing frequent disk reads (cache misses) and aggressive dirty page flushing
- With `db.r6g.2xlarge` (64 GB), the buffer pool can cache significantly more data in memory, reducing disk I/O and bringing DiskQueueDepth down

**Other metrics (supporting, not critical):**

- **CPUUtilization**: Peaks at ~58%, sustained 43-50% during peak hours. High but manageable -- not the bottleneck. <!-- TODO - insert cpu-utilization.png -->
- **ReadLatency**: Baseline ~0.88ms, spikes to 3.5ms (4x degradation) during I/O storms. Downstream symptom of DiskQueueDepth. <!-- TODO - insert read-latency.png -->
- **WriteLatency**: Baseline ~1.0ms, spikes to 1.66ms. Downstream symptom of DiskQueueDepth. <!-- TODO - insert write-latency.png -->
- **ReadIOPS**: Peaks at 1,727 IOPS. High reads during peak confirm the buffer pool is too small to serve reads from memory. <!-- TODO - insert read-iops.png -->
- **WriteIOPS**: Peaks at 4,469 IOPS. Write-heavy workload consistent with payment link creation. Dominant I/O pattern. <!-- TODO - insert write-iops.png -->

#### Key Indicator Summary

**DiskQueueDepth at 23 (should be < 3) is the smoking gun**, combined with connection spikes to 728 and correlated Vajra/SG 5xx alerts. This trifecta -- I/O saturation + connection exhaustion + confirmed production failures -- leaves no ambiguity about the root cause being DB capacity.

#### Why Payment Links Gets 5xx: Log Evidence

Production logs from Coralogix (March 9, 2026) confirm the failure mechanism:

- **Error code**: `DB_READ_CONN_SETUP_ERROR`
- **Error message**: `"PDO object is not initialized, constructor was not called"`
- **Affected routes**: `payment_links_cancel`, `payment_links_get`, `payment_links_fetch_multiple`
- **Severity**: CRITICAL (level 500)
- **Clusters**: Both `cde-green-eks` and `cde-blue-eks`

**What this means**: When the DB is overwhelmed (DiskQueueDepth > 20, connections at 728), new MySQL PDO connections fail to establish. The application can't even set up a database connection to serve the request, so it returns a 5xx. This is not an application bug -- the database is rejecting new connections because it's saturated.

Example log entry (March 9, 10:14 UTC):
```
route_name: payment_links_cancel
uri: /v1/payment_links/plink_SOz67VkayUPtfv/cancel
code: DB_READ_CONN_SETUP_ERROR
message: PDO object is not initialized, constructor was not called
```

#### Correlated Alert Evidence from Production

The following alerts fired during the same timeframes as the DB metric spikes:

| Date | Channel | Alert |
|---|---|---|
| March 4 | `#vajra-alerts` | **[FIRING] Gimli API Errors - 4xx/5xx alert** -- 500 error value: 25.43 |
| March 7-8 | `#sg_alerts` | **[FIRING] [SG][5xx] Payment Links Create 5xx count > 5 over last 15 mins** -- count = 22 over 60 mins, pod: `nocodeapps`, severity: critical |
| March 7 | `#tech_spine_alerts_sg` | `POST v1/payment-links` has **multiple 503s** from upstream in SG |
| March 8 | `#sg_alerts` | SG edge team reporting **zenduty calls from 1 AM to 4 AM** over the weekend due to upstream 503s on `/v1/payment_links` |

### Risks if Not Approved

1. **Payment link creations will continue to fail with 5xx** during peak traffic hours (daily pattern, not a one-off). This directly impacts merchant payment collection. Logs confirm the failure is `DB_READ_CONN_SETUP_ERROR` -- the database literally cannot accept new connections.

2. **SG region is also affected** -- the SG edge team (`#sg_alerts`) is receiving zenduty alerts for upstream 503s on `POST /v1/payment_links`, generating oncall fatigue and potential SLA breaches.

3. **Meta/WhatsApp partnership at risk** -- Meta has escalated that they can't move Enhanced Payment Links out of Alpha due to our low TPS limits. They are currently routing only ~10% of traffic to Razorpay. Without scaling, we risk losing **Rs 100 Cr in GMV** to competitors (PayU, Cashfree). This also jeopardizes ongoing Ads Billing and Payouts discussions with Meta.

4. **Omni migration (Amazon + Jio) at risk** -- The Omni team is ramping up +6-7 lakh transactions/day from Amazon and Reliance Jio by month-end, with Amazon generating 5-10L PL creations/day peaking at 70-140 TPS. Without the upgrade, these traffic increases will worsen the existing failures and potentially cause sustained outages.

5. **Revenue impact** -- Every failed payment link creation is a blocked merchant transaction. Payment links is a high-volume product used for bulk collections by large merchants including CredCollect, CASHe, Adda247.

6. **Worsening trajectory** -- Traffic is growing. The current instance is already saturated at 58% CPU with DiskQueueDepth at 23. Without an upgrade, 5xx frequency and duration will increase as traffic grows.

### Mitigation Plan

#### Immediate: Instance Upgrade (this request)

The instance upgrade is required **now** to stop ongoing 5xx failures and handle the current + incoming traffic (Meta/WhatsApp EPL rollout). This is the only lever that can be applied immediately without code changes or deployment risk.

The `db.r6g.2xlarge` upgrade addresses all three pressure points:
- **2x CPU** (4 -> 8 vCPUs): More capacity for concurrent query execution
- **2x Memory** (32 -> 64 GB): Larger InnoDB buffer pool reduces disk reads, directly lowering DiskQueueDepth
- **Higher network/I/O throughput**: Larger instance classes get proportionally better network and EBS throughput from AWS

#### Medium-term: Dev Effort to Reduce DB Load

There are engineering optimizations that can reduce the load on Gimli and potentially allow us to scale back the instance or avoid further upgrades in the future. However, these require dev effort across multiple sprints -- design, implementation, testing, and deployment.

Meanwhile, the DB is failing **today** and Meta is escalating **now**. The instance upgrade is the bridge to keep production stable while we pursue these longer-term improvements.

---

## References

- Vajra Dashboard: [Payment Links v2](https://vajra.razorpay.com/d/GrmafVeZk/payment-links-v2)
- AWS CloudWatch: `prod-aurora-mysql-gimli-new-1b` metrics (March 4-10, 2026)
- Slack alerts: `#vajra-alerts`, `#sg_alerts`, `#tech_spine_alerts_sg`, `#no-code-app`
- Meta/WhatsApp EPL 300 TPS request: [Slack thread](https://razorpay.slack.com/archives/C01FCB94K6V/p1772085775609699)
- Omni Amazon+Jio migration traffic increase: [Slack thread](https://razorpay.slack.com/archives/C6QPQKVLZ/p1756707976007009)
- Coralogix logs: `DB_READ_CONN_SETUP_ERROR` on `payment_links_cancel`, `payment_links_get`, `payment_links_fetch_multiple` (March 9, 2026)
