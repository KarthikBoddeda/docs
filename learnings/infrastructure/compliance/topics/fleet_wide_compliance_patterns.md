# Fleet-Wide Compliance Patterns

## What is it?

Strategies for executing mandatory changes (usually regulatory or security) across an entire infrastructure fleet — hundreds of resources, dozens of teams, hard deadlines.

## Why it matters

Compliance findings from regulators like RBI come with non-negotiable deadlines. Unlike feature work where you can negotiate scope, compliance is binary: done or not done. Missing the deadline has legal and financial consequences.

## The Pattern

### Phase 1: Scope and Audit

Before writing any code, understand the actual scope:

1. **Inventory** — list all affected resources
2. **Classify** — active vs. inactive, production vs. test, managed vs. unmanaged
3. **Assign owners** — every resource needs a human owner
4. **Reduce scope** — eliminate test, stale, and internal resources that don't need compliance treatment

**Example:** In the [SQS Encryption project](/learnings/stories/sqs-encryption-rbi-compliance.md), Ashwath's initial analysis reduced scope from "hundreds" of queues to 277 active ones — making the project feasible.

### Phase 2: Toolchain Validation

Fleet-wide changes often hit toolchain limitations:
- Terraform version requirements
- Policy-as-code constraints
- ICR approval workflows not designed for batch changes

**Validate the tool can execute the change** before asking teams to start. In the SQS project, teams discovered they needed a Terraform upgrade before they could even enable encryption.

### Phase 3: Blanket Approval

When changing 200+ identical resources in the same way, individual ICRs (change requests) are impractical. Get a **blanket approval** with:
- Clear scope definition
- Rollback plan
- Monitoring plan
- Single responsible owner

### Phase 4: Execution with Ownership

Two approaches:

| Approach | When to use |
|---|---|
| **Team self-service** | Resources managed by Terraform; teams apply their own changes |
| **Centralized execution** | Resources not managed by IaC; central team applies changes |

Most fleet-wide projects are a mix of both.

### Phase 5: Verification

Post-change verification per resource:
- Confirm the change took effect (encryption enabled, policy applied, etc.)
- Confirm no degradation in service health
- Update the tracking spreadsheet

## The Ownership Problem

The biggest challenge in fleet-wide compliance is **ownership**. Resources created 3 years ago by a team that no longer exists have no natural owner. Solutions:

1. **Service catalog ownership** — every resource maps to a service, every service maps to a team
2. **Tag-based ownership** — AWS tags indicating team ownership
3. **Escalation chains** — if no owner is found, escalate to the group/sub-group lead
4. **Default owners** — infrastructure team owns unowned resources by default

## Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Individual ICRs for identical changes | Creates 200+ approval bottlenecks |
| Starting on Friday before a long weekend | Teams can't test, timelines slip |
| Assuming all resources are IaC-managed | Manual resources need different handling |
| No ownership tracking | Resources slip through the cracks |

## Related Stories

- [SQS Encryption RBI Compliance](/learnings/stories/sqs-encryption-rbi-compliance.md) — 277 queues, 15+ teams, one RBI deadline
