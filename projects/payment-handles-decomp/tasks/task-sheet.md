# Payment Handles Decomp — Task Sheet & Follow-up Questions

This file tracks open questions and unclear tasks for the payment handles decomposition.

## Open Questions

### Q1: Payment Handle Experiment Setup
**Context:** NCA PR 1 uses a dummy experiment name `payment_handle_proxy_state` for the splitz experiment.
**Question:** What is the correct Splitz experiment name/ID to use for payment handle proxy state?
**Action needed:**
1. Create a new Splitz experiment (similar to PP's `PpAafnXN2nt8GZ`)
2. Update `PaymentHandleProxyStateExperimentName` in NCA config (`internal/config/config.go`)
3. Update the env var in all environments

**Related:** NCA PR 1 comment `// TODO: Replace dummy value with actual experiment ID`

---

### Q2: Scope of getPaymentHandleByMerchant Callers
**Context:** `getPaymentHandleByMerchant` is called from multiple places in the monolith:
- `Merchant/Core.php::getPaymentHandleDynamicProps` (dashboard slug display)
- `Merchant/Detail/Core.php::getSegmentEventParams` (segment analytics)

**Question:** Are there any other callers of `getPaymentHandleByMerchant` or `getPaymentHandle` that need to be routed through NCA? Should we run a full codebase grep?

```bash
grep -rn "getPaymentHandleByMerchant\|getPaymentHandle\b" app/ --include="*.php"
```

---

### Q3: payment_handle_create via PaymentLinkController
**Context:** Currently `PaymentLinkController::createPaymentHandle` also exists as a direct API endpoint (`POST /v1/payment_handle`) in the monolith. When a merchant calls this endpoint directly (not via activation), it goes to the old Service path.
**Question:** Should `PaymentLinkController::createPaymentHandle` also call `createPaymentHandleNCA` instead of `createPaymentHandle`? Or is this only called during activation?

---

### Q4: Diff Configuration for payment_handle_create and payment_handle_update
**Context:** Diff configs need to be registered in `internal/monolith_decomp/diffs/configs.go` so the dual-write handler can calculate and log diffs between monolith and NCA responses.
**Question:** What fields should be compared? Known fields from monolith response: `id`, `slug`, `url`, `title`, `status`, `view_type`. Are there any fields that should be excluded from diff comparison?

---

### Q5: NCA-only migration path for payment handles
**Context:** Payment handles are simpler than payment pages (no line items, no order creation). Can we move to `nca_only` faster (skipping some intermediate states)?
**Question:** Is `dual_write_shadow_read_no_external` state required for handles? Or can we go directly from `dual_write_no_reads_no_external` to `nca_only`?

---

### Q6: Merchant Config / Merchant Settings in NCA for Handles
**Context:** In the monolith, the handle's slug is stored in merchant settings (`default_payment_handle` key), NOT in the payment_pages table. NCA currently stores it only as part of the entity's `short_url`.
**Question:** Does NCA need to replicate the merchant settings structure for handle slug lookup, or can it use the entity's `short_url` field directly? What's the read path for getting a merchant's handle slug in NCA?

---

### Q7: payment_handle_update scope
**Context:** `PATCH /v1/payment_handle` in the monolith updates the handle's slug/title/settings. But the update goes through the same `payment_handle` entity.
**Question:** What is the full list of fields that `payment_handle_update` can modify? Is slug update a separate flow or part of the same PATCH endpoint?

---

## Resolved

_(None yet)_
