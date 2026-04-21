# Merchant Balance Segregation — Migrating Every Merchant, Zero Disruption

**Date:** February 2026
**Channel:** `#merchant-balance-segregation`
**Thread:** [Update message](https://razorpay.slack.com/archives/C09H12YA5CZ/p1771923101475139)

---

## STAR Summary

| | |
|---|---|
| **Situation** | All existing merchants needed to be migrated to segregated balances, and new merchants needed auto-onboarding to the new model |
| **Task** | Execute a full merchant base migration to a new balance architecture while ensuring new signups automatically use the new model |
| **Action** | Phased migration of existing merchants + automatic onboarding change for new merchants, with two-track completion |
| **Result** | 100% of existing merchants migrated; new merchants auto-onboarded to segregated balances |

---

## The Full Story

### What is Balance Segregation?

In a payment platform, merchant balances represent the money flowing through the system — collections, settlements, refunds, and reserves. "Balance segregation" separates these into distinct, isolated pools:

```
Before (unified balance):
┌──────────────────────────────┐
│  Merchant Balance             │
│  Collections + Settlements    │
│  + Refunds + Reserves        │
│  = One big number             │
└──────────────────────────────┘

After (segregated):
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Collections   │ │ Settlements  │ │ Reserves     │
│ balance       │ │ balance      │ │ balance      │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Why This Matters

Balance segregation is typically driven by:
- **Regulatory compliance** — RBI requires clear separation of different types of merchant funds
- **Accounting accuracy** — segregated balances reduce reconciliation errors
- **Risk management** — you can see exactly how much is in reserves vs. available for settlement
- **Operational clarity** — support teams can diagnose balance issues faster

### The Migration

Rahul Agarwal reported:

> "We made a good progress on the migration. **It's 100% completed for existing Merchants.** New Merchants are by default onboarded on the segregated balance."

This is a **two-track migration**:

1. **Existing merchants (backfill):** Migrate every existing merchant's balance representation to the new segregated model
2. **New merchants (forward-fill):** Change the onboarding flow so new merchants automatically get segregated balances

Both had to be complete for the migration to be "done."

---

## Why This Is Interesting

### 1. The "migrate everyone, break no one" challenge

Unlike feature launches where you can target a cohort, balance segregation must eventually cover **100% of merchants**. You can't leave 5% of merchants on the old model forever — that creates permanent dual-system maintenance burden.

But migrating financial balances is high-risk:
- A bug could make a merchant's balance appear incorrect
- An incorrect balance could block settlements (merchant doesn't get paid)
- A blocked settlement generates support tickets, escalations, and merchant churn

### 2. The forward-fill + backfill pattern

The two-track approach is a common pattern for migrations:

```
Time →
────────────────────────────────────────────
Track 1 (Forward-fill): New merchants auto-onboard to new model
Track 2 (Backfill):     Existing merchants migrated in batches
────────────────────────────────────────────
                                  ↑
                          Migration complete
                          (both tracks done)
```

**Why start with forward-fill:** It stops the "old model" population from growing. Every new merchant that joins on the old model is one more merchant to backfill later.

**Why backfill takes longer:** Existing merchants have live balances, pending settlements, and in-flight transactions. You can't just flip a switch — you need to wait for quiet periods, verify balances match, and ensure no transactions are in flight.

**Related learning:** [Zero-downtime traffic migration patterns](/learnings/distributed-systems/migrations/topics/zero_downtime_traffic_migration_patterns.md)

### 3. Financial data migration has uniquely high stakes

When you migrate a user's profile picture from one CDN to another, a bug means a broken image. When you migrate a merchant's balance from one model to another, a bug means:
- Merchant sees wrong balance → panic
- Settlement amount is incorrect → legal/financial liability
- Reconciliation fails → accounting team escalation

The verification requirements for financial data migration are an order of magnitude higher than for most other data types.

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Forward-fill + backfill** | Start by onboarding new entities on the new model (stops the bleeding), then backfill existing entities |
| **100% migration mandate** | Financial/regulatory migrations can't leave a long tail — you must eventually migrate everyone |
| **Balance verification** | Financial data migrations require balance verification at every step — you can't rely on "it looks right" |
| **Dual-system maintenance cost** | Every day you maintain both old and new models costs engineering time. Finish the migration completely. |

---

## Key References

- [Rahul's completion update (#merchant-balance-segregation)](https://razorpay.slack.com/archives/C09H12YA5CZ/p1771923101475139)
