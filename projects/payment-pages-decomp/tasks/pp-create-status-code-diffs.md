# Task: Fix payment_page_create Status Code Diffs

**Status:** 🟡 In Progress  
**Priority:** P0  
**API:** `payment_page_create` (`POST /payment_pages`)

---

## Problem Statement

The `payment_page_create` API is currently in **dual-write state**. During dual-write, both monolith and NCA execute the same request, and their responses are compared. This task addresses **status code diffs** - cases where monolith and NCA return different HTTP status codes.

### What is a Status Code Diff?

When NCA proxies a request to monolith:
- Monolith executes and returns a response (e.g., 200 OK)
- NCA executes the same logic and returns a response (e.g., 400 Bad Request)
- If status codes differ → **Status Code Diff** is logged

### Why This Matters

**Any mismatch is a bug that needs fixing.** The goal is for NCA to behave exactly like monolith.

- **Monolith 200, NCA 400/500**: NCA is rejecting requests that monolith accepts → fix NCA validation
- **Monolith 400/500, NCA 200**: NCA is accepting requests that monolith rejects → fix NCA validation

---

## Prerequisites

Before starting, ensure:

1. **Devstack is deployed** with prefix `pp-decomp-*`
2. **Commits are known** for: NCA service, API service, Gimli service
3. **Failure logs are accessible** at `/pythonscripts/decomp-scripts/failure_logs/pp_create_failures/`

> **⚠️ STOP:** If you don't have the commits for all services, **ABORT** and ask the user for inputs.

---

## How-To References

| Action | Reference |
|--------|-----------|
| Deploy to devstack | [/docs/agent-actions/deploy-to-devstack.md](/docs/agent-actions/deploy-to-devstack.md) |
| Sample API requests | [/docs/projects/payment-pages-decomp/payment-pages-api.http](/docs/projects/payment-pages-decomp/payment-pages-api.http) |
| Failure logs location | `/pythonscripts/decomp-scripts/failure_logs/pp_create_failures/` |
| Analysis report | `/pythonscripts/decomp-scripts/failure_logs/pp_create_failures/analysis.md` |
| Migration architecture | [/docs/projects/payment-pages-decomp/PAYMENT_PAGES_DECOMP.md](/docs/projects/payment-pages-decomp/PAYMENT_PAGES_DECOMP.md) |

---

## Subtasks (Ordered by Frequency)

All mismatches need to be fixed. Work through them in order of occurrence count.

| # | Diff Type | Count | Monolith | NCA | Status | Summary |
|---|-----------|-------|----------|-----|--------|---------|
| 1 | `validation failure: The tracker type field is required` | 13,345 | 200 | 400 | ⬜ | |
| 2 | `description contains invalid characters` | 8,090 | 400 | 200 | ⬜ | |
| 3 | `title contains invalid characters` | 676 | 400 | 200 | ⬜ | |
| 4 | `validation failure: slug already exists` | 519 | 200 | 400 | ⬜ | |
| 5 | `settings.payment_success_message contains invalid characters` | 339 | 400 | 200 | ⬜ | |
| 6 | `terms contains invalid characters` | 317 | 400 | 200 | ⬜ | |
| 7 | `min_purchase should be null or valid integer` | 140 | 400 | 200 | ⬜ | |
| 8 | `Contact number should be at least 8 digits` | 45 | 400 | 200 | ⬜ | |
| 9 | `The udf_schema may not have more than 15 items` | 40 | 400 | 200 | ⬜ | |
| 10 | `dual write id extraction: item missing in payment page item response` | 21 | 200 | 400 | ⬜ | |
| 11 | `Contact number contains invalid characters` | 20 | 400 | 200 | ⬜ | |
| 12 | `validation failure: min_amount should be minimum 50 for USD` | 18 | 200 | 400 | ⬜ | |
| 13 | `validation failure: support_contact is invalid` | 17 | 200 | 400 | ⬜ | |
| 14 | `Price has to be a fixed amount` | 17 | 400 | 200 | ⬜ | |
| 15 | `validation failure: Price has to be a fixed amount` | 13 | 200 | 400 | ⬜ | |
| 16 | `validation failure: domain must be a valid domain` | 11 | 200 | 400 | ⬜ | |
| 17 | `validation failure: the length must be no more than 20` | 11 | 200 | 400 | ⬜ | |
| 18 | `We are facing some trouble completing your request` | 9 | 400 | 200 | ⬜ | |
| 19 | `max amount exceeds maximum payment amount allowed` | 8 | 400 | 200 | ⬜ | |
| 20 | `validation failure: support_contact invalid contact format` | 6 | 200 | 400 | ⬜ | |
| 21 | `validation failure: terms length must be between 5 and 2000` | 6 | 200 | 400 | ⬜ | |
| 22 | `Contact number should not be greater than 15 digits` | 6 | 400 | 200 | ⬜ | |
| 23 | `validation failure: value length must be no more than 100` | 4 | 200 | 400 | ⬜ | |
| 24 | `validation failure: amount should be minimum 50 for USD` | 3 | 200 | 400 | ⬜ | |
| 25 | `internal error: validation failure ends_by must be in future` | 3 | 200 | 400 | ⬜ | |
| 26 | `validation failure: the length must be between 4 and 30` | 3 | 200 | 400 | ⬜ | |
| 27 | `slug required for page with custom domain` | 2 | 400 | 200 | ⬜ | |
| 28 | `validation failure: must be a valid URL` | 2 | 200 | 400 | ⬜ | |
| 29 | `internal error: validation failure available_units` | 2 | 200 | 400 | ⬜ | |
| 30 | `The max amount must be valid integer` | 2 | 400 | 200 | ⬜ | |
| 31 | `db error: Cannot execute statement in a READ ONLY transaction` | 1 | 200 | 400 | ⬜ | |
| 32 | `The min purchase must be valid integer` | 1 | 400 | 200 | ⬜ | |

---

## Workflow for Each Subtask

### Step 1: Deploy Infrastructure (if not already deployed)

```bash
# Check if devstack with pp-decomp prefix exists
kubectl get pods -A -l name=pp-decomp-<label>

# If not, deploy following /docs/agent-actions/deploy-to-devstack.md
cd ~/rzp/kube-manifests/helmfile
# Update helmfile.yaml with:
#   - devstack_label: pp-decomp-<your-label>
#   - commits for: nca, api, gimli
helmfile lint && helmfile sync
```

> **⚠️ STOP:** If you don't know the commits to use, **ABORT** and ask the user.

### Step 2: Reproduce the Diff

1. Find sample logs in the categorized folder:
   ```
   /pythonscripts/decomp-scripts/failure_logs/pp_create_failures/categorized/<diff_folder>/<date>.csv
   ```

2. Use the sample request from `payment-pages-api.http` as template

3. Build the request body from the log data to replicate the exact failing request

4. Hit the NCA endpoint on devstack:
   ```bash
   curl -X POST "https://nca-<devstack-label>.dev.razorpay.in/v1/payment_pages" \
     -H "rzpctx-dev-serve-user: <devstack-label>" \
     -H "Authorization: Basic <auth_token>" \
     -H "Content-Type: application/json" \
     -d '<request_body_from_log>'
   ```

5. Check NCA diff logs to see the mismatch

### Step 3: Identify the Fix

- Analyze why NCA behaves differently from monolith
- **Goal:** Make NCA match monolith behavior (monolith is source of truth)

> **⚠️ IMPORTANT:** 
> - **Prefer NCA changes** - we want NCA to match monolith
> - **If monolith change is required** → **ABORT** and notify user
> - Even if NCA behavior seems "correct", match monolith for now (optimize later)

### Step 4: Test the Fix

1. Apply code changes (TODO: setup hot reloading - see agent-actions)
2. Rebuild/redeploy if needed
3. Hit the same request again
4. Verify:
   - Diff is gone
   - Behavior matches monolith
   - No new regressions

### Step 5: Document and Commit

1. If fix is successful:
   - Commit changes with descriptive message
   - Update subtask status to 🟢
   - Add summary and commit hash to Work Log
   - Add proof of work (before/after response comparison)

2. If fix not found:
   - Keep status as ⬜
   - Document findings in Work Log
   - Move to next subtask

### Step 6: Next Steps

Based on user input or current progress:
- Continue to next subtask, OR
- Hand control back to user

---

## Work Log

### Template for Each Fix

```markdown
#### Subtask #X: <diff_type>

**Date:** YYYY-MM-DD  
**Status:** 🟢 Fixed / 🔴 Blocked / ⬜ Investigated  

**Root Cause:**
<description of why the diff occurs>

**Fix:**
<description of the fix>

**Commit:** `<commit_hash>`

**Files Changed:**
- `path/to/file1.go`
- `path/to/file2.go`

**Proof of Work:**

Before:
```json
// NCA response (400)
{"error": {"code": "BAD_REQUEST", "description": "..."}}
```

After:
```json
// NCA response (200) - matches monolith
{"id": "pp_xxx", ...}
```

**Notes:**
<any additional notes>
```

---

### Completed Fixes

*(Add entries here as subtasks are completed)*

---

### Investigation Notes

*(Add notes for subtasks investigated but not fixed)*

---

## Devstack Configuration

| Service | Commit | Label |
|---------|--------|-------|
| NCA | `<pending>` | `pp-decomp-<label>` |
| API | `<pending>` | `pp-decomp-<label>` |
| Gimli | `<pending>` | `pp-decomp-<label>` |

> Update this section when devstack is deployed.

---

## Statistics

| Metric | Value |
|--------|-------|
| Total Diffs | 23,953 |
| Monolith 200, NCA 400/500 | 13,987 (58.4%) |
| Monolith 400/500, NCA 200 | 9,712 (40.5%) |
| Timeouts | 250 (1.0%) |
| Subtasks Total | 32 |
| Subtasks Completed | 0 |
| Subtasks Remaining | 32 |

---

## Abort Conditions

**STOP and ask the user if:**

1. You don't know the commits for devstack deployment
2. A fix requires changes to the monolith (API) code
3. You're stuck and can't identify the root cause after investigation
4. You're unsure whether a behavior difference is acceptable
5. Test results are ambiguous or unexpected

