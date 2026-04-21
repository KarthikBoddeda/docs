---
tags: [kubernetes, hpa, autoscaling, cpu, scaling]
status: Answered
topics:
  - [hpa_target_cpu_utilization_percentage](../topics/hpa_target_cpu_utilization_percentage.md)
---

# HPA targetCPUUtilizationPercentage — what does it mean and what are the tradeoffs?

## ❓ The Core Question

What exactly is `targetCPUUtilizationPercentage` in a Kubernetes HPA? Is it a percentage of the node's CPU, or the pod's CPU limit, or something else? And what's the tradeoff between a lower vs higher value?

## 🧠 The Learning Log

### Initial Understanding

Assumed it was a percentage of the node's total CPU, or the pod's CPU limit.

### 🔄 Refinement: It's a percentage of `requests`, not limits or node CPU

**My Misconception:** Thought the target percentage was relative to the node's available CPU or the pod's CPU limit.

**The Correction:** It's a percentage of the pod's **CPU request**. With `api_requests_cpu: 200m` and `targetCPUUtilizationPercentage: 40`, HPA tries to keep average CPU at `40% × 200m = 80m` per pod.

**Key Insight:** This means the `requests` value directly drives the HPA scaling math. An unrealistically low `requests` (e.g. `100m`) makes HPA think pods are much more loaded than they are, causing over-scaling.

### Scale-out formula

```
desired_replicas = ceil(current_replicas × current_avg_cpu / target_avg_cpu)

# Example: 10 pods, target = 80m, actual total = 1200m
desired = ceil(10 × 1200 / 800) = 15 pods
```

### 🔄 Refinement: Lower target ≠ always better

**My Misconception:** Lower target percentage is always safer because it scales out sooner.

**The Correction:** Lower target can cause HPA flapping — if CPU hovers near the target threshold, HPA oscillates between scaling in and out. Kubernetes mitigates this with a 5-minute scale-down stabilization window by default, but it's still a concern.

**Key Insight:** The right target depends on context. During a known traffic surge, 40% makes sense to scale proactively. In steady state, 50% avoids unnecessary churn. Revisit with real utilization data post-rollout.

### Real example that prompted this

Pre-scaling NCA pods for a 5x hosted page traffic surge (20% → 100% rollout). Lowered from 50% → 40% to get earlier scale-out during the burst. Also raised `api_requests_cpu` from 100m → 200m to make the request realistic and fix the HPA math.
