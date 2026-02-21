# Task 005: Kong Edge Routing for Payment Handle APIs

**Created:** 2026-02-21  
**Status:** 🟢 Completed  
**Priority:** P0  
**DevRev:** [ISS-1604278](https://app.devrev.ai/razorpay/works/ISS-1604278)  
**PR:** [terraform-kong#8736](https://github.com/razorpay/terraform-kong/pull/8736)  
**Branch:** `feat/payment-handle-nca-routing`  

---

## What This Task Does

Adds Kong route definitions and `upstream-override` plugins for all 6 payment handle APIs to enable routing through NCA (`no-code-apps-service`) for the 100% dual write milestone.

| Route Name | Method | Path |
|------------|--------|------|
| `payment_handle_create` | POST | `/v1/payment_handle` |
| `payment_handle_update` | PATCH | `/v1/payment_handle` |
| `payment_handle_get` | GET | `/v1/payment_handle` |
| `payment_handle_suggestion` | GET | `/v1/payment_handle/suggestion` |
| `payment_handle_availability` | GET | `/v1/payment_handle/:slug/exists` |
| `payment_handle_amount_encryption` | POST | `/v1/payment_handle/custom_amount` |

---

## Rollout Strategy

Each `upstream-override` plugin has two conditions:

| Condition | Match | Rollout | Purpose |
|-----------|-------|---------|---------|
| 1 (priority=1) | Header `X-NoCodeApps-Routing: nocodeapps` | 1 (100%) | Internal test routing — always routes to NCA |
| 2 (priority=2) | None (general traffic) | 0 (disabled) | **Set to 1 to enable production dual write** |

To enable 100% dual write in production: update `rollout = 0` → `rollout = 1` in condition 2 for `payment_handle_create` and `payment_handle_update`.

---

## Pre-requisites Before Enabling Production Rollout

1. NCA PRs merged: #1006, #1007, #1008
2. Monolith PR merged: api#64786
3. Real Splitz experiment created for `payment_handle_proxy_state` (replace dummy experiment name in config)
4. Data migration of existing payment handles to NCA DB
