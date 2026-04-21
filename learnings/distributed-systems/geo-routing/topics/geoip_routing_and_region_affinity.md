# Topic: GeoIP Routing and Region Affinity

## Definition

**GeoIP routing** directs incoming requests to the geographically nearest (or contextually appropriate) data center or region based on the client's IP address. **Region affinity** is the property that once a user's data is created in a region, all subsequent requests for that user should be routed to the same region.

## How GeoIP Routing Works

```
Client request (IP: 203.0.113.45)
    ↓
DNS / Edge layer looks up IP → Country: US
    ↓
Route to US region endpoint
    ↓
US region processes request, creates DB entities locally
```

### Common implementations
- **DNS-based:** Route53 geolocation routing, Cloudflare geo-steering
- **Edge proxy-based:** Kong/Nginx at the edge inspects IP and forwards to the right backend
- **Header-based:** Edge injects a region header (e.g., `x-razorpay-user-merchant-region: IN`) and backends respect it

## The Region Affinity Problem

GeoIP routing infers region from the **client's current location**. But a user's data has **permanent region affinity** based on where it was first created:

| Signal | What it tells you | Stable? |
|---|---|---|
| Client IP geolocation | Where the user is *right now* | No — users travel, use VPNs |
| Merchant country code | Where the merchant is *registered* | Yes — doesn't change |
| Entity creation region | Where the data *lives* | Yes — unless migrated |

**The gap:** GeoIP routes based on the *unstable* signal (current IP), but data affinity is based on the *stable* signal (creation region).

## Failure Mode: Cross-Region Entity Split

When GeoIP routing and entity creation region don't match:

```
User signs up from US IP → entities created in US region
User's merchant country = IN → post-login routing goes to IN region
IN region: merchant record ✓, legal entity ✗ (only exists in US)
→ 500 error
```

This is exactly what happened in the [GeoIP Cross-Region Database Ghost](/learnings/stories/geoip-cross-region-database-ghost.md) incident.

## Best Practices

1. **Explicit region context** — don't infer region from IP alone. Pass a region header explicitly (e.g., `x-razorpay-user-merchant-region`).
2. **Region validation at creation time** — when creating entities, verify they'll be reachable from the expected routing path.
3. **Cross-region read fallback** — if an entity isn't found in the routed region, check other regions before returning 404.
4. **Test with geo-diverse clients** — before ramping GeoIP routing, test sign-up and login flows from multiple regions.

## Related

- [Cross-region data consistency](./cross_region_data_consistency.md)
- [Story: GeoIP Cross-Region Database Ghost](/learnings/stories/geoip-cross-region-database-ghost.md)
