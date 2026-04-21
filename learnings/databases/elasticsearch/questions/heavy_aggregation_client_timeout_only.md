---
tags: [elasticsearch, aggregations, timeout, circuit-breaker, memory]
status: In Progress
related_topics: []
---

# Heavy aggregation increase client timeout only

## ❓ The Core Question

> "We run a heavy aggregation on a 100M-document index. We're fine with 30–60 second latency, so we don't need to optimize the query—we'll just increase the client timeout."
>
> What can still go wrong even if the client is patient?

## 🧠 The Learning Log

*(Refinements, misconceptions, and follow-ups will be added here as we go.)*
