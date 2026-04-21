# Topic: Cross-Region Data Consistency

## Definition

**Cross-region data consistency** refers to the challenge of keeping data coherent when entities are spread across multiple geographic regions (e.g., India, US, Singapore), each with its own database.

## The Core Problem

In a multi-region architecture, you face a fundamental tension:

```
                  ┌──── Low latency (read/write locally)
                  │
Multi-region ─────┤
                  │
                  └──── Consistency (all regions see the same data)
```

You can optimize for one, but not both without trade-offs (this is essentially CAP theorem applied geographically).

## Common Multi-Region Data Models

### 1. Single-region primary (all writes go to one region)
```
Write → Region A (primary) → async replicate → Region B, C
Read  → Any region (eventual consistency)
```
**Pros:** Simple consistency model, no write conflicts
**Cons:** Higher write latency for non-primary regions

### 2. Regional primaries (each entity owned by one region)
```
Merchant M1 (India) → writes go to IN region
Merchant M2 (US)    → writes go to US region
```
**Pros:** Low latency for writes, regional data sovereignty
**Cons:** Cross-region queries are expensive, entity creation must be routed correctly

### 3. Multi-primary (any region can write)
```
Write → Any region → conflict resolution → eventual consistency
```
**Pros:** Lowest write latency everywhere
**Cons:** Conflict resolution is complex, risk of divergent state

## Failure Modes

### Split-brain entities
When parts of an entity (e.g., merchant record in Region A, legal entity in Region B) are created in different regions due to routing inconsistency. This was the root cause of the [GeoIP Cross-Region Database Ghost](/learnings/stories/geoip-cross-region-database-ghost.md).

### Stale reads after failover
After a region failover, the new primary may not have the latest writes from the old primary. Reads return stale data until replication catches up.

### Orphaned entities
An entity is created in Region A, but the user is subsequently always routed to Region B. The entity in Region A becomes invisible and orphaned.

## Mitigation Strategies

| Strategy | How it helps |
|---|---|
| **Explicit region headers** | Prevents GeoIP from routing entity creation to the wrong region |
| **Cross-region read fallback** | If entity not found locally, check other regions before 404 |
| **Entity-region registry** | Central lookup mapping entity IDs to their home region |
| **Creation-time validation** | Verify all dependent entities will be created in the same region |
| **Replication lag monitoring** | Alert when cross-region replication falls behind threshold |

## Related

- [GeoIP routing and region affinity](./geoip_routing_and_region_affinity.md)
- [Story: GeoIP Cross-Region Database Ghost](/learnings/stories/geoip-cross-region-database-ghost.md)
