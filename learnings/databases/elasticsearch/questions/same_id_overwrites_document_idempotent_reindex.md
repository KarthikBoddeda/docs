---
tags: [elasticsearch, document-id, indexing, idempotency, reindex]
status: In Progress
related_topics: []
---

# Same _id overwrites document idempotent reindex

## ❓ The Core Question

> "We use `_id` from our application for every document so that re-indexing is idempotent. ES just overwrites the doc when we send the same `_id` again."
>
> In what sense is that only "partly" true, and what actually happens under the hood on a "same _id" index request?

## 🧠 The Learning Log

*(Refinements, misconceptions, and follow-ups will be added here as we go.)*
