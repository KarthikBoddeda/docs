# Payment Page ACTIVATE & DEACTIVATE Flow Audit

**Context:** Validating safety of moving merchants to `dual_write_read_no_external` proxy state.  
**Date:** 2025-02-17

---

## 1. Activate Flow Comparison

### Monolith Activate (Core.php lines 964–1013)

**Exact order of operations:**

1. **Lock** – `lockForUpdateAndReload($paymentLink)` (inside transaction)
2. **Validate (pre-edit)** – `validateActivateOperation()` (rejects if already active)
3. **Edit input** – `$paymentLink->edit($input)` — applies `expire_by` (and other fields) from input to entity **before** second validation
4. **Validate (post-edit)** – `validateShouldActivationBeAllowed()` — validates stock, times_payable (V1), and **expire_by** (uses entity’s value, which now includes the new expire_by from edit)
5. **Change status** – `changeStatus($paymentLink, Status::ACTIVE, null)`
6. **Save** – `saveOrFail($paymentLink)`
7. **Post-save** – `dispatchHostedCache($paymentLink)`

**Important:** `edit($input)` applies the new `expire_by` to the entity before `validateShouldActivationBeAllowed()`. So re-activating an expired page with a new future `expire_by` works because validation sees the updated value.

---

### NCA Deployed (commit 1b91174) – updateStatus

**Order of operations:**

1. **Fetch** – `FindByIdAndMerchantIdAndModeWithAllAssociations` (no lock yet)
2. **Validate status change** – `validateStatusChange()` (rejects active→active, inactive→inactive)
3. **Validate activation** – `validateShouldActivationBeAllowed(&paymentPageEntity)` — uses **entity’s current expire_by** (DB value)
4. **Build request** – set req.Status, req.ExpireBy, etc.
5. **Update** – `updatePaymentPageEntitiesWithTransaction` (acquires lock, `LockRowById`, then updates)

**Critical difference:** There is **no** step that applies the new `expire_by` to the entity before validation. `validateShouldActivationBeAllowed` runs on the entity as loaded from DB, which still has the old (possibly expired) `expire_by`.

**Result:** Re-activating an expired page with a new future `expire_by` **fails** in deployed NCA because validation checks the old expired value.

---

### NCA Local (working copy) – updateStatus

**Order of operations:**

1. **Fetch** – `FindByIdAndMerchantIdAndModeWithAllAssociations`
2. **Validate status change** – `validateStatusChange()`
3. **Apply expire_by before validation** – `if expireBy != nil { paymentPageEntity.SetExpireBy(expireBy) }` (lines 1471–1478)
4. **Validate activation** – `validateShouldActivationBeAllowed(&paymentPageEntity)` — now sees the new expire_by
5. **Build request** – set req.Status, req.ExpireBy, etc.
6. **Update** – `updatePaymentPageEntitiesWithTransaction`

**Result:** Matches monolith behavior. Re-activating an expired page with a new future `expire_by` **succeeds**.

---

## 2. Deactivate Flow Comparison

### Monolith Deactivate (Core.php lines 926–962)

**Order of operations:**

1. **Lock** – `lockForUpdateAndReload($paymentLink)` (inside transaction)
2. **Validate** – `validateDeactivateOperation()` (rejects if already inactive)
3. **Change status** – `changeStatus($paymentLink, Status::INACTIVE, StatusReason::DEACTIVATED)`
4. **Save** – `saveOrFail($paymentLink)`

No `edit()`, no `expire_by` handling. Flow is simpler.

---

### NCA Deactivate (both deployed and local)

**Order of operations:**

1. **Call** – `updateStatus(ctx, id, &nocode.StatusInactive, &statusReason, nil, res)` — `expireBy` is `nil`
2. **Fetch** – `FindByIdAndMerchantIdAndModeWithAllAssociations`
3. **Validate status change** – `validateStatusChange()` (rejects inactive→inactive)
4. **Skip activation validation** – `status != &nocode.StatusActive`, so `validateShouldActivationBeAllowed` is not called
5. **Update** – `updatePaymentPageEntitiesWithTransaction`

**Result:** Deactivate flow is equivalent between monolith and NCA. No validation differences. No expire_by handling needed.

---

## 3. Status Transition Rules

| From   | To     | Allowed? | Notes                                                                 |
|--------|--------|----------|-----------------------------------------------------------------------|
| active | active | No       | `validateStatusChange` / `validateActivateOperation` reject           |
| active | inactive | Yes   | Deactivate or expire                                                  |
| inactive | inactive | No   | `validateStatusChange` / `validateDeactivateOperation` reject          |
| inactive | active | Yes   | Activate (with optional new expire_by)                                |
| expired | active | Yes   | Re-activate with new future expire_by (monolith + NCA local only)     |

**Expired → active:**  
- Monolith: Works via `edit($input)` applying new expire_by before validation.  
- NCA deployed: Fails because validation uses old expired expire_by.  
- NCA local: Works via `SetExpireBy(expireBy)` before validation.

---

## 4. Validation Differences

### validateStatusChange (NCA) vs validateActivateOperation / validateDeactivateOperation (Monolith)

| Check | Monolith | NCA |
|-------|----------|-----|
| active→active | `validateActivateOperation` | `validateStatusChange` |
| inactive→inactive | `validateDeactivateOperation` | `validateStatusChange` |
| Error messages | Same semantics | Same semantics |

### validateShouldActivationBeAllowed

| Check | Monolith | NCA |
|-------|----------|-----|
| Stock (times_payable exhausted) | V2: `isTimesPayableExhausted()` | `isTimesPayableExhausted()` |
| times_payable (V1) | `validateTimesPayableForActivation` | No V1 equivalent (NCA creates V2 only) |
| expire_by | `validateExpireBy` (entity value) | Same logic (entity value) |
| MIN_EXPIRY_SECS | 900 (15 min) | 900 (15 min) |

### NCA Controller ExpireBy Validation (utils.ValidateAndParseExpireBy)

- Before calling core: `expire_by` must be future timestamp (not in past).  
- Monolith: no explicit past check in controller; `validateExpireBy` requires `expire_by >= now + 15 min`.  
- NCA: `expire_by <= currentTime` → "expire_by must be a future timestamp".  
- Monolith: `expire_by < minExpireBy` → "expire_by should be at least 15 minutes after current time".  
- Both enforce future expiry; NCA additionally rejects past timestamps at controller level.

---

## 5. Locking Comparison

| Step | Monolith | NCA |
|------|----------|-----|
| Lock | `lockForUpdateAndReload` inside DB transaction | `AquireLock` (distributed) + `LockRowById` inside transaction |
| Lock timing | Before any validation | Lock acquired inside `updatePaymentPageEntitiesWithTransaction`, after validation | 
| Race window | Lock held during validation | Validation runs before lock; fetch is not locked |

**Note:** Lock ordering differs: monolith validates under lock; NCA validates before acquiring the lock. For activate/deactivate this is usually acceptable because status changes are idempotent.

---

## 6. Known Risks

### 1. Expire_by fix not deployed (critical)

- **Deployed NCA (1b91174):** Does not apply `expire_by` before validation.  
- **Impact:** Re-activating an expired page with a new future `expire_by` fails in NCA but succeeds in monolith.  
- **Mitigation:** Deploy the local fix (lines 1471–1478 in `updateStatus`) before moving merchants to `dual_write_read_no_external`.

### 2. V1 times_payable validation

- Monolith: V1 payment links use `validateTimesPayableForActivation` (times_payable > times_paid).  
- NCA: Only `isTimesPayableExhausted` (V2 stock-based). No `validateTimesPayableForActivation`.  
- **Impact:** If any V1 payment pages exist in NCA, activation behavior may differ. NCA creates V2 only, so this is likely low risk for new pages.

### 3. Lock ordering

- Monolith: Lock → validate → update.  
- NCA: Validate → lock → update.  
- **Impact:** Small race window between fetch and lock. For activate/deactivate, status checks make this low risk.

---

## 7. Recommendation

**Before moving merchants to `dual_write_read_no_external`:**

1. **Deploy the expire_by fix** – Ensure the local change that applies `SetExpireBy(expireBy)` before `validateShouldActivationBeAllowed` is in production.
2. **Verify** – Test re-activation of an expired page with a new `expire_by` in staging.
3. **Deactivate** – Safe to move; no known differences.

---

## 8. File References

| Component | File |
|-----------|------|
| NCA Activate/Deactivate core | `/no-code-apps/internal/modules/payment_page/core.go` |
| NCA validation | `/no-code-apps/internal/modules/payment_page/validation.go` |
| NCA controllers | `/no-code-apps/internal/controllers/payment_page.go` |
| Monolith activate/deactivate | `/api/app/Models/PaymentLink/Core.php` |
| Monolith validation | `/api/app/Models/PaymentLink/Validator.php` |
