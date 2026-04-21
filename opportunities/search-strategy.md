# Search Strategy — How These Opportunities Were Found

Documents the methodology for discovering OSS contribution opportunities from Razorpay's Slack.

## Approach

The search followed a **snowball strategy**: start from a known thread, identify key people and channels, then fan out with targeted queries.

## Phase 1: Starting Point

Started from the user-provided thread:
- **Thread**: https://razorpay.slack.com/archives/C05L8PNL1MF/p1773335832670699
- **Channel**: `#observability_at_razorpay` (C05L8PNL1MF)
- **Context**: Gyan's HyperDX contribution celebrated

### Initial Actions
1. Fetched the thread + all replies (4 replies)
2. Resolved all user IDs to names
3. Fetched the linked PR: https://github.com/hyperdxio/hyperdx/pull/1590
4. Fetched the linked GitHub issue: https://github.com/hyperdxio/hyperdx/issues/1588

## Phase 2: Fan-Out from Key People

Identified key people from the thread:
- **Alok S** (U037VG59JTU) — Posted the original message
- **Gyanendra Singh** (UKPGDG9GB) — The contributor
- **Nandakishore B** (U05GHS728TX) — Asked for the PR

### Search Queries Used

| Query | Channel Filter | Purpose |
|-------|---------------|---------|
| `clickhouse gyan` | C05L8PNL1MF | Find Gyan's ClickHouse involvement |
| `clickhouse` | C05L8PNL1MF | Broader ClickHouse activity |
| `hyperdx` | C05L8PNL1MF | HyperDX discussions |
| `hyperdx contribution` | (all) | Find contribution threads |
| `hyperdx open source` | (all) | OSS discussions about HyperDX |

This revealed the `#tech_articles` thread (C7CFVBLF2) where Alok was encouraging Gyan, which led to the full backstory.

## Phase 3: Broader OSS Discovery

### Keyword-Based Searches (last 6 months)

| Query | Time Range | Results | Key Finds |
|-------|-----------|---------|-----------|
| `open source contribution` | 6m | 50 matches | Mostly internal PR reviews |
| `OSS contribute PR upstream` | 6m | 20 matches | HyperDX upstream sync |
| `clickhouse contribution feature request` | 3m | 30 matches | SLO issue, ClickHouse adoption |
| `open source project razorpay` | 6m | 50 matches | Various internal projects |

### Technology-Specific Searches (last 3 months)

| Query | Results | Key Finds |
|-------|---------|-----------|
| `eBPF odigos contribute` | 30 matches | Bottlerocket incompatibility |
| `TiDB vitess database open source` | 30 matches | Character set blocker |
| `kubernetes istio envoy service mesh` | 30 matches | Mostly operational, not contribution-ready |
| `CNCF open source project interesting` | 30 matches | Mixed results |

### Emerging Tech Searches (last 1-3 months)

| Query | Results | Key Finds |
|-------|---------|-----------|
| `opencode open source AI coding tool` | 30 matches | OpenCode pilot |
| `nexus community agentic MCP` | 30 matches | MCP server ecosystem |
| `Olly2.0 wide event observability ClickHouse` | 30 matches | Olly 2.0 architecture |
| `SLO SLI error budget hyperdx` | C05L8PNL1MF | No in-channel matches (issue is on GitHub) |
| `wide event architecture ClickHouse OTEL` | C05L8PNL1MF | No in-channel matches |
| `agent-sdlc agentic cloud agent skill` | C0AD3SNKGCE | Cloud agent work |
| `hyperdx azure anthropic` | (all) | PR backstory |

## Phase 4: Thread Deep-Dives

For each promising hit, fetched the full thread:

| Thread | Channel | Why |
|--------|---------|-----|
| p1767629907 | #tech_articles | Alok's ClickStack December update — revealed full contribution history |
| p1765850842 | #observability_at_razorpay | HyperDX deployment progress |
| p1753362256 | #observability_at_razorpay | Swiggy meeting — eBPF/wide event background |
| p1773335832 | #observability_at_razorpay | Original thread (starting point) |

## Phase 5: GitHub Issue/PR Analysis

Fetched key GitHub pages for full context:
- https://github.com/hyperdxio/hyperdx/pull/1590 (Gyan's merged PR)
- https://github.com/hyperdxio/hyperdx/issues/1588 (Azure AI issue)
- https://github.com/hyperdxio/hyperdx/issues/1453 (SLO feature request — the big one)

## Channels Explored

| Channel ID | Name | Relevance |
|------------|------|-----------|
| C05L8PNL1MF | #observability_at_razorpay | **Primary** — HyperDX, ClickHouse, OTEL, Odigos |
| C7CFVBLF2 | #tech_articles | **High** — OSS contribution discussions |
| C08BU395ZEJ | #ai-code-champions | **High** — OpenCode, AI tools |
| C08DS8AE7T8 | #developer-experience | **Medium** — AI tooling, agent SDKs |
| C0AFQDKH33N | #agentic-sdlc | **Medium** — Cloud agents, OTEL for AI |
| C09QBCXAHC2 | #clickhouse-poc | **Medium** — ClickHouse setup |
| C0ACJU8JS6Q | #observability-bbplus | **Low** — Specific team observability |

## What Was NOT Searched (Gaps)

The search has blind spots:
1. **Private channels** — Cannot access private/restricted channels
2. **DMs** — Cannot access direct messages
3. **Older than 6 months** — Most searches limited to recent activity
4. **Non-English keywords** — Only searched English terms
5. **Specific team channels** — Did not systematically search every team's channel
6. **GitHub organization-wide** — Did not search razorpay GitHub org for forks with upstream contribution potential
7. **Confluence/Google Docs** — Cannot search internal documentation

## Recommendations for Expanding

To find more opportunities:
1. **Search `#tech_articles` systematically** — Engineers share OSS they're using/hitting issues with
2. **Search for "fork" or "forked"** — Teams maintaining forks likely have upstream contribution potential
3. **Search for "bug" + OSS tool names** — Find real bugs in tools Razorpay uses
4. **Monitor `#observability_at_razorpay`** — Most active OSS contribution channel
5. **Search for "workaround" or "patch"** — Internal workarounds that should be upstreamed
6. **Check Razorpay's GitHub org** — https://github.com/razorpay for public forks
