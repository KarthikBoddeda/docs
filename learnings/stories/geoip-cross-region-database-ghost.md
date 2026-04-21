# The GeoIP Cross-Region Database Ghost

**Date:** February 26, 2026
**Channel:** `#potential_outages`
**Thread:** [Original post](https://razorpay.slack.com/archives/C02B75CA8V9/p1772119948349139)
**Incident:** INC-14426 (P1-S4, rejected — no payment impact)

---

## STAR Summary

| | |
|---|---|
| **Situation** | US-based merchants signing up on RazorpayX dashboard got 500 errors on login; existing US merchants couldn't reach their dashboard |
| **Task** | Diagnose a cross-region routing bug across multi-service, multi-region infra without disrupting live transacting merchants |
| **Action** | Cross-functional war room (10+ engineers), systematic reproduction, root-caused to GeoIP ramp-up creating entities in the wrong region |
| **Result** | Fix deployed next day, 81 users affected (onboarding only), zero payment disruption |

---

## The Full Story

### What Happened

Indian merchants on RazorpayX were fine. But merchants logging in from the US started hitting two issues:

1. **Issue 1 (Higher Priority):** US merchants who completed onboarding on `x.razorpay.com` couldn't navigate to the dashboard. Clicking "Navigate to Dashboard" after login returned a **500 Internal Server Error**.
2. **Issue 2:** New US merchants attempting signup couldn't complete registration. After entering a correct email OTP, they got an error — the merchant details API was failing with "ID does not exist".

### The Investigation

Kailash Atal raised the alarm. The IM bridge was stood up, and the warroom started pulling in people:

- **Arshpreet Wadehra** — led the triaging effort
- **Raghav Dang** — incident coordination and comms
- **Shubham Choudhary** — joined from the connected experience team
- **Babajan Patan** — deployed the fix
- **Yamuna Bharani** — i18n/onboarding domain expert
- Plus members from partnership-US, merchant experience, and platform teams

The key breakthrough came when Arshpreet **created a reproducible scenario**: he traced what happens when a sign-up request originates from a US IP address.

### Root Cause: The GeoIP Routing Trap

The root cause was a subtle interaction between **three independent systems** that each worked correctly in isolation:

```
┌──────────────────────────────────────────────────────┐
│  US-based user opens x.razorpay.com                  │
│  ↓                                                    │
│  GeoIP ramp-up → routes request to US region          │
│  ↓                                                    │
│  Signup API processes in US → creates legal entity     │
│  in US database                                       │
│  ↓                                                    │
│  Merchant country = IN (X is India-only product)      │
│  ↓                                                    │
│  Post-login: requests routed to India (country=IN)    │
│  ↓                                                    │
│  India DB: merchant exists ✓, legal entity? ✗ (404)   │
│  ↓                                                    │
│  500 Internal Server Error                            │
└──────────────────────────────────────────────────────┘
```

**The chain of causation:**

1. **GeoIP ramp-up** was recently enabled — requests from US IPs now routed to the US region (previously everything went to India)
2. **Signup happened in US region** — DB entities (legal entity, etc.) were created in the US database
3. **Merchant was tagged as IN** — because X Dashboard is an India-only product
4. **Post-login routing used country code** — so subsequent requests went to the India region
5. **Cross-region mismatch** — merchant record existed in India, but legal entity only existed in US. The `merchant_details` API tried to fetch the legal entity in India and got "ID does not exist"

### The Fix

Arshpreet identified that the fix was surprisingly simple:

> Every fetch request from X dashboard should have this header: `x-razorpay-user-merchant-region: IN`

Since X is currently India-only, hardcoding the region header ensures all entity creation routes to India regardless of where the user physically is. Babajan and team raised a PR, tested, and deployed the next morning after AD+ approval.

### Impact

- **81 users** affected (upper bound)
- All were **onboarding users**, not transacting merchants
- **Zero payment disruption**
- Logged as P1-S4, rejected as formal incident since no business disruption

---

## Why This Is Interesting

### 1. Emergent behavior from independent correct systems

None of the three systems were "buggy":
- GeoIP routing was working correctly (route US traffic to US)
- Signup was working correctly (create entities in the processing region)
- Post-login routing was working correctly (route based on merchant country)

The bug only emerged from their **interaction**. This is the hallmark of distributed systems complexity — each component is correct, but the composition is broken.

**Related learning:** [Cross-region data consistency in multi-region architectures](/learnings/distributed-systems/geo-routing/topics/cross_region_data_consistency.md)

### 2. The "who owns the region context?" question

The fundamental issue: **who is responsible for carrying region context?** The GeoIP layer inferred region from IP. The signup layer created entities locally. The login layer inferred region from merchant data. No single system owned the truth about "this merchant's data lives in India."

**Related learning:** [GeoIP routing and region affinity](/learnings/distributed-systems/geo-routing/topics/geoip_routing_and_region_affinity.md)

### 3. The ramp-up triggering latent bugs

The bug was **latent** — it always existed conceptually, but was never triggered because all traffic previously went to India. The GeoIP ramp-up was the catalyst. This is a classic pattern: feature flags and gradual rollouts can expose edge cases that never manifested before.

### 4. Systematic reproduction was the breakthrough

Arshpreet didn't just hypothesize — he created a **reproducible test case** proving the exact failure path. In incident response, the ability to reproduce consistently is what separates a 2-hour RCA from a 2-day RCA.

---

## What I Learned

| Concept | Takeaway |
|---|---|
| **Emergent failures** | Distributed systems break at the seams, not in individual components |
| **Region ownership** | In multi-region architectures, every request needs explicit region context — inference from IP or country code is fragile |
| **Gradual rollouts exposing latent bugs** | Feature flags can activate dormant code paths; test edge cases before ramping |
| **Reproduction is king** | In RCA, the fastest path to a fix is creating a reproducible scenario |

---

## Key References

- [Original Slack thread (#potential_outages)](https://razorpay.slack.com/archives/C02B75CA8V9/p1772119948349139)
- [Deployment thread](https://razorpay.slack.com/archives/C0123GJPYCE/p1772127817632249)
- [RCA by Shubham Choudhary](https://razorpay.slack.com/archives/C02B75CA8V9/p1772128770203089)
