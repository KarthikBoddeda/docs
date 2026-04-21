# Odigos — eBPF Auto-Instrumentation + Bottlerocket OS

**Project**: [odigos-io/odigos](https://github.com/odigos-io/odigos) (Go, eBPF)
**Status**: Razorpay shifted to enterprise version due to OSS limitations
**Difficulty**: Very High (kernel-level eBPF programming)
**Impact**: High — would unblock OSS adoption for any org running Bottlerocket

## Why This Matters to Razorpay

Razorpay's platform team (Parth Anand, Saijal) evaluated Odigos for auto-instrumentation — getting distributed traces from all services without code changes. The promise: function-level instrumentation with zero code modification.

### What Went Wrong with OSS

From Parth Anand in `#observability_at_razorpay`:
> "Open source tools for eBPF based are not compatible on bottlerocket OS and context propagation was also breaking in many services for them. Hence we shifted to enterprise where they built product for bottlerocket."

Key issues:
1. **Bottlerocket OS incompatibility** — Razorpay runs Amazon Bottlerocket (container-optimized Linux) on EKS. Open source Odigos doesn't support it.
2. **Context propagation breaking** — Trace context wasn't propagating correctly across service boundaries in many Razorpay services.

### Enterprise Workaround

They moved to Odigos Enterprise which has Bottlerocket support. From Avinash Gupta:
> "Good to see that Parth Anand and Saijal's conviction about value of Odigos is getting validation from other places also. They also got convinced once they saw the engineering strength of Odigos team."

## What Could Be Contributed

### 1. Bottlerocket OS Support (High Impact)
Bottlerocket uses a read-only root filesystem, no package manager, and a different kernel module loading mechanism. eBPF probes need to be adapted for:
- Different filesystem layout
- Limited kernel headers availability
- Bottlerocket-specific security constraints

### 2. Context Propagation Fixes
Cross-service trace context propagation is fragile when auto-instrumented. Specific issues:
- HTTP header propagation across Go services
- gRPC metadata forwarding
- Async queue message context (SQS, Kafka)

## Technical Context

From the [evaluation doc](https://docs.google.com/document/d/1Z-vXAnKf6gjoDO4HnkjOlvw0No2efimRmDx6qO2WCF0/edit) shared by Parth:
- Multiple open source eBPF tools evaluated
- All had missing pieces for Razorpay's infra
- Odigos was the most promising but Bottlerocket was the deal-breaker

### Nanda's Critique (Key Insight)

From Nandakishore B:
> "Although auto-instrumentation is great, the absence of an integrated UI for correlation is a drawback. With New Relic, the function-level instrumentation was paired with a user-friendly, cohesive UI. Odigos pushes UI responsibility to external tracing tools like Jaeger or Coralogix."
> "The true value of observability isn't just in the data we emit, it's in having an intuitive UI that reveals patterns and relationships within that data."

This is partly why HyperDX was chosen as the UX layer — combining Odigos traces with HyperDX visualization.

## Slack Threads

| Thread | Channel | What's Discussed |
|--------|---------|-----------------|
| [p1767851914](https://razorpay.slack.com/archives/C05L8PNL1MF/p1767851914084469) | #observability_at_razorpay | Parth on Bottlerocket incompatibility |
| [p1767854911](https://razorpay.slack.com/archives/C05L8PNL1MF/p1767854911291049) | #observability_at_razorpay | Razvi's perspective on Odigos vs Olly2.0 |
| [p1767946241](https://razorpay.slack.com/archives/C05L8PNL1MF/p1767946241835719) | #observability_at_razorpay | Avinash on Odigos enterprise conviction |
| [p1753362256](https://razorpay.slack.com/archives/C05L8PNL1MF/p1753362256886769) | #observability_at_razorpay | Swiggy meeting, eBPF evaluation context |
| [p1772454282](https://razorpay.slack.com/archives/C05L8PNL1MF/p1772454282572659) | #tech_e2e_stability_program | Odigos temporarily disabled |

## Key People

- **Parth Anand** (@parth.anand) — Led eBPF/Odigos evaluation
- **Saijal** (@saijal) — Co-evaluated with Parth
- **Nandakishore B** (@nandakishore.b) — Provided critical UX feedback
- **Avinash Gupta** (@avinash.gupta) — Leadership support
