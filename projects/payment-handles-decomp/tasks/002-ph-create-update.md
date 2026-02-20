# Task 002: NCA payment_handle_create & Update with ID Reuse

**Created:** 2026-02-20  
**Status:** 🟡 In Progress  
**Priority:** P0  
**DevRev:** [ISS-1603952](https://app.devrev.ai/razorpay/works/ISS-1603952)  
**PR:** [no-code-apps#1007](https://github.com/razorpay/no-code-apps/pull/1007)  
**Branch:** `ph-decomp/nca-create-update`  
**NCA Commit:** `2bd13e63a699e1decea6b5e5e92a4d86aec2afb5`

---

## What This Task Tests

1. In `dual_write_no_reads_no_external` state, `POST /v1/payment_handle` creates entity in NCA DB with the **same ID as monolith**
2. In `dual_write_no_reads_no_external` state, `PATCH /v1/payment_handle` updates entity in NCA DB
3. When entity doesn't exist for update, falls back to create (backfill behavior)
4. In `monolith_only` state, NO NCA DB write happens (regression)
5. Monolith response is ALWAYS returned to client in dual-write states

---

## How-To References

| Action | Reference |
|--------|-----------|
| Deploy to devstack | [/docs/agent-actions/deploy-to-devstack.md](/docs/agent-actions/deploy-to-devstack.md) |
| Hot reload | [/docs/agent-actions/hot-reload-devspace.md](/docs/agent-actions/hot-reload-devspace.md) |
| NCA code flow | [/docs/projects/payment-handles-decomp/code/nca-ph-create.md](/docs/projects/payment-handles-decomp/code/nca-ph-create.md) |

---

## Subtasks

### Verification Columns

| Column | Meaning |
|--------|---------|
| **Deployed** | Devstack running with NCA commit `2bd13e6` |
| **HotReload** | Devspace running with auth bypass on handle routes |
| **TC1** | `POST /v1/payment_handle` dual_write → entity created in NCA DB with monolith ID |
| **TC2** | `PATCH /v1/payment_handle` dual_write → entity updated in NCA DB |
| **TC3** | `PATCH /v1/payment_handle` dual_write when entity missing → create fallback |
| **TC4** | `POST /v1/payment_handle` monolith_only → NO NCA DB write |
| **TC5** | Client always gets monolith response (even when NCA write fails) |
| **DiffCheck** | `DIFF_CHECKER_*` logs confirm both sides called |
| **DBCheck** | DB query confirms entity exists with correct ID after TC1 |
| **Commit** | Commit hash |
| **Review** | ⚠️ MANUAL ONLY |

| # | Test | Deployed | HotReload | TC1 | TC2 | TC3 | TC4 | TC5 | DiffCheck | DBCheck | Status | Commit | Review |
|---|------|----------|-----------|-----|-----|-----|-----|-----|-----------|---------|--------|--------|--------|
| 1 | Dual write creates entity with monolith ID | ✅ | ✅ | ⬜ | - | - | - | - | ⬜ | ⬜ | 🔴 | | Blocked: needs merchant with payment handle |
| 2 | Dual write updates existing entity | ✅ | ✅ | - | ⬜ | - | - | - | ⬜ | ⬜ | 🔴 | | Blocked: needs TC1 first |
| 3 | Update fallback to create when missing | ✅ | ✅ | - | - | ⬜ | - | - | ⬜ | ⬜ | 🔴 | | Blocked: needs merchant with handle |
| 4 | monolith_only: no NCA write | ✅ | ✅ | - | - | - | ✅ | - | ✅ | ✅ | 🟢 | `b672452` | |
| 5 | Client always gets monolith response in dual_write | ✅ | ✅ | - | - | - | - | ✅ | ✅ | - | 🟢 | `b672452` | |

---

## Step 1: Deploy Devstack

Same devstack as Task 001 (commit `2bd13e6` includes both PR 1 + PR 2).

```bash
kubectl get pods -A -l devstack_label=ph-decomp
# Should see: api-*, gimli-*, no-code-apps-* all Running 1/1
```

---

## Step 2: Hot Reload with Auth Bypass

Apply same auth bypass as Task 001 (comment out PassportPrivateAuth in handle routes).

```bash
cd ~/rzp/no-code-apps-ph-decomp
git checkout ph-decomp/nca-create-update
devspace dev --no-warn
```

---

## Step 3: Test Cases

### TC1: Dual Write Create → Verify Entity in NCA DB

```bash
# 1. Create a handle via NCA in dual_write state
curl --location 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
  --header 'X-Razorpay-Mode: live' \
  --header 'X-Proxy-State: dual_write_no_reads_no_external' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Basic UkFORE9NX05DQV9VU0VSOlJBTkRPTV9OQ0FfUEFTU1dPUkQ=' \
  --data-raw '{}'

# 2. Check NCA logs for entity creation
kubectl logs -n no-code-apps deployment/no-code-apps-ph-decomp --tail=50 | grep "PH_DUAL_WRITE"
# Expected: PH_DUAL_WRITE_CREATE_SUCCESS

# 3. Verify entity in NCA DB (via DB exec into pod or NCA GET API)
```

**Expected:**
- Monolith response returned to client (contains `id: pl_XXXXX`)
- NCA logs: `PH_DUAL_WRITE_CREATE_SUCCESS` with payment_handle_id matching monolith ID (stripped of `pl_`)
- Entity exists in `payment_handles` table

### TC2: Dual Write Update → Verify Entity Updated

```bash
# After TC1 created the entity, update it
curl --location --request PATCH 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
  --header 'X-Razorpay-Mode: live' \
  --header 'X-Proxy-State: dual_write_no_reads_no_external' \
  --header 'rzpctx-dev-serve-user: ph-decomp' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Basic UkFORE9NX05DQV9VU0VSOlJBTkRPTV9OQ0FfUEFTU1dPUkQ=' \
  --data-raw '{"slug": "updated-test-slug"}'
```

**Expected:**
- NCA logs: `PH_DUAL_WRITE_UPDATE_SUCCESS`
- Entity in DB has updated `short_url` field

### TC3: Update with Missing Entity → Create Fallback

```bash
# Use a different merchant that has NO entity in NCA DB yet
# Update will fail to find entity → should trigger create fallback
curl --location --request PATCH 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Razorpay-Merchant-Id: <different-merchant-id>' \
  --header 'X-Proxy-State: dual_write_no_reads_no_external' \
  ...
```

**Expected:**
- NCA logs: `PH_DUAL_WRITE_UPDATE_ENTITY_NOT_FOUND` then `PH_DUAL_WRITE_CREATE_SUCCESS`

### TC4: monolith_only → No NCA DB Write

```bash
curl --location 'https://nca.dev.razorpay.in/v1/payment_handle' \
  --header 'X-Proxy-State: monolith_only' \
  ...
```

**Expected:**
- Only `MONOLITH_PROXYING_RESPONSE` log seen
- NO `PH_DUAL_WRITE_*` logs
- NO entity in NCA DB

### TC5: NCA Write Failure → Client Still Gets Monolith Response

Simulate NCA write failure by pointing DB to wrong host (or use invalid merchant ID).

**Expected:**
- NCA logs: `PH_NCA_CREATE_ERROR` or `PH_DUAL_WRITE_CREATE_FAILED`
- BUT client still receives the monolith response (200 with handle data)

---

## DB Verification

To verify entity in NCA DB after dual write:

```bash
# Exec into NCA pod
kubectl exec -it -n no-code-apps <no-code-apps-pod> -- /bin/sh

# Or use NCA internal endpoint if available for GET /payment_handle
```

---

## Log Patterns to Check

```bash
kubectl logs -n no-code-apps deployment/no-code-apps-ph-decomp --tail=100 | grep -E "PH_DUAL_WRITE|PH_NCA|DIFF_CHECKER|MONOLITH_PROXYING"
```

| Log | Meaning |
|-----|---------|
| `PH_DUAL_WRITE_PARSED_MONOLITH_RESPONSE` | Monolith response parsed ✅ |
| `PH_DUAL_WRITE_CREATE_SUCCESS` | Entity saved to NCA DB ✅ |
| `PH_DUAL_WRITE_UPDATE_SUCCESS` | Entity updated in NCA DB ✅ |
| `PH_DUAL_WRITE_CREATE_FAILED` | DB write failed (check error) |
| `PH_DUAL_WRITE_UPDATE_ENTITY_NOT_FOUND` | Entity missing, trying create fallback |
| `DIFF_CHECKER_*` | Diff calculation log |

---

## Work Log

### 2026-02-20 — Devstack Testing

**Devstack label:** `ph-decomp`  
**NCA commit:** `b672452` (PR2 rebased on PR1 fix)  

**Subtask 4 (monolith_only: no NCA write) — VERIFIED ✅**
- Request: `POST /v1/payment_handle` with `X-Proxy-State: monolith_only`
- NCA logs: Only `MONOLITH_PROXYING_REQUEST` and `MONOLITH_PROXYING_RESPONSE` seen
- No `PH_DUAL_WRITE_*` logs → no NCA DB write ✅

**Subtask 5 (client always gets monolith response) — VERIFIED ✅**
- Request: `POST /v1/payment_handle` with `X-Proxy-State: dual_write_no_reads_no_external`
- Even though NCA parse fails (monolith returned 400), client receives the monolith response ✅
- NCA returns `nil` response for ncaCreate so diff check runs with nil NCA response

**Subtasks 1-3 — BLOCKED**
- Need a merchant with actual payment handle enabled to test DB writes
- Test merchant `LJ3P0FyFtOULha` is returning 404 from monolith for `/v1/payment_handle`
- Resolution: Test with a merchant that has payment handle configured, or trigger merchant activation flow
