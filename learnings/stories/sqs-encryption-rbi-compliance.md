# SQS Encryption Enablement — 277 Queues, 15+ Teams, One RBI Deadline

**Date:** January–February 2026
**Channel:** `#potential_outages`
**Thread:** [Original post](https://razorpay.slack.com/archives/C02B75CA8V9/p1769164909992679)
**Completion:** [Monica's announcement](https://razorpay.slack.com/archives/C02B75CA8V9/p1770361580808489)
**Ownership sheet:** [Queue ownership spreadsheet](https://docs.google.com/spreadsheets/d/1adTGr1ryUjNWhZaEz0LjhCa6kWtwRahnTBxocSay91c/edit)

---

## STAR Summary

| | |
|---|---|
| **Situation** | RBI audit finding required encryption-at-rest for all active SQS queues — 277 queues across 15+ teams with a hard Feb 1 deadline |
| **Task** | Enable server-side encryption on 277 production SQS queues without breaking any asynchronous payment flows |
| **Action** | Ashwath scoped down from all queues to 277 active ones; Rajeev and Anks led execution; Terraform upgrades, blanket ICR, team-by-team rollout |
| **Result** | All 277 queues encrypted on time, zero incidents, RBI finding closed |

---

## The Full Story

### The Mandate

An RBI audit finding required **encryption-at-rest** for all active SQS queues. At a fintech processing billions in transactions, SQS queues carry sensitive payment data — order details, refund callbacks, settlement notifications. Unencrypted queues were a compliance risk.

### The Scale of the Problem

Initial assessment:
- Total SQS queues in the estate: **hundreds**
- Active queues with live traffic: **277**
- Number of owning teams: **15+**
- Many queues had **no assigned owner**
- Some queues were managed by Terraform (Vishnu), others were manually created
- Hard deadline: **February 1, 2026**

### The Challenges

#### 1. The "275 queues with no owner" problem

When Monica Vemula kicked off the effort, 275 out of 277 queues initially had **no SPOCs assigned**. Nobody knew who owned what. This is a common problem in large organizations — infrastructure grows organically, teams change, and queue ownership becomes tribal knowledge.

#### 2. The Friday-before-long-weekend timing

When the IM team tried to engage engineering POCs for stage testing, the call summary captured the reality:

> "Most team representatives indicate they cannot complete testing immediately due to lack of context on the queues, need for developer support, concerns about affecting critical asynchronous payment flows, and the timing being a Friday before a long weekend."

#### 3. Terraform version mismatch

The Terminals team discovered that enabling encryption via Terraform required **upgrading from Terraform <0.14 to 0.14+** in atlantis.yaml. This wasn't just a config change — it was a toolchain upgrade with its own testing requirements.

#### 4. The "blanket ICR" decision

With 277 queues, individual ICR (Infrastructure Change Request) approvals were impractical. The team had to convince approvers to issue a **blanket ICR** covering all queues — a policy decision, not just a technical one.

### How They Pulled It Off

| Phase | What happened |
|---|---|
| **Scope reduction** | Ashwath Kumar K analyzed all queues and reduced scope to 277 active ones — eliminating test, internal, and stale queues |
| **Owner assignment** | Monica drove ownership assignment via spreadsheet, escalating through team leads |
| **Terraform fix** | DevOps upgraded Terraform version, enabling teams to self-serve encryption via Vishnu |
| **Stage testing** | First queue tested on staging (prod-payments-bank-transfer) |
| **Blanket ICR** | Abhishek Prakash prepared ICR for all 200+ queues |
| **Prod rollout** | Teams deployed via Vishnu; DevOps handled non-Terraform queues |
| **Verification** | Each queue verified post-encryption |

### The Celebration

Monica's announcement:

> "SQS Queues — Encryption Enablement Completed!
>
> I would like to sincerely thank everyone involved in the successful closure of this **critical RBI finding**. This was a high-impact effort, and the collaboration and ownership across teams made this possible."

She specifically called out:
- **Rajeev** and **Anks** — end-to-end ownership and heavy lifting
- **Ashwath Kumar K** — initial analysis that reduced scope and focused effort
- **Saif, Pranav, Sid, Sreenadh, Sagar, Sarthak, Abhishek** — execution through closure
- **Prabu Ram, Viv, Praveen, Anand Saha, Ashish, Tushar** — leadership support

---

## Why This Is Interesting

### 1. The "who owns this queue?" problem at scale

In a company with 176+ microservices, infrastructure ownership decays over time. Teams create queues, then reorg, and the queue outlives its creator. This project forced a **fleet-wide ownership audit** — which is valuable beyond encryption. Now every active queue has an assigned owner.

**Related learning:** [Infrastructure fleet-wide compliance patterns](/learnings/infrastructure/compliance/topics/fleet_wide_compliance_patterns.md)

### 2. Scope reduction as the most valuable contribution

Ashwath's initial analysis didn't write a single line of code. He just analyzed which queues were active, which had traffic, and which were test/internal. This reduced the scope from "hundreds" to 277 — making the project feasible within the timeline. **The most impactful contribution to a project is often reducing its scope.**

### 3. Compliance-driven engineering is a different beast

Unlike feature work where you can ship incrementally and iterate, compliance work has:
- A **hard deadline** (RBI doesn't negotiate)
- A **binary outcome** (compliant or not)
- **Multi-team coordination** (you can't just own your part)
- **Zero tolerance for breakage** (the queues carry payment data)

This creates a unique project management challenge: you need the urgency of an incident response with the planning horizon of a feature project.

### 4. The Terraform toolchain upgrade cascade

A seemingly simple change (enable encryption) required upgrading Terraform versions, which required updating atlantis.yaml, which required testing the upgrade, which unblocked all teams. This **toolchain dependency** is a hidden tax on compliance work — you don't just change the config, you upgrade the tool that manages the config.

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Scope reduction > scope completion** | Reducing 277 queues from hundreds saved more time than any optimization would have |
| **Fleet ownership audits** | Large compliance projects force ownership clarity — treat this as a permanent benefit, not a one-time cost |
| **Blanket ICR for fleet-wide changes** | When changing 200+ resources identically, get a single approval rather than 200+ individual ones |
| **Toolchain dependencies** | Infrastructure changes often cascade into tool upgrades — account for this in timelines |
| **Compliance project management** | Hard deadlines + multi-team coordination + zero breakage tolerance = need incident-level urgency with project-level planning |

---

## Key References

- [Original thread (#potential_outages)](https://razorpay.slack.com/archives/C02B75CA8V9/p1769164909992679)
- [Monica's completion announcement](https://razorpay.slack.com/archives/C02B75CA8V9/p1770361580808489)
- [Anand Saha's scoping questions](https://razorpay.slack.com/archives/C02B75CA8V9/p1769505795624099)
- [Call summary — Friday timing challenge](https://razorpay.slack.com/archives/C02B75CA8V9/p1769173321965149)
- [Encryption enablement steps](https://razorpay.slack.com/archives/C02B75CA8V9/p1769492459316989)
- [Thread summary by Chronos](https://razorpay.slack.com/archives/C02B75CA8V9/p1769589515967279)
- [Queue ownership spreadsheet](https://docs.google.com/spreadsheets/d/1adTGr1ryUjNWhZaEz0LjhCa6kWtwRahnTBxocSay91c/edit)
