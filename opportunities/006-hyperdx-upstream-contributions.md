# HyperDX — Upstream Contributions (Ongoing)

**Project**: [hyperdxio/hyperdx](https://github.com/hyperdxio/hyperdx) (9K stars, TypeScript)
**Status**: Active — Razorpay team is already contributing
**Difficulty**: Low to Medium (individual PRs)
**Impact**: Medium — features Razorpay needs in production

## Background

Razorpay deployed HyperDX as the UX layer for their ClickHouse-based observability stack. They maintain a [Razorpay fork](https://github.com/razorpay/hyperdx) with custom patches and regularly contribute features upstream.

## Contributions Already Made

### 1. Multi-Provider AI Support (Merged)
- **PR**: [#1590 — feat: extending AI support for multi-providers](https://github.com/hyperdxio/hyperdx/pull/1590)
- **Author**: Gyanendra Singh (@gyancr7)
- **Merged**: Jan 21, 2026
- **What**: Added Azure AI Anthropic support + extensible multi-provider architecture
- **Featured in**: [ClickHouse January 2026 blog](https://clickhouse.com/blog/whats-new-in-clickstack-january-2026)

### 2. Configuration Toggle for Live Tail
- **Author**: Alok S (@alok87)
- **Status**: Merged (Dec 2025 ClickStack update)
- **What**: Simple configuration toggle

### 3. Chart Label Filters (Merged)
- **PR**: [#1572](https://github.com/hyperdxio/hyperdx/pull/1572)
- **What**: Tile chart label filters for dashboard UX

### 4. Full Screen View (Merged)
- **PR**: [#1581](https://github.com/hyperdxio/hyperdx/pull/1581)
- **Author**: Alok S
- **What**: Full screen view support for dashboards

### 5. Tile Filters
- **PR**: [#1568](https://github.com/hyperdxio/hyperdx/pull/1568)
- **Author**: Alok S
- **What**: Tile-level filters like other UX tools

## Open Opportunities in HyperDX

Beyond the big SLO feature (#1453), there are smaller but useful contributions:

### Features Razorpay Wants
1. **SLO/SLI/Error Budgets** — See [001-hyperdx-slo-sli-error-budgets.md](./001-hyperdx-slo-sli-error-budgets.md)
2. **Apdex Score** — @sgarfinkel mentioned they have it in their fork and were planning to open a PR
3. **ClickHouse Official Operator Support** — Currently using a manual/custom setup

### Fork Management

From the tech_articles thread, Alok asked Gyan:
> "I was thinking instead of back merge should we rebase master or we should cherry pick what we built on top of their master."

Gyan's response:
> "If we rebase commit history will not be maintained."

They're currently using back-merge strategy for keeping the Razorpay fork in sync with upstream. Gyan is automating PR creation for upstream sync:
> "First we need to raise a PR against master with the upstream commits, we can automate the PR creation and posting on slack."

## HyperDX Discord

Alok shared the HyperDX Discord link for community engagement: https://discord.gg/FErRRKU78j

## Slack Threads

| Thread | Channel | What's Discussed |
|--------|---------|-----------------|
| [p1773335832](https://razorpay.slack.com/archives/C05L8PNL1MF/p1773335832670699) | #observability_at_razorpay | Gyan's contribution celebrated |
| [p1767629907](https://razorpay.slack.com/archives/C7CFVBLF2/p1767629907809939) | #tech_articles | Full contribution history, fork management |
| [p1767805023](https://razorpay.slack.com/archives/C7CFVBLF2/p1767805023285669) | #tech_articles | Alok encouraging Gyan with PR examples |
| [p1767894062](https://razorpay.slack.com/archives/C7CFVBLF2/p1767894062949089) | #tech_articles | Chart label filter PR, AI deployment |
| [p1773392461](https://razorpay.slack.com/archives/C05L8PNL1MF/p1773392461852779) | #observability_at_razorpay | Upstream sync discussion |

## How to Get Involved

1. **Check HyperDX issues**: https://github.com/hyperdxio/hyperdx/issues
2. **Join Discord**: https://discord.gg/FErRRKU78j
3. **Follow Razorpay fork**: https://github.com/razorpay/hyperdx
4. **Talk to**: Alok S (@alok.s) or Gyanendra Singh (@gyanendra.singh) in #observability_at_razorpay
