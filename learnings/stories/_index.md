# Engineering War Stories

Real incidents, debugging sagas, and creative solutions from Razorpay's Slack channels — documented using the STAR method with deep technical analysis and learning references.

## Incident Stories

| Story | Category | Key Learning |
|-------|----------|-------------|
| [GeoIP Cross-Region Database Ghost](./geoip-cross-region-database-ghost.md) | Distributed Systems, Multi-region | Emergent failures from independently correct systems |
| [Americana/Mashreq Marathon](./americana-mashreq-marathon.md) | Incident Management, Integration | Cross-company debugging and human endurance |
| [FTS Negative Timeout Overflow](./fts-negative-timeout-overflow.md) | Go, Type Safety | Go `time.Duration` integer overflow from double multiplication |
| [Phantom Snapshot Devstack Outage](./phantom-snapshot-devstack-outage.md) | Infrastructure, AWS | Automation deleting live AMI snapshots breaks ASG scaling |
| [AI Pre-Mortem Catches P0](./ai-premortem-catches-p0.md) | AI Engineering, Code Review | AI PR review tool catches root cause of P0 from code diff alone |
| [TiDB Data Correction 4x Speedup](./tidb-data-correction-4x-speedup.md) | Databases, Optimization | Parallel optimization during incident — 20min→5min correction |
| [Smart Retry Saves Cross-Border](./smart-retry-saves-cross-border.md) | Resilience, Payments | Pre-built retry mechanism auto-heals during outage |
| [ChiragBot Digital Twin](./chiragbot-digital-twin.md) | AI, Slack Bots | Personal digital twin survives 20+ jailbreak attempts |

## Project Stories

Larger, multi-week/multi-month engineering projects — migrations, platform builds, compliance efforts.

| Story | Category | Key Learning |
|-------|----------|-------------|
| [Amazon Pay JWS Migration](./amazon-pay-jws-migration.md) | Migrations, Auth | Textbook gradual ramp-up: 1%→100%, 100ms latency bonus, zero drama |
| [SQS Encryption RBI Compliance](./sqs-encryption-rbi-compliance.md) | Compliance, Infrastructure | 277 queues, 15+ teams, scope reduction as highest-impact contribution |
| [YesBank ACS/FRM Two-Quarter Migration](./yesbank-acs-frm-two-quarter-migration.md) | Banking, Migrations | Zero issues over 6 months — the power of persistent ownership |
| [Merchant Balance Segregation](./merchant-balance-segregation.md) | Data, Financial Systems | Forward-fill + backfill pattern for 100% merchant migration |
| [RDS to Aurora Wallet Migration](./rds-to-aurora-wallet-migration.md) | Databases, Migrations | Progressive validation with dual sanity checks (app + DE pipelines) |

## How to Read These

Each story follows a consistent structure:
1. **STAR Summary** — quick table (Situation, Task, Action, Result)
2. **The Full Story** — narrative with Slack links and timeline
3. **Deep Dive** — technical analysis with diagrams and related concepts
4. **Why This Is Interesting** — analysis of patterns and non-obvious insights
5. **What I Learned** — concrete takeaways table
6. **Key References** — Slack threads, PRs, docs

## Related Learning Topics

Stories reference deeper concept files in the learnings categories:
- [Distributed Systems](/learnings/distributed-systems/_index.md)
- [Go Language](/learnings/golang/_index.md)
- [Infrastructure](/learnings/infrastructure/_index.md)
- [Databases](/learnings/databases/_index.md)
- [AI Engineering](/learnings/ai-engineering/_index.md)
- [Incident Management](/learnings/incident-management/_index.md)
