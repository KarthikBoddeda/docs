# OpenCode — Open Source AI Coding Tool

**Project**: [opencode-ai/opencode](https://github.com/opencode-ai/opencode)
**Status**: Razorpay piloting as of Mar 2026
**Difficulty**: Medium
**Impact**: Medium-High — organization-wide developer tooling

## What's Happening

Razorpay's AI/developer experience team is actively evaluating **OpenCode** as an open-source alternative to Claude Code. They want to self-host it with multiple model backends.

From Kaushik Bhat in `#ai-code-champions` (Mar 5, 2026):
> "We are enabling a bunch of open source models + opencode. Starting a pilot by Monday. Will include you in the pilot."

From Shashank (CTO-level) in `#pod-velocity-and-ai-working-group`:
> "opencode, etc. are good frontend interface as a replacement for claude code. We should experiment with these in the org. Should host it internally and encourage devs to try out open source options as well."

From Kamalesh in `#ai-code-champions`:
> "I would like to be part of the opencode pilot as well. I think opencode should be the way to go forward, would like to contribute in any way shape or form to make that happen."

## Why This Is an OSS Opportunity

Razorpay has 100+ engineers using AI coding tools daily. From Prabu Ram's engineering-all update:
> "Over the last four weeks, AI adoption across the company has grown exponentially. Across levels and across teams, we have made real progress."

With this many users, Razorpay will quickly surface real bugs and feature gaps in OpenCode. Contributing fixes back would be:
1. High visibility (used by the whole org)
2. Fast feedback loop (immediate user base for testing)
3. Modern stack (Go/TypeScript, AI, developer tools)

## Related Tools Being Evaluated

| Tool | Status | Notes |
|------|--------|-------|
| OpenCode | Piloting | Open source, self-hostable |
| Forge | Mentioned | ZSH integrations, talk to AI from shell |
| Anthropic Agent SDK | Explored | Python/TypeScript only, Go missing |
| Agentura AI | Shared | Open source platform to self-host/manage AI agents |

### Interesting Gap: Go Agent SDK

From Kaushik Bhat:
> "Many python projects getting built in AI-world. Primarily because claude-agent-sdk support only exists in Python/Typescript."

Shashank (CTO):
> "opencode, etc. are good frontend interface as a replacement for claude code."

Razorpay is a Go shop. A Go-native agent SDK or contributing Go support to existing agent frameworks would be huge.

## Slack Threads

| Thread | Channel | What's Discussed |
|--------|---------|-----------------|
| [p1772817878](https://razorpay.slack.com/archives/C08BU395ZEJ/p1772817878295599) | #ai-code-champions | OpenCode pilot announcement |
| [p1772177341](https://razorpay.slack.com/archives/C05L8PNL1MF/p1772177341571419) | #pod-velocity | Shashank on self-hosting open source AI tools |
| [p1772861132](https://razorpay.slack.com/archives/C08BU395ZEJ/p1772861132993719) | #ai-code-champions | Kamalesh volunteering to contribute |
| [p1772187279](https://razorpay.slack.com/archives/C05L8PNL1MF/p1772187279268529) | #pod-velocity | Go Agent SDK gap discussion |
| [p1772039085](https://razorpay.slack.com/archives/C05L8PNL1MF/p1772039085245529) | #engineering-all | AI adoption growth metrics |
| [p1773220446](https://razorpay.slack.com/archives/C08BU395ZEJ/p1773220446394369) | #ai-code-champions | Forge (another OSS alternative) |
| [p1772275422](https://razorpay.slack.com/archives/C08DS8AE7T8/p1772275422927859) | #developer-experience | Agentura AI open source platform |

## Key People

- **Kaushik Bhat** (@kaushik.bhat / kb) — AI strategy, driving OpenCode pilot
- **Shashank** (@shashank) — CTO-level, pushing for open source AI tools
- **Kamalesh S** (@kamalesh.s) — Volunteered to contribute to OpenCode
- **Saurabh Kumar Dixit** (@saurabh.dixit) — Pod velocity, agent projects
- **Amit Kothari** (@amit.kothari) — Claude Code/Vertex AI setup
