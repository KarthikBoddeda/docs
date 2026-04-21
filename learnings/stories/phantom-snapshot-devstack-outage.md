# The Phantom Snapshot — When Automation Eats Infrastructure

**Date:** February 17, 2026
**Channel:** `#platform-devstack`
**Thread:** [Original post](https://razorpay.slack.com/archives/C024Y4GAW8N/p1771384552105599)
**Ticket:** TKT-4544100

---

## STAR Summary

| | |
|---|---|
| **Situation** | Pods stuck in Pending state for 30+ minutes across devstack; no deployments going through |
| **Task** | Identify why Kubernetes nodes couldn't provision when no one made infrastructure changes |
| **Action** | Traced to an internal automation that accidentally deleted an AMI snapshot referenced by ASG launch templates |
| **Result** | Affected ASGs updated, nodes resumed provisioning, devstack restored |

---

## The Full Story

### What Happened

Ayush Yadav reported to `#platform-devstack`:

> "Pods are not getting deployed and have been in the Pending state for the last 30 minutes. Label: ayush123"

This wasn't a single service — it was **infrastructure-wide**. Pods across multiple services couldn't schedule because new Kubernetes nodes weren't coming up.

### The Investigation

Parag Dudeja from the platform team dug in and traced the failure chain:

```
Internal cleanup automation runs
    ↓
Deletes an AMI snapshot (mistakenly — snapshot was still in use)
    ↓
ASG launch templates reference the deleted snapshot
    ↓
ASG tries to launch new EC2 instances
    ↓
Launch fails: "snapshot not found"
    ↓
No new nodes join the Kubernetes cluster
    ↓
Pending pods have nowhere to schedule
    ↓
All deployments across devstack stall
```

### The Fix

Parag identified all affected Auto Scaling Groups, removed the deleted snapshot reference from their launch templates, and pointed them at a valid snapshot. New nodes started coming up and pods moved out of Pending state.

### The Aftermath

Even after the fix, ripple effects continued:
- Abhishek Mishra reported e2e tests still failing due to pods not coming up
- The payments-cross-border service was among those affected
- Some teams had to re-trigger their deployment pipelines

---

## Deep Dive: The AMI/ASG/Launch Template Dependency Chain

### How AWS Auto Scaling Groups work

```
┌─────────────────────┐
│   Auto Scaling Group │
│   (ASG)              │
│                      │
│   "I need N nodes"   │
│         ↓            │
│   Launch Template    │
│   - AMI ID ──────────┼──→ AMI (Amazon Machine Image)
│   - Instance Type    │         ↓
│   - Security Groups  │    EBS Snapshot(s)
│   - User Data        │    (root volume, data volumes)
└─────────────────────┘
```

When an ASG needs to scale out:
1. It reads the **Launch Template** for the instance configuration
2. The Launch Template references an **AMI** (the disk image to boot from)
3. The AMI is backed by **EBS Snapshots** (the actual disk data)
4. If any snapshot in the chain is deleted → **launch fails**

**Related learning:** [ASG launch template AMI dependencies](/learnings/infrastructure/aws-autoscaling/topics/asg_launch_template_ami_dependency.md)

### Why automation deleted a live snapshot

Snapshot cleanup automations typically:
1. List snapshots older than N days
2. Check if they're referenced by any AMI
3. Delete unreferenced ones

The gap: **checking AMI references isn't enough**. You also need to check:
- Launch Templates referencing the AMI
- ASGs referencing those Launch Templates
- **Even deregistered AMIs** whose snapshots might be needed for rollback

This is the classic "reference counting is hard" problem applied to infrastructure.

**Related learning:** [Destructive automation safeguards](/learnings/infrastructure/aws-autoscaling/topics/destructive_automation_safeguards.md)

---

## Why This Is Interesting

### 1. The invisible dependency chain

The person who wrote the cleanup automation likely thought: "If no AMI references this snapshot, it's safe to delete." But the dependency chain is deeper: `ASG → Launch Template → AMI → Snapshot`. Deleting a snapshot at the bottom of this chain breaks everything above it, but the breakage is **delayed** — it only manifests when the ASG next tries to scale out.

### 2. "No one made any changes" — the most dangerous statement

The report was "pods are stuck and no one changed anything." In fact, something *did* change — an automated process deleted a resource. But since it was automation, no human was aware. This is a recurring pattern in infrastructure incidents: **automated systems making changes that humans don't track**.

### 3. Blast radius of infrastructure-level bugs

A single deleted snapshot affected **every team** using devstack. Application-level bugs are scoped to a service; infrastructure-level bugs are scoped to an **entire environment**. This asymmetry means infrastructure automation needs disproportionately more safety checks.

### 4. The delayed-fuse failure mode

The snapshot was deleted at some point before the incident. But the failure only appeared when the ASG tried to provision new nodes. If the cluster had enough spare capacity, the bug could have remained latent for days or weeks. This "delayed fuse" pattern makes root-causing harder because the trigger event is temporally separated from the symptom.

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Deep dependency chains** | Infrastructure resources have multi-layer dependencies (ASG → Launch Template → AMI → Snapshot). Deleting any layer breaks everything above. |
| **Automation needs guardrails** | Destructive automations must verify the full dependency tree, not just immediate references. Add dry-run modes and alerts. |
| **Delayed-fuse failures** | Some infrastructure failures only manifest when a resource is next *used*, not when it's *broken*. The time gap makes RCA harder. |
| **Blast radius asymmetry** | Infrastructure bugs affect entire environments, not individual services. Safety investment should be proportional to blast radius. |

---

## Key References

- [Original Slack thread (#platform-devstack)](https://razorpay.slack.com/archives/C024Y4GAW8N/p1771384552105599)
- [Parag Dudeja's resolution message](https://razorpay.slack.com/archives/C024Y4GAW8N/p1771390358551059)
- [Follow-up: e2e tests still failing](https://razorpay.slack.com/archives/C024Y4GAW8N/p1771398322031829)
