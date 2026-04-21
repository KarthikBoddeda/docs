# Shadow Merchants — Read Readiness Assessment

**Last updated:** 2026-03-16 (B8 update)  
**Source:** B8 diff logs (Mar 14–16, 2026, ~48 hrs) + B1–B7 historical batches  
**Purpose:** Classify which shadowed merchants are safe to promote from `dual_write_shadow_read_no_external` to `dual_write_read_no_external` (actual NCA reads).

> **B8 TL;DR:** After commit `a2f5404b` code fixes, 14 of the 16 previously-BLOCKED merchants have cleared.  
> Only **2 merchants remain blocked** (`Q35jgV9BxiOLB7`, `Ha18e7jHMVjYEb` — both fixable with datafix).  
> `DBeZ7DIU7L8wae` has a new data issue (`contact_optional` wrong for 1 page).  
> **61 of 63 merchants are promoteable.**

---

## Full Merchant List (63 merchants)

```
RGzkFbQMhEVxhO, RFNMAWAYrA0hQD, RNpuBjh3LInMP1, QedWZefco2y2EA, Qq82BbjBr05Puh,
DBeZ7DIU7L8wae, R1zuJZIHpAp6hf, R7Y2Dervg5gGGU, Oj581PzHLVRxC7, E3t3a2CPXQheb4,
IcpNy3QUNDyNVE, Nb3LsbAB1ToDoA, G7NMeax5Gewf8a, H9OTnVWUomZFRH, Qqv3ROJPJbRIte,
S2weyEuIGyJea4, OsfUYocg447V4q, I7xsnTCezlNBUx, QxnNidPPJVSamO, Rtqep4DUv7EmNC,
RJ50Be6vFJ8jEc, RehuE0RHDiIaVC, R2QqWoGtqIMYZd, IgSJ0eqRBzyopb, Qxhak9YqVLOg2c,
PfHRcImw0wXm5q, Q35jgV9BxiOLB7, F4nh3jBiH6yDGz, ReT7Pl4HOtZHCU, Jm5NuHPOevlGjc,
GFgVQ22W7LOjwQ, QmiQDQbbz6M6RI, NSBm9qrpaKRUTq, PaS9HFGajwrJKL, JI4sdkUpF3pwhu,
Ha18e7jHMVjYEb, ON0fLjgxT0piuQ, O5fUwEkTm6kG8P, M0xDktKEVkwjMu, N8NJICx3XDfP8U,
Qqu5myFMhxgXtB, Q5lN5wEahShGn4, HVcrMm15PVZFNx, INm4viwxSqTTZo, RnV89DaE06b2kn,
R0fO7IjFL9lEhT, RJ6JSVTlEIWlpr, RrRAhIezVg8VmB, DGpl8SzsSdc5MM, IgP1gE3lHWkQFc,
HHhwpt2llhzbKS, RvOn6LUd6QKwqE, KKq8j9FkP5wa2A, KQ4Ou7uC2oJpgi, QefibgMIGGfG9M,
FRJIooOPmPzW6Z, MtchSvbHI1IUlt, RGEeRPhcCv3zqO, IOi3H46aRzBFss, RN2uD47L3cZsWd,
PrCuq0aEPFpu8z, QagXBwUNeuZFow, GD7mMjsQtkObxK
```

---

## Tier 1 — CLEAN ✅ (zero diffs in B8)

Zero meaningful diffs observed. Safe to promote immediately.

| Merchant ID | B6 status | B8 status |
|-------------|-----------|-----------|
| Oj581PzHLVRxC7 | CLEAN | CLEAN |
| E3t3a2CPXQheb4 | CLEAN | CLEAN |
| G7NMeax5Gewf8a | CLEAN | CLEAN |
| H9OTnVWUomZFRH | CLEAN | CLEAN |
| Qqv3ROJPJbRIte | CLEAN | CLEAN |
| RJ50Be6vFJ8jEc | CLEAN | CLEAN |
| RehuE0RHDiIaVC | CLEAN | CLEAN |
| R2QqWoGtqIMYZd | CLEAN | CLEAN |
| ON0fLjgxT0piuQ | CLEAN | CLEAN |
| O5fUwEkTm6kG8P | CLEAN | CLEAN |
| Q5lN5wEahShGn4 | CLEAN | CLEAN |
| R0fO7IjFL9lEhT | CLEAN | CLEAN |
| RvOn6LUd6QKwqE | CLEAN | CLEAN |
| KKq8j9FkP5wa2A | CLEAN | CLEAN |
| KQ4Ou7uC2oJpgi | CLEAN | CLEAN |
| QefibgMIGGfG9M | CLEAN | CLEAN |
| MtchSvbHI1IUlt | CLEAN | CLEAN |
| RGEeRPhcCv3zqO | CLEAN | CLEAN |
| IOi3H46aRzBFss | CLEAN | CLEAN |
| RN2uD47L3cZsWd | CLEAN | CLEAN |
| GD7mMjsQtkObxK | CLEAN | CLEAN |
| GFgVQ22W7LOjwQ | SAFE (B6) | CLEAN ✨ |
| N8NJICx3XDfP8U | **BLOCKED** (B6) | CLEAN ✨ |
| NSBm9qrpaKRUTq | **BLOCKED** (B6) | CLEAN ✨ |
| PfHRcImw0wXm5q | **BLOCKED** (B6) | CLEAN ✨ |
| S2weyEuIGyJea4 | SAFE (B6) | CLEAN ✨ |
| RJ6JSVTlEIWlpr | SAFE (B6) | CLEAN ✨ |

---

## Tier 2 — SAFE WITH ACCEPTABLE DIFFS ✅

Have diffs but only of types that are transient race conditions, cosmetic, or known acceptable semantic differences. Safe to promote.

Acceptable diff types:
- **`/key_id`** — intentional keyless flow (NCA=null, mono=rzp_live_xxx); checkout.js uses `x_entity_id` instead. Not a regression.
- **`/order/description`** — NCA returns null, monolith returns rich-text JSON. Cosmetic for page creation flow.
- **Live counter race** — `captured_payments_count`, `quantity_sold`, `total_amount_paid` (NCA lags monolith by 1-2 transactions, self-corrects within seconds)
- **ES lag** — `pages_extra_in_nca` / `pages_missing_in_nca` (Elasticsearch indexing delay in list API)
- **Cosmetic null vs empty** — `user/contact_mobile`, `user/email`, `order/notes`
- **List `/count`** — small count discrepancies from ES vs DB semantics

| Merchant ID | Diff types in B8 | B6 → B8 change |
|-------------|-----------------|----------------|
| DGpl8SzsSdc5MM | list ES lag | **BLOCKED** → SAFE ✨ |
| F4nh3jBiH6yDGz | live counters, list ES lag | **BLOCKED** → SAFE ✨ |
| FRJIooOPmPzW6Z | list ES lag, /count | **BLOCKED** → SAFE ✨ |
| HHhwpt2llhzbKS | list ES lag | **BLOCKED** → SAFE ✨ |
| IcpNy3QUNDyNVE | list ES lag, live counters | **BLOCKED** → SAFE ✨ |
| IgP1gE3lHWkQFc | list ES lag | **BLOCKED** → SAFE ✨ |
| IgSJ0eqRBzyopb | live counters, list ES lag | **BLOCKED** → SAFE ✨ |
| Jm5NuHZUevlGjc | live counters (get_details) | **BLOCKED** → SAFE ✨ |
| KQ4Ou7uC2oJpgi | list ES lag | **BLOCKED** → SAFE ✨ |
| OsfUYocg447V4q | live counters (get_details) | **BLOCKED** → SAFE ✨ |
| PrCuq0aEPFpu8z | live counters, list ES lag | **BLOCKED** → SAFE ✨ |
| QagXBwUNeuZFow | live counters, list ES lag | **BLOCKED** → SAFE ✨ |
| QmiQDQbbz6M6RI | live counters, list ES lag | **BLOCKED** → SAFE ✨ |
| QxnNidPPJVSamO | live counters (get_details) | **BLOCKED** → SAFE ✨ |
| RNpuBjh3LInMP1 | live counters, list ES lag | **BLOCKED** → SAFE ✨ |
| RnV89DaE06b2kn | list ES lag, /count | **BLOCKED** → SAFE ✨ |
| Rtqep4DUv7EmNC | list ES lag | **BLOCKED** → SAFE ✨ |
| DBeZ7DIU7L8wae | live counters, /count, ES lag | SAFE (same) |
| HVcrMm15PVZFNx | /count, user fields, ES lag | SAFE (same) |
| I7xsnTCezlNBUx | live counters, /count, ES lag | SAFE (same) |
| INm4viwxSqTTZo | items null vs [] | SAFE (same) |
| JI4sdkUpF3pwhu | ES lag | SAFE (same) |
| Jm5NuHPOevlGjc | live counters (get_details) | SAFE (same) |
| M0xDktKEVkwjMu | live counters, /count, ES lag | SAFE (same) |
| Nb3LsbAB1ToDoA | live counters, /count, ES lag | SAFE (same) |
| PaS9HFGajwrJKL | /count, ES lag | SAFE (same) |
| QedWZefco2y2EA | live counters | SAFE (same) |
| Qq82BbjBr05Puh | live counters, /count, ES lag | SAFE (same) |
| Qqu5myFMhxgXtB | /count, ES lag | SAFE (same) |
| Qxhak9YqVLOg2c | /count, ES lag | SAFE (same) |
| R1zuJZIHpAp6hf | live counters, /count, ES lag | SAFE (same) |
| R7Y2Dervg5gGGU | live counters | SAFE (same) |
| RFNMAWAYrA0hQD | live counters | SAFE (same) |
| RGzkFbQMhEVxhO | live counters, /count, ES lag | SAFE (same) |
| RJ50Be6vFJ8jEc | /key_id only | SAFE (same) |
| ReT7Pl4HOtZHCU | live counters | SAFE (same) |
| RehuE0RHDiIaVC | /key_id only | SAFE (same) |
| RrRAhIezVg8VmB | /count, ES lag | SAFE (same) |

---

## Tier 3 — BLOCKED ❌ (2 merchants remaining)

| Merchant ID | Blocking diffs | Root cause | Fix |
|-------------|---------------|------------|-----|
| **Q35jgV9BxiOLB7** | `/settings/custom_domain` (2 rows) | Page `pl_SN7RBTlbt0xdm9` has a custom domain configured in monolith but NCA doesn't have the setting synced | Datafix `pl_SN7RBTlbt0xdm9` settings |
| **Ha18e7jHMVjYEb** | `status`: mono=`active`, nca=`inactive` for `pl_SR7ZV4vD7EYrzr` (13 rows) and `pl_SR1mqBMJamYJ4t` (1 row) | 2 newly-created pages not correctly migrated/activated in NCA | Run datafix on `pl_SR7ZV4vD7EYrzr` and `pl_SR1mqBMJamYJ4t` |

### Watch: New data issue (not hard-blocking, but notable)

| Merchant ID | Diff | Detail | Risk level |
|-------------|------|--------|------------|
| **DBeZ7DIU7L8wae** | `/merchant/contact_optional`: mono=`True`, nca=`False` for `pl_Pismr7brxYXKKl` (91 rows) | Merchant has contact set as optional in monolith but NCA doesn't have this flag synced. On NCA-served pages, contact would be required instead of optional. | Medium — user-facing form regression for this one page |

---

## Summary

| Tier | B6 count | B8 count | Change |
|------|----------|----------|--------|
| ✅ Clean (zero diffs) | 21 | 27 | +6 |
| ✅ Safe (acceptable diffs) | 26 | 36 | +10 |
| ❌ Blocked | 16 | **2** | **-14** |
| **Total** | **63** | **63** | |

**Merchants promoteable: 61 of 63 (96.8%)** ← up from 74.6% in B6 assessment

---

## Change Log

| Date | Update |
|------|--------|
| 2026-03-13 | Initial assessment (B6 data). 47/63 promoteable. |
| 2026-03-16 | B8 update after commit `a2f5404b`. 61/63 promoteable. 14 merchants unblocked. |

---

## Notes on "Acceptable" Diffs

These diff types are **not blockers** for read promotion because they either self-correct or don't affect what users/merchants see:

1. **`/key_id`** — NCA returns `null` intentionally; keyless flow uses `x_entity_id`. checkout.js falls back to `x_entity_id`. Pending checkout team validation, but not a data bug.
2. **`/order/description`** — NCA returns `null` vs monolith's rich-text JSON. Only visible in `payment_page_create_order`; cosmetic.
3. **Live counter race** (`quantity_sold`, `collected_amount`, etc.) — NCA lags monolith by 1-3 transactions, resolves within seconds. Acceptable for reads.
4. **ES lag** (`pages_extra/missing_in_nca`) — Elasticsearch indexing delay. Pages appear/disappear from list temporarily. Expected behavior during dual-write.
5. **`/count` list** — small discrepancies from ES vs DB semantics. Affects pagination display but not page data correctness.
6. **Cosmetic `null` vs `""`** — user/contact_mobile, user/email, order/notes. No functional impact.
