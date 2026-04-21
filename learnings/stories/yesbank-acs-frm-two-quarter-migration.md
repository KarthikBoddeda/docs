# YesBank ACS/FRM Migration — Two Quarters, Zero Issues

**Date:** Q3–Q4 2025 (completed February 2026)
**Channel:** `#yesbank-acs-frm`
**Thread:** [Original post](https://razorpay.slack.com/archives/C0754S8M2F9/p1766051708452129)
**Completion:** [Sambit's message](https://razorpay.slack.com/archives/C0754S8M2F9/p1770352853361669)

---

## STAR Summary

| | |
|---|---|
| **Situation** | YesBank's ACS (Access Control Server) and FRM (Fraud Risk Management) needed migration — a critical banking infrastructure project spanning two quarters |
| **Task** | Execute a multi-quarter migration involving banking partner coordination, DevOps, and development teams — with zero tolerance for payment failures |
| **Action** | Strong ownership model with seamless DevOps-Dev coordination; systematic rollout over 6 months |
| **Result** | Completed with zero issues; celebrated for "strong ownership and seamless coordination" |

---

## The Full Story

### What is ACS/FRM?

In card payment processing:
- **ACS (Access Control Server)** handles 3D Secure authentication — the "Verified by Visa" or "Mastercard SecureCode" step that protects against unauthorized card use
- **FRM (Fraud Risk Management)** evaluates transaction risk in real-time — deciding whether to approve, challenge, or decline a payment

Both are **critical path** for card payments. Any failure in ACS means customers can't complete 3DS authentication. Any failure in FRM means either fraud slips through or legitimate transactions get blocked.

### The Migration Challenge

Migrating ACS/FRM for a major issuing bank (YesBank) is not a simple code deployment:

```
Old ACS/FRM system
    │
    │  Must maintain during migration:
    │  - Zero authentication failures
    │  - Zero false fraud declines
    │  - Sub-second response times
    │  - Regulatory compliance (PCI-DSS, RBI)
    │
    ▼
New ACS/FRM system
```

Key constraints:
- **Zero downtime** — card payments can't stop processing
- **Banking partner coordination** — YesBank has their own testing and approval cycles
- **Regulatory requirements** — ACS is audited by card networks (Visa, Mastercard)
- **Two-quarter timeline** — this is long enough to lose momentum, short enough to feel the deadline

### The Execution

Sambit Mallick summarized it at completion:

> "The migration spanning the last two quarters has been completed successfully with **zero issues.**
> This was driven by strong ownership and seamless coordination between DevOps and Development teams."

The thread tagged both DevOps and Dev teams, plus leadership (Varun Saluja, Avinash Gupta, Prashant Kamboj, Nikhil Sharma, etc.) — signaling this was a cross-functional effort with executive visibility.

---

## Why This Is Interesting

### 1. "Zero issues" over two quarters is the real achievement

Two quarters is ~6 months. In that time, teams rotate, priorities shift, holidays happen, and other incidents compete for attention. Maintaining a clean migration over this period requires:
- **Persistent ownership** — someone needs to own the project through the full timeline, not just their sprint
- **Incremental validation** — each step must be verified before the next
- **Regression protection** — existing functionality can't break while new capabilities are added

### 2. The DevOps-Dev coordination pattern

Sambit specifically called out "seamless coordination between DevOps and Development teams." In banking infrastructure migrations, this coordination is critical because:
- **Dev** understands the application logic (auth flows, risk models)
- **DevOps** understands the infrastructure (networking, TLS, load balancing, DNS)
- **The migration touches both** — you're changing application behavior AND infrastructure routing

When these two teams are misaligned, you get: deploys that break networking, infrastructure changes that break app behavior, or (worst case) both breaking simultaneously.

### 3. Banking infrastructure is unforgiving

Unlike most software projects where you can ship a bug and hotfix it, banking infrastructure failures have immediate regulatory and financial consequences:
- A broken ACS = customers can't authenticate = payment failures = merchant complaints + RBI scrutiny
- A broken FRM = fraud slips through = financial losses + compliance violations
- Both systems require **PCI-DSS compliance** even during migration

This is why two quarters for "zero issues" is genuinely impressive — the margin for error is essentially zero.

### 4. The long project momentum problem

Short projects (1-2 sprints) have natural urgency. Long projects (2 quarters) risk:
- **Priority erosion** — newer projects steal attention
- **Context loss** — people forget why decisions were made
- **Ownership diffusion** — "isn't someone else handling that?"

The fact that this project maintained momentum through two quarters speaks to strong project ownership and regular cadence.

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Banking infra migration** | ACS/FRM migrations are zero-tolerance: no downtime, no auth failures, no fraud leaks. Plan accordingly. |
| **Two-quarter discipline** | Long projects need persistent ownership, weekly status cadence, and exec visibility to avoid momentum loss. |
| **DevOps-Dev alignment** | Banking infrastructure changes touch both app logic and infra config. Misalignment between teams = breakage. |
| **"Zero issues" as a metric** | In critical-path banking systems, "zero issues" over 6 months is the gold standard. It means preparation was excellent. |

---

## Key References

- [Migration thread (#yesbank-acs-frm)](https://razorpay.slack.com/archives/C0754S8M2F9/p1766051708452129)
- [Sambit's completion message](https://razorpay.slack.com/archives/C0754S8M2F9/p1770352853361669)
