# Topic: AI Pre-Mortem PR Review

## Definition

**AI pre-mortem PR review** is the practice of using AI/LLM-powered tools to analyze pull request diffs and predict potential production failures *before* the code is merged — turning post-mortem analysis into a preventive measure.

## Pre-Mortem vs Post-Mortem

| | Post-Mortem | Pre-Mortem |
|---|---|---|
| **When** | After the incident | Before the code ships |
| **Input** | Logs, metrics, customer reports | Code diff, PR context |
| **Output** | Root Cause Analysis (RCA) | Risk assessment, warnings |
| **Cost of being wrong** | Missed learning | False positive (minor friction) |
| **Value** | Prevents recurrence of *this* bug | Prevents *similar* bugs from shipping |

## How It Works

```
┌────────────────┐    ┌───────────────────────┐    ┌──────────────────┐
│  PR Code Diff   │───▶│  AI Pre-Mortem Engine  │───▶│  Risk Assessment │
│                 │    │                        │    │                  │
│  + PR description│    │  Components:           │    │  - Risk level    │
│  + File context  │    │  - LLM (Claude/GPT)   │    │  - Failure modes │
│  + Test changes  │    │  - Pattern DB from RCAs│    │  - Suggestions   │
│                 │    │  - Domain rules         │    │                  │
└────────────────┘    └───────────────────────┘    └──────────────────┘
```

### Input signals the AI uses

1. **Code diff** — what changed (additions, deletions, modifications)
2. **File context** — surrounding code (imports, function signatures, error handling patterns)
3. **Historical patterns** — known failure patterns from past RCAs
4. **Domain rules** — payment-specific constraints (idempotency, atomicity, state machine validity)

### What it catches

| Pattern | Example | Why AI catches it |
|---|---|---|
| **Missing error handling** | New API call without error check | Pattern: all external calls need error handling |
| **State machine violations** | Allowing invalid status transitions | Trained on past state-related incidents |
| **Race conditions** | Concurrent access without locks | Pattern: shared state + concurrent access |
| **Data type mismatches** | Using int where int64 is needed | Pattern: overflow-prone operations |
| **Missing idempotency** | Retry-able operation without idempotency key | Domain rule: all payment mutations need idempotency |

## The Learning Flywheel

The key insight from the [AI Pre-Mortem Catches P0](/learnings/stories/ai-premortem-catches-p0.md) incident: the AI can be **trained on historical RCAs** to continuously improve:

```
Incidents happen
    ↓
RCAs are written (root cause, contributing factors, fix)
    ↓
AI ingests RCA patterns
    ↓
AI reviews future PRs with expanded pattern library
    ↓
Catches similar bugs before merge
    ↓
Fewer incidents (but new edge cases emerge)
    ↓
New RCAs feed back into the system
    ↓
(flywheel accelerates)
```

Each incident makes the organization's code review **permanently smarter**.

## Challenges

### False positives
AI may flag code that looks risky but is actually correct. Too many false positives lead to alert fatigue and engineers ignoring the tool.

**Mitigation:** Confidence scoring, thumbs-up/down feedback loop, focus on high-severity patterns only.

### Context limitations
AI sees the diff but may not understand the full system architecture (e.g., "this service is behind a rate limiter, so the race condition is actually safe").

**Mitigation:** Provide architectural context via system descriptions, service dependency maps, or RAG over internal docs.

### Organizational memory decay without AI
Post-mortem learnings are lost to:
- Engineer attrition (people leave, knowledge leaves)
- Team rotation (new team doesn't know old team's incidents)
- Archive rot (docs exist but nobody reads them)

AI pre-mortem tools solve this by **encoding learnings into an active review process** that runs on every PR.

## Related

- [Story: AI Pre-Mortem Catches P0](/learnings/stories/ai-premortem-catches-p0.md)
- [Story: ChiragBot Digital Twin](/learnings/stories/chiragbot-digital-twin.md)
