# The Americana/Mashreq Marathon — 48 Hours Awake

**Date:** January 2026
**Channel:** `#potential_outages`
**Thread:** [Original post](https://razorpay.slack.com/archives/C02B75CA8V9/p1768557839190359)
**Shoutout:** [Avinash's message](https://razorpay.slack.com/archives/C02B75CA8V9/p1768581950377769)

---

## STAR Summary

| | |
|---|---|
| **Situation** | Critical integration issue with Americana (major merchant) involving the Mashreq bank processing path |
| **Task** | Diagnose and fix a persistent bank integration bug requiring cross-company coordination with Mashreq |
| **Action** | VP-led marathon debugging sessions spanning 2 days, with an engineer staying awake for 48+ hours |
| **Result** | Root cause identified, Mashreq team engaged for fix, issue tracked to closure |

---

## The Full Story

### What Happened

A critical issue emerged in the payment processing path for Americana — a major merchant — involving the Mashreq bank integration. The exact technical details of the failure aren't fully public in the thread, but the scope was significant enough that VP Avinash Gupta personally escalated and rallied a core team.

### The Marathon

This wasn't a "fix it in an hour" kind of problem. The debugging required:

1. **Cross-company coordination** — the fix needed Mashreq (external banking partner) to cooperate
2. **Deep protocol-level debugging** — understanding the exact failure mode in the bank integration
3. **High-stakes merchant relationship** — Americana is a significant account, so resolution time mattered

The team that assembled:

| Engineer | Role |
|---|---|
| **Nikku** (@nikku) | Lead debugger — stayed awake for ~48 hours |
| **Razvi** (@razvi) | Tracked the issue to closure |
| **Amit Kumar Dewangan** | Extended debugging sessions |
| **Mithun Patil** | Extended debugging sessions |
| **Avinash Gupta** (VP) | Escalation and coordination |

Avinash's message in the thread captures the intensity:

> "Thanks Razvi, Nikku, Amit Kumar Dewangan, Mithun Patil for the marathon session today. **Nikku: you have been awake for large part of last two days** but I hope, all this work will help us resolve Americana issue for good. Let's work with Mashreq team to fix the issue."

### Why Cross-Company Debugging Is Brutal

When the bug lives at the **boundary** between your system and an external partner's system:

```
┌─────────────────┐     ┌──────────────────┐
│  Razorpay        │────▶│  Mashreq Bank    │
│  (your logs,     │     │  (their logs,    │
│   your code,     │◀────│   their code,    │
│   your control)  │     │   their schedule)│
└─────────────────┘     └──────────────────┘
      ↑                         ↑
  Full visibility          Black box
  Full control             Meeting-gated
```

- You can't read their logs
- You can't deploy fixes to their side
- You can't reproduce in isolation (need their sandbox)
- Debugging requires **synchronized availability** across companies
- Time zones, on-call schedules, and org politics all add friction

**Related learning:** [Structured cross-company debugging](/learnings/incident-management/process/topics/structured_cross_company_debugging.md)

---

## Why This Is Interesting

### 1. Human endurance as an engineering variable

Software engineering rarely talks about physical endurance. But in high-stakes incident response, **the ability to sustain focus over 48 hours** is a genuine differentiator. Nikku's marathon wasn't just heroic — it was likely the only way to maintain the debugging context across multiple sessions with the banking partner.

Context switching is the enemy of deep debugging. By staying on the problem continuously, Nikku avoided the hours of "where was I?" ramp-up that would have fragmented the investigation.

### 2. VP-level escalation changes the dynamics

When a VP personally joins the incident thread and thanks individual engineers by name, it signals:
- The problem matters organizationally (not just technically)
- Engineers have air cover to work extended hours
- The cross-company partner (Mashreq) will take the issue seriously

### 3. "Track to closure" as a role

Razvi's role — tracking the issue to closure — is underrated. In multi-day incidents, someone needs to own the **state machine**: what's been tried, what's pending, who's blocked on what, and what the next handoff looks like. Without this, marathon sessions devolve into re-explaining the same context.

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Cross-company debugging** | External integrations are black boxes — plan for it with structured logging at the boundary |
| **Context continuity** | In multi-day incidents, someone staying on the problem continuously avoids catastrophic context loss |
| **Incident coordinator role** | Explicitly assign a "track to closure" person who owns the state machine of the investigation |
| **Escalation as enablement** | Leadership joining the thread isn't micromanagement — it's signaling priority and providing air cover |

---

## Key References

- [Original thread (#potential_outages)](https://razorpay.slack.com/archives/C02B75CA8V9/p1768557839190359)
- [Avinash's shoutout](https://razorpay.slack.com/archives/C02B75CA8V9/p1768581950377769)
