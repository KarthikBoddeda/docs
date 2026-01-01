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

> **⚠️ IMPORTANT:** NCA code is written to **exactly mimic monolith behavior**. Monolith is the source of truth. Even if NCA behavior seems "correct", match monolith for now. Optimizations can be done later after NCA becomes reliable.

> **📝 NOTE: Some diffs may already be fixed.** Master branch and cherry-picked commits may contain fixes for some diffs. If you try to reproduce a diff and it doesn't occur on devstack, mark the subtask as `🔵 Already Fixed` and move on. The user will double-check these cases.

---

## Prerequisites

Before starting, ensure:

1. **Devstack is deployed** with prefix `pp-decomp-*`
2. **Commits are known** for: NCA service, API service, Gimli service
3. **Failure logs are accessible** at `/pythonscripts/decomp-scripts/failure_logs/pp_create_failures/`

> **⚠️ STOP:** If you don't have the **NCA commit**, **ABORT** and ask the user. API and Gimli have defaults (see Devstack Configuration section).

---

## How-To References

| Action | Reference |
|--------|-----------|
| Deploy to devstack | [/docs/agent-actions/deploy-to-devstack.md](/docs/agent-actions/deploy-to-devstack.md) |
| Hot reload (test code changes) | [/docs/agent-actions/hot-reload-devspace.md](/docs/agent-actions/hot-reload-devspace.md) |
| Sample API requests | [/docs/projects/payment-pages-decomp/payment-pages-api.http](/docs/projects/payment-pages-decomp/payment-pages-api.http) |
| Failure logs location | `/pythonscripts/decomp-scripts/failure_logs/pp_create_failures/` |
| Analysis report | `/pythonscripts/decomp-scripts/failure_logs/pp_create_failures/analysis.md` |
| Migration architecture | [/docs/projects/payment-pages-decomp/PAYMENT_PAGES_DECOMP.md](/docs/projects/payment-pages-decomp/PAYMENT_PAGES_DECOMP.md) |

### Code References

| Code Area | Reference |
|-----------|-----------|
| **NCA code flow** | [/docs/projects/payment-pages-decomp/code/nca-pp-create.md](/docs/projects/payment-pages-decomp/code/nca-pp-create.md) |
| **Monolith code flow** | [/docs/projects/payment-pages-decomp/code/api-pp-create.md](/docs/projects/payment-pages-decomp/code/api-pp-create.md) |
| **Monolith navigation guide** | [/docs/projects/payment-pages-decomp/code/monolith-navigation-guide.md](/docs/projects/payment-pages-decomp/code/monolith-navigation-guide.md) |
| **Proxying & dual write logic** | [/docs/projects/payment-pages-decomp/code/proxying.md](/docs/projects/payment-pages-decomp/code/proxying.md) |
| **Code reference index** | [/docs/projects/payment-pages-decomp/code/_index.md](/docs/projects/payment-pages-decomp/code/_index.md) |

---

## Subtasks (Ordered by Frequency)

All mismatches need to be fixed. Work through them in order of occurrence count.

> **🚨 CRITICAL: A subtask is NOT complete until ALL verification columns are ✅**  
> **DO NOT mark Status as 🟢 unless Deployed, Reproduced, HotReload, and Tested are ALL checked.**

### Status Legend

| Status | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🟡 | In progress (code written, NOT yet tested) |
| 🟢 | **VERIFIED FIXED** (deployed, reproduced, tested, working) |
| 🔵 | Already Fixed (doesn't reproduce on devstack - user will verify) |
| 🔴 | Blocked (needs user input) |

### Verification Columns

| Column | Meaning |
|--------|---------|
| **Deployed** | Devstack is running with required services |
| **Reproduced** | Diff was reproduced on devstack BEFORE fix |
| **HotReload** | Devspace hot-reload is set up and syncing |
| **Tested** | Fix was tested via hot-reload on devstack |
| **Commit** | Commit hash (only after testing passes) |

| # | Diff Type | Count | M | N | Deployed | Reproduced | HotReload | Tested | Status | Commit |
|---|-----------|-------|---|---|----------|------------|-----------|--------|--------|--------|
| 1 | `tracker type field is required` | 13,345 | 200 | 400 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 2 | `description contains invalid characters` | 8,090 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 3 | `title contains invalid characters` | 676 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 4 | `slug already exists` | 519 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 5 | `payment_success_message invalid chars` | 339 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 6 | `terms contains invalid characters` | 317 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 7 | `min_purchase null or valid integer` | 140 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 8 | `Contact number at least 8 digits` | 45 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 9 | `udf_schema more than 15 items` | 40 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 10 | `item missing in pp_item response` | 21 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 11 | `Contact number invalid characters` | 20 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 12 | `min_amount minimum 50 for USD` | 18 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 13 | `support_contact is invalid` | 17 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 14 | `Price has to be a fixed amount` | 17 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 15 | `Price has to be a fixed amount (v2)` | 13 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 16 | `domain must be a valid domain` | 11 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 17 | `length must be no more than 20` | 11 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 18 | `trouble completing your request` | 9 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 19 | `max amount exceeds maximum` | 8 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 20 | `support_contact invalid format` | 6 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 21 | `terms length 5 and 2000` | 6 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 22 | `Contact number > 15 digits` | 6 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 23 | `value length no more than 100` | 4 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 24 | `amount minimum 50 for USD` | 3 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 25 | `ends_by must be in future` | 3 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 26 | `length between 4 and 30` | 3 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 27 | `slug required for custom domain` | 2 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 28 | `must be a valid URL` | 2 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 29 | `available_units validation` | 2 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 30 | `max amount must be valid integer` | 2 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 31 | `READ ONLY transaction` | 1 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |
| 32 | `min purchase must be valid integer` | 1 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | |

---

## Workflow for Each Subtask

> **🚨 MANDATORY: Follow these steps IN ORDER. Do NOT skip steps. Do NOT mark complete without testing.**

---

### 🔲 STEP 1: DEPLOY DEVSTACK (Required First)

**You MUST have a running devstack before proceeding.**

```bash
# CHECK: Is devstack already running?
kubectl get pods -A -l name=pp-decomp-<label>
```

**If NO pods found → Deploy now:**
```bash
cd ~/rzp/kube-manifests/helmfile
# Update helmfile.yaml with commits from Devstack Configuration section
helmfile lint && helmfile sync
```

**Wait for pods to be ready:**
```bash
kubectl get pods -A -l name=pp-decomp-<label> -w
# Wait until ALL pods show STATUS=Running and READY=1/1
```

> **🛑 CHECKPOINT:** Run `kubectl get pods -A -l name=pp-decomp-<label>` and confirm pods are Running.  
> **If not running → DO NOT PROCEED. Fix deployment first.**  
> **✅ Once confirmed → Update subtask row: `Deployed` = ✅**

---

### 🔲 STEP 1.5: SET UP HOT RELOAD WITH AUTH BYPASS (Required for Direct Testing)

**⚠️ IMPORTANT:** When hitting NCA directly (not via Edge), Passport auth headers are not present. You MUST bypass Passport auth to test.

1. **Apply auth bypass in NCA code:**

   In `internal/router/payment_page_private_routes.go`, update `GetMiddlewares()`:
   
   ```go
   func (a *PaymentPageRoutes) GetMiddlewares() []gin.HandlerFunc {
       return []gin.HandlerFunc{
           middlewares.Serialize,
           middlewares.WithAppErrorHandler(),
           middlewares.WithRequestInterceptor(),
           middlewares.WithResponseInterceptor(),
           //middlewares.PassportPrivateAuth(),  // COMMENTED OUT for direct testing
           middlewares.WithAuth(),               // USE THIS INSTEAD
           middlewares.WithMerchantIdInterceptor(),
           middlewares.WithModeInterceptor(),
           middlewares.WithDualWriteStateInterceptor(),
           middlewares.WithPrometheus(),
           tracingIntegration.GinTracingMiddleware,
       }
   }
   ```

2. **Set up hot reload:**
   ```bash
   cd ~/rzp/no-code-apps
   go mod tidy && go mod vendor
   # Update devspace.yaml with your devstack_label
   devspace dev --no-warn
   ```

3. **Wait for sync to complete and pod to be ready**

> **🛑 CHECKPOINT:** Devspace is syncing and pod is running with auth bypass.  
> **✅ Once confirmed → Update subtask row: `HotReload` = ✅**

> **📝 NOTE:** You can reuse the same hot reload session for multiple subtasks. Just close the terminal when done - no need to run `devspace purge` between tasks.

---

### 🔲 STEP 2: REPRODUCE THE DIFF (Required Before Coding)

**You MUST reproduce the diff on devstack BEFORE writing any fix.**

1. **Get sample request from logs:**
   ```bash
   # Find the categorized folder for this diff type
   ls /Users/boddedakarthik.s/rzp/pythonscripts/decomp-scripts/failure_logs/pp_create_failures/categorized/
   
   # Read a recent log file
   head -5 "<categorized_folder>/<recent_date>.csv"
   ```

2. **Build the test request** using `payment-pages-api.http` as template

3. **Hit devstack and verify the diff exists:**
   ```bash
   curl -X POST "https://nca-<devstack-label>.dev.razorpay.in/v1/payment_pages" \
     -H "rzpctx-dev-serve-user: <devstack-label>" \
     -H "Authorization: Basic <auth_token>" \
     -H "Content-Type: application/json" \
     -d '<request_body_from_log>'
   ```

4. **Check response** - you should see the same error/diff as in logs

> **🛑 CHECKPOINT:** Did you reproduce the diff?  
> - **YES** → ✅ Update subtask row: `Reproduced` = ✅ → Proceed to Step 3  
> - **NO (diff doesn't occur)** → Mark status as `🔵 Already Fixed`, add note in Work Log, move to next subtask

---

### 🔲 STEP 3: WRITE THE FIX

**Only after reproducing the diff, analyze and write the fix.**

- Compare NCA code vs Monolith code (see Code References)
- **Goal:** Make NCA behave exactly like monolith
- Write the fix in NCA code

> **⚠️ IMPORTANT:** 
> - **ONLY change NCA code** - monolith is source of truth
> - **If monolith change is required** → **ABORT** and ask user
> - Even if NCA behavior seems "correct", match monolith for now

---

### 🔲 STEP 4: TEST THE FIX

**`devspace dev` must be running for hot reload to work. Code changes auto-sync while it's running.**
But the devspace pod must already be running right now, so this time devspace dev would be much faster.

1. **Ensure devspace dev is running:**
   ```bash
   # If not already running, start it:
   cd ~/rzp/no-code-apps
   devspace dev --no-warn
   ```

2. **Make your fix** - code changes will auto-sync to the pod

3. **If you added new dependencies:**
   ```bash
   go mod tidy && go mod vendor
   ```

5. **TEST: Hit the SAME request that reproduced the diff:**
   ```bash
   curl -X POST "https://nca-<devstack-label>.dev.razorpay.in/v1/payment_pages" \
     -H "Content-Type: application/json" \
     -H "X-Merchant-Id: <merchant_id>" \
     -H "X-Mode: test" \
     -d '<same_request_body>'
   ```

6. **Verify fix works:**
   - Diff is GONE
   - NCA response matches monolith behavior
   - No new errors

> **🛑 CHECKPOINT:** Did the fix work?  
> - **YES** → ✅ Update subtask row: `Tested` = ✅ → Proceed to Step 5  
> - **NO** → Debug, fix, repeat. DO NOT proceed until fix is verified.

---

### 🔲 STEP 5: COMMIT AND DOCUMENT (Only After Testing)

> **🚨🚨🚨 DO NOT COMMIT UNTIL FIX IS TESTED AND WORKING 🚨🚨🚨**
>
> **You MUST have completed Step 4 and verified the fix works on devstack.**
> **If `Tested` column is not ✅, DO NOT COMMIT.**

1. **Commit the fix:**
   ```bash
   cd ~/rzp/no-code-apps
   git add -A
   git commit -m "fix: <descriptive message>"
   ```

2. **Update subtask table:**
   - `Status` = 🟢
   - `Commit` = `<commit_hash>`

3. **Add Work Log entry** with:
   - Root cause
   - Fix description
   - Proof of work (before/after responses)
   - Commit hash

---

### 🔲 STEP 6: NEXT SUBTASK

Based on user input or current progress:
- Continue to next subtask (start from Step 2), OR
- Hand control back to user

---

## Work Log

> **When to add detailed entries:**
> 1. **Fix is VERIFIED and TESTED** → Add full details to Completed Fixes
> 2. **Fix FAILED after multiple iterations** → Add debugging details to Investigation Notes
> 3. **During investigation** → Keep notes minimal (just commit hash and pending steps)

### Completed Fixes

*(Add entries here ONLY after ALL verification columns are ✅)*

**Template for verified fix:**
```
#### Subtask #X: <diff_type>
**Date:** YYYY-MM-DD | **Commit:** `<hash>`
**Root Cause:** <why the diff occurred>
**Fix:** <what was changed>
**Files:** <list of files>
**Proof:** Before (NCA 400) → After (NCA 200 matches monolith)
```

### Already Fixed (User Verification Needed)

*(Diffs that don't reproduce on devstack - likely fixed in master/cherry-picks)*

**Template:**
```
#### Subtask #X: <diff_type>
**Date:** YYYY-MM-DD | **Devstack:** `pp-decomp-xxx`
**Result:** No diff observed - both return <status_code>
```

---

### Investigation Notes

> **When to add details here:**
> - Fix is verified and tested → add to Completed Fixes with full details
> - Fix didn't work after multiple iterations → add details here for debugging
> - Minimal notes only during investigation

*(Empty - start fresh)*

---

## Devstack Configuration

| Service | Commit | Label | Notes |
|---------|--------|-------|-------|
| NCA | `609f32edd7bd63b9db1ac09ba32fafd6b3e73236` | `pp-decomp-<label>` | **User input required** - always ask for latest |
| API | `d54e3b9afaf981785390805c70dde2b48761ae5c` | `pp-decomp-<label>` | Default (use unless specified) |
| Gimli | `4bf1861181c41e61b7994bbc5658012b430a4530` | `pp-decomp-<label>` | Default (use unless specified) |

> **⚠️ NCA commit is mandatory user input.** API and Gimli commits above are defaults - use them unless user specifies otherwise.

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
6. Devstack deployment fails
7. You cannot reproduce the diff on devstack
8. Hot reload setup fails

---

## ⛔ NEVER DO THIS

1. **NEVER mark Status as 🟢 without ALL verification columns checked (✅)**
2. **NEVER commit a fix without testing via hot reload on devstack**
3. **NEVER skip the reproduction step** - you must see the diff before fixing it
4. **NEVER assume a fix works** - always verify with actual requests
5. **NEVER proceed to next subtask without completing current one properly**

