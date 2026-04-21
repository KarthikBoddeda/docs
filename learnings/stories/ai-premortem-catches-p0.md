# AI Pre-Mortem Catches P0 Root Cause Before Humans

**Date:** February 26, 2026
**Channel:** `#incident-management`
**Thread:** [Original post](https://razorpay.slack.com/archives/C01J62JFFRT/p1772138425327949)
**Incident PR:** [razorpay/payment-methods#227](https://github.com/razorpay/payment-methods/pull/227/changes)
**Related Incident:** [P0 in #potential_outages](https://razorpay.slack.com/archives/C02B75CA8V9/p1772094168201349)

---

## STAR Summary

| | |
|---|---|
| **Situation** | A P0 incident hit production affecting 13,800+ MIDs in the payment methods service |
| **Task** | Validate whether an AI-powered PR review tool could have caught the bug before it shipped |
| **Action** | Ran the enhanced "Pre-Mortem Skill" against the PR that caused the P0; it correctly identified the root cause |
| **Result** | Proved the AI tool's value for incident prevention; kicked off initiative to train it on historical RCAs |

---

## The Full Story

### The Incident

A P0 incident caused payment method update failures for **13,814 merchant IDs (MIDs)**. The resolution required:
- Identifying and communicating with affected merchants
- Excluding 45 MIDs from the initial set
- Handling 277 MIDs where method updates failed separately
- Mrityunjay Nutan led the resolution communication

### The AI Experiment

After the incident was resolved, Akshay Goyal ran an experiment. Razorpay had been developing an "enhanced Pre-Mortem Skill" — an AI-powered code review tool designed to catch potential production issues before PRs are merged.

He ran the tool against the **exact PR that caused the P0** ([payment-methods#227](https://github.com/razorpay/payment-methods/pull/227/changes)) and shared the results:

> "The enhanced Pre-Mortem Skill was able to catch the root cause of the issues from yesterday's P0 incident, on this PR."

The AI correctly identified what the human RCA team found *after* the outage — but it did so from **just the code diff**.

### The Proposal

Akshay then made a forward-looking proposal:

> "Can you share the repository of all RCA, so that we can train the AI to distil learnings from all past incidents and improve the reviews further? This will ensure similar incidents don't happen multiple times."

He tagged tech leadership (viv, Anand Saha, Prashant Kamboj, Shrey, kb, vikas, Richesh, sp, shk) to get access to the RCA repository.

---

## Deep Dive: AI Pre-Mortem Analysis

### What is a Pre-Mortem Review?

Traditional post-mortem: "What went wrong *after* the incident?"
Pre-mortem: "What *could* go wrong *before* we ship?"

An AI pre-mortem tool:
1. Takes a PR diff as input
2. Analyzes the code changes for potential failure modes
3. Cross-references against known patterns (e.g., race conditions, missing error handling, state machine violations)
4. Generates warnings before the PR is merged

```
┌────────────────┐    ┌───────────────────┐    ┌──────────────────┐
│  PR Code Diff   │───▶│  AI Pre-Mortem     │───▶│  Risk Assessment │
│                 │    │  Skill             │    │  + Warnings      │
│  payment-       │    │                    │    │                  │
│  methods#227    │    │  - Pattern DB      │    │  "This change    │
│                 │    │  - Historical RCAs │    │   could cause    │
│                 │    │  - Domain rules    │    │   method update  │
│                 │    │                    │    │   failures for   │
│                 │    │                    │    │   affected MIDs" │
└────────────────┘    └───────────────────┘    └──────────────────┘
```

**Related learning:** [AI pre-mortem PR review patterns](/learnings/ai-engineering/code-review/topics/ai_premortem_pr_review.md)

### The Feedback Loop Vision

What Akshay proposed is a **learning flywheel**:

```
Incidents happen
    ↓
RCAs are written
    ↓
AI trains on RCA patterns
    ↓
AI reviews future PRs
    ↓
Catches similar bugs before merge
    ↓
Fewer incidents
    ↓
New edge cases create new incidents
    ↓
(cycle repeats with broader coverage)
```

Each incident makes the AI smarter. Over time, the organization's collective debugging wisdom becomes encoded in the review system.

---

## Why This Is Interesting

### 1. Code diffs contain more signal than we think

A human reviewer looking at a PR diff has limited context: they know what changed, maybe some surrounding code, and whatever knowledge they personally carry. The AI tool demonstrated that **the code diff alone** contained enough signal to predict the production failure — no logs, no metrics, no customer reports needed.

This suggests that many production incidents are **foreseeable from the code changes alone**, if reviewed with sufficient domain knowledge and pattern recognition.

### 2. The "organizational memory" problem

Every P0 incident generates learnings. But those learnings live in:
- Post-mortem docs that few people read
- Tribal knowledge in specific engineers' heads
- Slack threads that disappear into the archive

An AI trained on historical RCAs becomes **organizational memory that scales** — it doesn't forget, it doesn't go on leave, and it reviews every PR.

### 3. Closing the loop: incidents → prevention

Most organizations have a gap between "we wrote a post-mortem" and "we actually prevent recurrence." Action items get deprioritized, engineers rotate teams, and the same bug pattern recurs in a different service. An AI pre-mortem tool bridges this gap by **automatically applying past learnings** to new code.

### 4. The 13,814 MID question

If this tool had been in the review pipeline before the PR was merged, could it have prevented the P0? The answer appears to be yes — it caught the root cause from just the diff. That's 13,814 merchants who wouldn't have been affected. The ROI of such a tool is measured in incidents prevented, not lines of code reviewed.

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Pre-mortem > post-mortem** | The most valuable RCA is the one that happens *before* the incident. AI makes this scalable. |
| **Code diffs as predictors** | Production incidents are often foreseeable from the code changes alone — the challenge is having enough context to see the risk. |
| **Organizational memory decay** | Post-mortem learnings are lost to attrition, team rotation, and archive rot. AI can encode them permanently. |
| **Learning flywheel** | Each incident makes the prevention system smarter. The key is feeding RCAs back into the review loop. |

---

## Key References

- [Original Slack thread (#incident-management)](https://razorpay.slack.com/archives/C01J62JFFRT/p1772138425327949)
- [Incident PR: razorpay/payment-methods#227](https://github.com/razorpay/payment-methods/pull/227/changes)
- [Related P0 incident thread](https://razorpay.slack.com/archives/C02B75CA8V9/p1772094168201349)
