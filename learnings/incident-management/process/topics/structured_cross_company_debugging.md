# Topic: Structured Cross-Company Debugging

## Definition

**Cross-company debugging** is the process of diagnosing issues that span organizational boundaries — where part of the system is owned by your team and part is owned by an external partner (bank, payment gateway, vendor). It requires structured communication and shared context because you can't read their logs or deploy fixes to their code.

## Why Cross-Company Debugging Is Hard

```
┌─────────────────┐     ┌──────────────────┐
│  Your System     │────▶│  Partner System   │
│                  │     │                   │
│  ✓ Full logs     │     │  ✗ No log access  │
│  ✓ Full code     │◀────│  ✗ No code access │
│  ✓ Deploy anytime│     │  ✗ Deploy windows │
│  ✓ Direct DB     │     │  ✗ API only       │
│  ✓ Instant comms │     │  ✗ Meeting-gated  │
└─────────────────┘     └──────────────────┘
```

### The friction points

| Factor | Internal debugging | Cross-company debugging |
|---|---|---|
| **Log access** | Full access | API response codes only |
| **Code access** | Full codebase | Documentation (often stale) |
| **Deploy speed** | Minutes | Days to weeks (their release cycle) |
| **Communication** | Slack message, instant | Email → meeting → follow-up (days) |
| **Reproduction** | Full control | Depends on their sandbox availability |
| **Root cause verification** | Deploy fix, observe | Ask them to check, wait for response |

## A Structured Approach

### Phase 1: Isolate the boundary

Before involving the partner, prove the issue is on their side:

```
1. Capture the full request/response at the boundary
2. Validate your request matches their API spec
3. Check if the error is intermittent or consistent
4. Test with their sandbox (if available)
5. Check their status page for known issues
```

### Phase 2: Build the evidence package

Partners respond faster to well-documented issues:

| Include | Why |
|---|---|
| **Exact timestamps** (UTC) | They can correlate with their logs |
| **Request IDs / trace IDs** | Direct lookup in their system |
| **Full request payload** (redacted) | They can replay the request |
| **Expected vs actual response** | Clear description of the bug |
| **Frequency and impact** | Helps them prioritize |

### Phase 3: Maintain context continuity

In multi-day cross-company debugging:

1. **Assign a "track to closure" owner** — one person who owns the full state machine of the investigation
2. **Maintain a shared timeline doc** — chronological log of what was tried, what was found, who responded
3. **Minimize handoffs** — every handoff loses context. If possible, keep the same person on both sides
4. **Escalate with data, not frustration** — partner engineering teams respond to evidence, not urgency

### Phase 4: Parallel tracks

Don't block on the partner:

```
Track 1: Wait for partner's response / fix
Track 2: Build a workaround on your side
Track 3: Explore alternate partners / paths
```

## The "48-Hour Engineer" Pattern

From the [Americana/Mashreq Marathon](/learnings/stories/americana-mashreq-marathon.md): sometimes the most effective strategy is having one engineer stay on the problem continuously across multiple partner interaction windows.

**Why it works:**
- Zero context-switch overhead between sessions
- The engineer builds a mental model that spans both systems
- Partner interactions are more productive because the engineer remembers every detail

**Why it's costly:**
- Unsustainable for more than 48-72 hours
- Risk of errors from fatigue
- Should be a last resort, not a default strategy

## Related

- [Story: Americana/Mashreq Marathon](/learnings/stories/americana-mashreq-marathon.md)
