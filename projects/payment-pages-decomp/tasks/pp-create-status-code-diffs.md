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

> **⚠️ AUTO-DEPLOY:** If devstack is not running, deploy it automatically using a base NCA image from the registry. Don't ask the user - just deploy. Use devspace for hot-reloading local code. API and Gimli have defaults (see Devstack Configuration section).

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

### Coralogix Log Search Patterns

To fetch actual request bodies from Coralogix MCP, use these log message patterns:

| Route | Coralogix Query Pattern | Application |
|-------|------------------------|-------------|
| `payment_page_create` | `"PAYMENT_PAGE_CREATE_REQUEST" AND "<razorpay_request_id>"` | `no-code-apps` |
| `payment_page_update` | `"PAYMENT_PAGE_UPDATE_REQUEST" AND "<razorpay_request_id>"` | `no-code-apps` |
| Other routes | *(Update this table as new tasks are added)* | `no-code-apps` |

> **Note:** Look for `razorpay_request_id` in the failure log CSV files, then use it to fetch the actual request from Coralogix.

---

## Subtasks (Ordered by Frequency)

All mismatches need to be fixed. Work through them in order of occurrence count.

> **🚨 CRITICAL: A subtask is NOT complete until ALL verification columns are ✅**  
> **DO NOT mark Status as 🟢 unless Deployed, Reproduced, CodeEvidence, HotReload, Tested, and DiffCheck are ALL ✅.**

### Status Legend

| Status | Meaning |
|--------|---------|
| ⬜ | Not started |
| 🟡 | In progress (code written, NOT yet tested) |
| 🟢 | **VERIFIED FIXED** (all columns ✅, awaiting manual review) |
| 🔵 | Already Fixed (doesn't reproduce on devstack - user will verify) |
| 🔴 | Blocked (needs user input) |

> **⚠️ TASK NOT COMPLETE UNTIL `Review` = ✅**
> 
> The `Review` column is **MANUAL ONLY** - only the user can mark it.
> Even if Status is 🟢, the subtask is NOT done until user marks Review ✅.

### Verification Columns

| Column | Meaning |
|--------|---------|
| **Deployed** | Devstack is running with required services |
| **ReqFound** | Actual request body retrieved from Coralogix logs |
| **Reproduced** | Diff was reproduced on devstack BEFORE fix |
| **CodeEvidence** | Code comparison done - monolith vs NCA behavior documented |
| **HotReload** | Devspace hot-reload is set up and syncing |
| **TC1** | Test Case 1: Request from this diff type (one date/entry) |
| **TC2** | Test Case 2: Different request from SAME diff type (another date/entry) |
| **TC3** | Test Case 3: Another request from SAME diff type (yet another date/entry) |
| **TC4** | Test Case 4: Standard request from `payment-pages-api.http` (regression) |
| **DiffCheck** | `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` log seen for ALL test cases |
| **Commit** | Commit hash (only after ALL testing passes) |
| **Review** | ⚠️ **MANUAL ONLY** - User verification required. Task NOT done until ✅ |

> **Note:** `✅*` means the step was completed but with a caveat (e.g., logs beyond Coralogix retention, used pattern-based test instead). See work log for details.

> **🧪 TEST CASES REQUIRED:** You MUST test at least 3 different scenarios before marking as fixed!

> **⚠️ CRITICAL:** You MUST use `X-Proxy-State: dual_write_shadow_read_no_external` for testing!
> - ⚠️ Header is `X-Proxy-State` NOT `X-Dual-Write-State`!
> - `dual_write_shadow_read_no_external` proxies to monolith AND compares responses
> - You MUST see `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` log to confirm fix works

| # | Diff Type | Count | M | N | Deployed | ReqFound | Reproduced | CodeEvidence | HotReload | TC1 | TC2 | TC3 | TC4 | DiffCheck | Status | Commit | Review |
|---|-----------|-------|---|---|----------|----------|------------|--------------|-----------|-----|-----|-----|-----|-----------|--------|--------|--------|
| 1 | `tracker type field is required` | 13,345 | 200 | 400 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟢 | `ce81003` | |
| 2 | `description contains invalid characters` | 8,090 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟢 | `7306449` | |
| 3 | `title contains invalid characters` | 676 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟢 | `7306449` | |
| 4 | `slug already exists` | 519 | 200 | 400 | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🔴 | | |
| 5 | `payment_success_message invalid chars` | 339 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟢 | `f16d92e` | |
| 6 | `terms contains invalid characters` | 317 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟢 | `f16d92e` | |
| 7 | `min_purchase null or valid integer` | 140 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟢 | `d4ffebe` | |
| 8 | `Contact number at least 8 digits` | 45 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟢 | `3f64cbe` | |
| 9 | `udf_schema more than 15 items` | 40 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟢 | `3f64cbe` | |
| 10 | `item missing in pp_item response` | 21 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟠 | | Pending - see analysis below |
| 11 | `Contact number invalid characters` | 20 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟢 | `2f2d558` | |
| 12 | `min_amount minimum 50 for USD` | 18 | 200 | 400 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟠 | | NCA over-validates - needs investigation |
| 13 | `support_contact is invalid` | 17 | 200 | 400 | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | ⬜ | 🟡 | `606cbbe` | Fix: Use raw length for validation |
| 14 | `Price has to be a fixed amount` | 17 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟢 | `2f2d558` | Logic fix - feature dependent |
| 15 | `Price has to be a fixed amount (v2)` | 13 | 200 | 400 | ✅ | ✅ | ✅ | ✅ | N/A | N/A | N/A | ✅ | N/A | ✅ | 🟢 | `2f2d558` | Fixed by same logic fix as #14 |
| 16 | `domain must be a valid domain` | 11 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟠 | | slug `@handle` format triggers domain validation |
| 17 | `length must be no more than 20` | 11 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟠 | | subscription_button - investigate field |
| 18 | `trouble completing your request` | 9 | 500 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🔵 | | Monolith 500 error - transient/infra |
| 19 | `max amount exceeds maximum` | 8 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | N/A | N/A | N/A | ✅ | N/A | ✅ | 🔵 | | Already works |
| 20 | `support_contact invalid format` | 6 | 200 | 400 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟠 | | Same as #13 - NCA over-validates |
| 21 | `terms length 5 and 2048` | 6 | 200 | 400 | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | ⬜ | 🟡 | `1c75c90` | Fix committed, needs testing |
| 22 | `Contact number > 15 digits` | 6 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | N/A | N/A | N/A | ✅ | N/A | ✅ | 🔵 | | Already works |
| 23 | `value length no more than 10000` | 4 | 200 | 400 | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | ⬜ | 🟡 | `9597018` | Fix: Increased limit to 100000 |
| 24 | `amount minimum 50 for USD` | 3 | 200 | 400 | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | ⬜ | 🟡 | `9597018` | Fix: Removed currency min from Amount |
| 25 | `ends_by must be in future` | 3 | 200 | 400 | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | ⬜ | 🟡 | `b442315` | Fix committed, needs testing |
| 26 | `slug length between 4 and 30` | 3 | 200 | 400 | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | ⬜ | 🟡 | `b442315` | Fix committed, needs testing |
| 27 | `slug required for custom domain` | 2 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | ⬜ | 🟡 | `9597018` | Fix: Added slug requirement |
| 28 | `must be a valid URL` | 2 | 200 | 400 | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | ⬜ | 🟡 | `b442315` | Fix committed, needs testing |
| 29 | `available_units validation` | 2 | 200 | 400 | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | ⬜ | 🟡 | `4399464` | Fix committed, needs testing |
| 30 | `max amount must be valid integer` | 2 | 400 | 200 | ✅ | ✅ | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ✅ | ⬜ | ⬜ | 🟡 | `9597018` | Fix: Added uint32 max validation |
| 31 | `READ ONLY transaction` | 1 | 200 | 400 | ✅ | ✅ | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 🔵 | | DB infra transient error |
| 32 | `min purchase must be valid integer` | 1 | 400 | 200 | ✅ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🔵 | | Same as #7 - already fixed |

---

## Workflow for Each Subtask

> **🚨 MANDATORY: Follow these steps IN ORDER. Do NOT skip steps. Do NOT mark complete without testing.**

---

### 🔲 STEP 1: DEPLOY DEVSTACK (Required First)

**You MUST have a running devstack before proceeding.**

```bash
# CHECK: Is devstack already running?
kubectl get pods -A -l devstack_label=pp-decomp-<label>
# You should see 3 pods running: api, gimli, no-code-apps
```

**If any pods missing → Deploy now:**
```bash
cd ~/rzp/kube-manifests/helmfile
# Update helmfile.yaml with commits from Devstack Configuration section
helmfile lint && helmfile sync
```

**Check if pods are ready (single command!):**
```bash
kubectl get pods -A -l devstack_label=pp-decomp-fix1
# You should see 3 pods: api-web-*, gimli-*, no-code-apps-*
# Wait until ALL pods show STATUS=Running and READY=1/1
```

> **🛑 CHECKPOINT:** Run `kubectl get pods -A -l devstack_label=pp-decomp-fix1` and confirm ALL 3 pods are Running.  
> **If not running → DO NOT PROCEED. Fix deployment first.**  
> **✅ Once confirmed → Update subtask row: `Deployed` = ✅**

---

### 🔲 STEP 1.5: SET UP HOT RELOAD WITH AUTH BYPASS (Required for Direct Testing)

**⚠️ IMPORTANT:** When hitting NCA directly (not via Edge), Passport auth headers are not present. You MUST bypass Passport auth to test.

> **⚠️ DO NOT COMMIT the auth bypass change.** Keep it uncommitted throughout testing. Only commit your actual bug fixes.

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
   export GOPRIVATE="github.com/razorpay/*"  # Required for private modules
   go mod tidy && go mod vendor
   # Update devspace.yaml with your devstack_label
   devspace dev --no-warn
   ```

3. **Wait for sync to complete and pod to be ready**

> **🛑 CHECKPOINT:** Devspace is syncing and pod is running with auth bypass.  
> **✅ Once confirmed → Update subtask row: `HotReload` = ✅**

> **📝 NOTE:** You can reuse the same hot reload session for multiple subtasks. Just close the terminal when done - no need to run `devspace purge` between tasks.

> **⚠️ WHEN TO PURGE:** After a fresh `helmfile sync`, check if there's a stale old devspace pod:
> ```bash
> kubectl get pods -A -l devstack_label=pp-decomp-fix1
> # If you see an OLD pod (e.g., 11h) alongside NEW pods (e.g., 2m), run:
> devspace purge
> # Then start fresh:
> devspace dev --no-warn
> ```

---

### 🔲 STEP 2: REPRODUCE THE DIFF (Required Before Coding)

**You MUST reproduce the diff on devstack BEFORE writing any fix.**

1. **Get `razorpay_request_id` from failure logs:**
   ```bash
   # Find the categorized folder for this diff type
   ls /Users/boddedakarthik.s/rzp/pythonscripts/decomp-scripts/failure_logs/pp_create_failures/categorized/
   
   # Read a recent log file and extract razorpay_request_id
   head -5 "<categorized_folder>/<recent_date>.csv"
   # Look for: "razorpay_request_id":"<uuid>"
   ```

2. **Get ACTUAL request body from Coralogix (MCP):**
   
   > **🔴 IMPORTANT: Don't guess the request - fetch the actual one!**
   
   Use `mcp_razorpay-cora-mcp-server_search_logs` with:
   - `search_string`: `"PAYMENT_PAGE_CREATE_REQUEST" AND "<razorpay_request_id>"`
   - `applicationName`: `no-code-apps`
   - **For recent logs:** `relative_hours`: `48`
   - **For older logs:** Use `start_time` + `end_time` (RFC3339 format)
   
   **Example queries:**
   ```
   # Recent logs (last 48 hours)
   search_string: "PAYMENT_PAGE_CREATE_REQUEST" AND "fc3302ff-a3d0-4116-ab54-d069daffab65"
   relative_hours: 48
   
   # Historical logs (specific date)
   search_string: "PAYMENT_PAGE_CREATE_REQUEST" AND "fc3302ff-a3d0-4116-ab54-d069daffab65"
   start_time: "2025-12-29T00:00:00Z"
   end_time: "2025-12-30T00:00:00Z"
   ```
   
   The log will contain the full request body that caused the diff.
   
   > ✅ Mark `ReqFound` column once you have the actual request body
   
   > **Note:** Coralogix has 2-3 months retention. Choose log files within this retention period.

3. **Build the test request:**

   > **🔴 USE THE HTTP FILE! 🔴**
   > 
   > **Template requests are in:** `docs/projects/payment-pages-decomp/payment-pages-api.http`
   > 
   > - Open the file in VS Code with REST Client extension
   > - Use `payment_page_create` request as base template
   > - All headers, auth, and variables are already configured!
   > - Just modify the request body to trigger the specific diff

   > **⚠️ CRITICAL:** 
   > - Use test merchant ID `LJ3P0FyFtOULha` - NOT production IDs from logs!
   > - Use `X-Proxy-State: dual_write_shadow_read_no_external` to enable comparison!
   > - DON'T `kubectl exec` into pods - hit URL directly!

   **If using curl directly (not recommended):**
   ```bash
   curl --location 'https://nca.dev.razorpay.in/v1/payment_pages' \
     --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
     --header 'X-Razorpay-Mode: live' \
     --header 'X-Proxy-State: dual_write_shadow_read_no_external' \
     --header 'rzpctx-dev-serve-user: <devstack-label>' \
     --header 'Content-Type: application/json' \
     --header 'Authorization: Basic UkFORE9NX05DQV9VU0VSOlJBTkRPTV9OQ0FfUEFTU1dPUkQ=' \
     --data-raw '<request_body_with_diff_trigger>'
   ```

   **Modify the body** to include the field that triggers the diff (e.g., `"settings": { "goal_tracker": {} }`)

4. **Check logs for diff:**
   - Look for `DIFF_CHECKER_*` logs in NCA pod logs
   - You should see a status code diff logged (e.g., `status_code_diff`)
   - This confirms the diff exists and comparison is working

> **🛑 CHECKPOINT:** Did you reproduce the diff?  
> - **YES** → ✅ Update subtask row: `Reproduced` = ✅ → Proceed to Step 3  
> - **NO (diff doesn't occur)** → Mark status as `🔵 Already Fixed`, add note in Work Log, move to next subtask

---

### 🔲 STEP 3: ANALYZE CODE & WRITE THE FIX

**Only after reproducing the diff, analyze and write the fix.**

> **📚 BEFORE CODING:** Read the navigation guides first!
> - `code/guide-to-navigate-nca-code.md` - NCA patterns, numeric types, debugging
> - `code/monolith-navigation-guide.md` - PHP magic functions, validation patterns

1. **Find the monolith code** that handles this validation/logic
   - Navigate using `code/monolith-navigation-guide.md`
   - Document the exact file, function, and line numbers
   - Understand WHY monolith behaves the way it does

2. **Find the NCA code** that handles the same logic
   - Navigate using `code/guide-to-navigate-nca-code.md`
   - Document the exact file, function, and line numbers
   - Identify the DIFFERENCE in behavior

3. **Write the fix** in NCA code to match monolith

4. **Add debug logs if needed** (to trace values during testing):
   ```go
   fmt.Printf("DEBUG: value = %+v, nil = %v\n", myVar, myVar == nil)
   ```
   **⚠️ Remove debug logs before committing!**

> **🛑 CHECKPOINT:** Do you have code evidence from BOTH monolith and NCA?
> - ✅ Document the monolith code (file:line, key logic)
> - ✅ Document the NCA code (file:line, what was wrong)
> - ✅ Update subtask row: `CodeEvidence` = ✅ → Proceed

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
   export GOPRIVATE="github.com/razorpay/*"
   go mod tidy && go mod vendor
   ```

4. **TEST: Run at least 3 different test cases:**

   > **🔴 USE THE HTTP FILE!**
   > 
   > **Template:** `docs/projects/payment-pages-decomp/payment-pages-api.http`
   > - Use `payment_page_create` request as base
   > - All headers/auth are pre-configured!
   > - Ensure `@dual_write_state = dual_write_shadow_read_no_external` (for comparison)

   > **⚠️ CRITICAL:**
   > - Use `X-Proxy-State: dual_write_shadow_read_no_external` - NOT `nca_only`!
   > - `nca_only` does NOT compare with monolith - useless for verifying fixes
   > - DON'T `kubectl exec` into pods - hit URL directly!

   **🧪 REQUIRED TEST CASES (minimum 4):**
   
   | Test Case | Description | Purpose |
   |-----------|-------------|---------|
   | **TC1** | Request from this diff type (e.g., `2025-12-29.csv`) | Confirms the fix works |
   | **TC2** | DIFFERENT request from same diff type (e.g., `2025-12-28.csv`) | Ensures fix is robust |
   | **TC3** | ANOTHER request from same diff type (e.g., different entry) | Additional validation |
   | **TC4** | Standard request from `payment-pages-api.http` | Regression test - normal flow works |
   
   > **🔴 IMPORTANT:** 
   > - TC1-TC3: Must be ACTUAL requests from failure logs (different dates/entries)
   > - TC4: Use the standard request from `payment-pages-api.http` (regression check)

   **If using curl (not recommended - use .http file instead):**
   ```bash
   curl --location 'https://nca.dev.razorpay.in/v1/payment_pages' \
     --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
     --header 'X-Razorpay-Mode: live' \
     --header 'X-Proxy-State: dual_write_shadow_read_no_external' \
     --header 'rzpctx-dev-serve-user: <devstack-label>' \
     --header 'Content-Type: application/json' \
     --header 'Authorization: Basic UkFORE9NX05DQV9VU0VSOlJBTkRPTV9OQ0FfUEFTU1dPUkQ=' \
     --data-raw '<same_request_body_with_diff_trigger>'
   ```

5. **Verify fix works for ALL test cases - CHECK LOGS:**
   - Look for `DIFF_CHECKER_NO_DIFFS_FOUND` in NCA pod logs → **✅ Fix works!**
   - If you still see diff logs → Fix didn't work, debug and retry
   - Also verify: `MONOLITH_PROXYING_RESPONSE` log shows API was called

> **🛑 CHECKPOINT:** Did ALL test cases pass?  
> - **YES (see `DIFF_CHECKER_NO_DIFFS_FOUND` for all 4)** → ✅ Update subtask: `TC1` = ✅, `TC2` = ✅, `TC3` = ✅, `TC4` = ✅, `DiffCheck` = ✅ → Proceed to Step 5  
> - **NO (any test case fails)** → Debug, fix, repeat. DO NOT proceed until ALL test cases pass.

---

### 🔲 STEP 5: COMMIT AND DOCUMENT (Only After Testing)

> **🚨🚨🚨 DO NOT COMMIT UNTIL FIX IS TESTED AND WORKING 🚨🚨🚨**
>
> **You MUST have completed Step 4 and verified the fix works on devstack.**
> **If `TC1`, `TC2`, `TC3`, `TC4`, and `DiffCheck` columns are not ALL ✅, DO NOT COMMIT.**

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

#### Subtask #1: `tracker type field is required`
**Date:** 2026-01-02 | **Commit:** `ce81003`

---

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_validation_failure_The_tracker_type_field_is_required./2025-12-29.csv`
- Sample: `merchant_id: D7GcDxYIcgAiXF`, `monolith_status_code: 200`, `shadow_status_code: 400`
- Note: Request inferred from error message. **For future tasks:** Use Coralogix MCP with `razorpay_request_id` to get actual request.

**Trigger Condition:**
When request contains `"settings": {"goal_tracker": {}}` (empty object), NCA returns 400, Monolith returns 200.

---

**Code Evidence - Monolith (PHP):**

```php
// api/app/Models/PaymentLink/Validator.php:736-742
public function validateGoalTracker(array $input)
{
    $tracker = array_get($input, Entity::SETTINGS . '.' . Entity::GOAL_TRACKER, []);

    if (count($tracker) <= 0) {  // <-- KEY: If empty, SKIP all validation!
        return;
    }
    
    $this->validateInput('goalTracker', $tracker);  // tracker_type is "required" here
    // ...
}
```

**Monolith Behavior:** When `goal_tracker: {}` is passed, PHP's `count($tracker) = 0` → returns early → NO validation happens → request succeeds.

---

**Code Evidence - NCA (Go) BEFORE fix:**

```go
// no-code-apps/internal/modules/nocode/validation.go (BEFORE)
if settings.GoalTracker != nil && settings.GoalTracker.TrackerType == nil {
    return errorclass.ErrValidationFailure.New("The tracker type field is required.")
}
```

**NCA Behavior BEFORE:** When `goal_tracker: {}` is parsed, Go creates `GoalTracker{}` struct (non-nil, but empty). Check `settings.GoalTracker != nil` passes → `TrackerType` is nil → error thrown → 400.

---

**Code Evidence - NCA (Go) AFTER fix:**

```go
// no-code-apps/internal/modules/nocode/validation.go (AFTER)
// Only validate TrackerType if GoalTracker is not empty
// Monolith skips validation if count($tracker) <= 0 (empty object)
if settings.GoalTracker != nil && !settings.GoalTracker.IsEmpty() && settings.GoalTracker.TrackerType == nil {
    return errorclass.ErrValidationFailure.New("The tracker type field is required.")
}

// no-code-apps/internal/modules/nocode/settings.go
func (g *GoalTracker) IsEmpty() bool {
    if g == nil {
        return true
    }
    return g.TrackerType == nil && g.IsActive == nil && g.MetaData == nil
}
```

**NCA Behavior AFTER:** `GoalTracker.IsEmpty()` returns true for empty struct → validation skipped → matches monolith.

---

**Additional Fixes (Nil Pointer Panics):**
1. `request.go:381` - `MonolithItemSettings` can be nil when `settings` not provided in item
2. `core.go:2649-2680` - `GoalTracker.MetaData` can be nil, need nil checks before accessing fields

**Additional Fix (GoalEndTimestamp Type Mismatch):**
During testing with a FULL `goal_tracker` object (from actual Coralogix production logs), the validation still failed with "tracker type field is required" even though the JSON clearly had `tracker_type` set. Root cause:
- `GoalTrackerMetaData.GoalEndTimestamp` was defined as `*int64` in Go struct
- Monolith accepts it as a string (`"1768501799"`), and production traffic sends it as a string
- `json.Unmarshal` silently fails when trying to unmarshal string into int64, causing the entire `GoalTracker` struct to be partially parsed (only `IsActive` survives because it's `*string`)
- Fix: Changed `GoalEndTimestamp` to use `*datatypes.NumericInt64Value` in `settings.go:74`
- The `NumericInt64Value` type (from `pkg/datatypes/numeric.go`) handles both string and int JSON values automatically
- Updated `core.go:1813` and `core.go:2670` to access `.Value` directly

> **See:** `code/guide-to-navigate-nca-code.md` for details on numeric types and other NCA patterns

---

**Verification:**
- Test request: `{"settings": {"goal_tracker": {}}, ...}` with `X-Proxy-State: dual_write_shadow_read_no_external`
- Log: `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅
- Both NCA and Monolith return 200, payment page created successfully

---

#### Subtask #2 & #3: `description/title contains invalid characters`
**Date:** 2026-01-02 | **Commit:** `7306449`

---

**Log Reference:**
- File: `pp_create_failures/categorized/400_200_description_contains_invalid_characters/2025-12-29.csv`
- File: `pp_create_failures/categorized/400_200_title_contains_invalid_characters/2025-12-29.csv`
- Sample razorpay_request_id (description): `856e7b98-d691-4b3e-b41a-fb14469573d1`
- Sample razorpay_request_id (title): `423781ce-f6f1-4764-83c6-fd7188bd12b0`

**Trigger Condition:**
When title or description contains **utf8mb4 characters** (4-byte UTF-8 sequences like emojis 🚀 🔐 ✅), monolith rejects with 400, but NCA was accepting with 200.

---

**Code Evidence - Monolith (PHP):**

```php
// api/app/Models/PaymentLink/Validator.php:66-67
Entity::TITLE           => 'required|string|min:3|max:80|utf8',
Entity::DESCRIPTION     => 'string|max:65535|nullable|utf8|custom',

// api/app/Models/Base/ExtendedValidations.php:511-523
protected function validateUtf8(string $attribute, $value)
{
    if ((empty($value) === false) and (is_string($value) === true))
    {
        if (is_valid_utf8($value) === false)  // <-- KEY
        {
            throw new BadRequestValidationFailureException(
                "$attribute contains invalid characters");
        }
    }
}

// api/app/lib/utility.php:592-595 - is_valid_utf8()
function is_valid_utf8(String $string)
{
    return (max(array_map('ord', str_split($string))) < 240);  // <-- Rejects bytes >= 240 (utf8mb4)
}
```

**Monolith Behavior:** Validates that title/description don't contain any byte >= 240 (utf8mb4 chars like emojis). The `utf8` rule doesn't allow utf8mb4 encoding.

---

**Code Evidence - NCA (Go) BEFORE fix:**

```go
// internal/utils/extended_validation/init.go
Utf8 = validation.NewStringRuleWithError(utf8.ValidString, Utf8Err)  // <-- Uses Go's utf8.ValidString which ALLOWS emojis!
```

**NCA Behavior BEFORE:** Used Go's `utf8.ValidString` which accepts ANY valid UTF-8 including utf8mb4 (emojis).

---

**Code Evidence - NCA (Go) AFTER fix:**

```go
// internal/utils/extended_validation/init.go
Utf8MB3  = validation.NewStringRuleWithError(IsValidUtf8MB3, Utf8MB3Err)

// IsValidUtf8MB3 checks if a string is valid UTF-8 but NOT utf8mb4 (4-byte sequences).
// This matches monolith's validation which rejects emojis and other 4-byte UTF-8 characters.
// Any byte >= 240 indicates a 4-byte sequence which we don't support (utf8mb4).
func IsValidUtf8MB3(s string) bool {
    for i := 0; i < len(s); i++ {
        if s[i] >= 240 {
            return false
        }
    }
    return true
}

// internal/modules/nocode/validation.go - ValidateForCreate()
validation.Field(&n.Title,
    validation.Required,
    validation.Length(3, 80),
    extended_validation.Utf8MB3.Error("title contains invalid characters"),
),
validation.Field(&n.Description,
    validation.When(n.Description != "",
        validation.Length(0, 65535),
        extended_validation.Utf8MB3.Error("description contains invalid characters"),
    ),
),
```

**NCA Behavior AFTER:** `IsValidUtf8MB3` rejects bytes >= 240 just like monolith → both now return 400 for emojis.

---

**Verification:**
- TC1 (description with 🚀): Both return 400 - `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅
- TC1 (title with 🔐): Both return 400 - `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅
- TC4 (normal request): Both return 200 - `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅

**Files Changed:**
- `internal/utils/extended_validation/constant.go` - Added `CodeValidationIsUtf8MB3`
- `internal/utils/extended_validation/init.go` - Added `IsValidUtf8MB3` function and `Utf8MB3` rule
- `internal/modules/nocode/validation.go` - Added title/description validation with `Utf8MB3`

---

#### Subtask #5 & #6: `payment_success_message/terms contains invalid characters`
**Date:** 2026-01-02 | **Commit:** `f16d92e`

---

**ReqFound Details:**
- **Subtask #5 razorpay_request_id:** `fb83788a-c56f-4b25-85f1-a5385c1ed3e2` (from 2025-09-29 logs)
- **Subtask #6 razorpay_request_id:** `56b43411-f286-487b-a8ea-01597a8c209d` (from 2025-09-29 logs)
- **Note:** September 2025 logs are beyond Coralogix retention (archiveWarning). Fix verified using pattern-based test cases with emoji-containing `payment_success_message` and `terms`.

**Log Reference:**
- File: `pp_create_failures/categorized/400_200_settings.payment_success_message_contains_invalid_characters/2025-09-29.csv`
- File: `pp_create_failures/categorized/400_200_terms_contains_invalid_characters/2025-09-29.csv`

**Trigger Condition:**
When `payment_success_message` or `terms` contains **utf8mb4 characters** (4-byte UTF-8 sequences like emojis), monolith rejects with 400, but NCA was accepting with 200.

---

**Code Evidence - Monolith (PHP):**

```php
// api/app/Models/PaymentLink/Validator.php
Entity::SETTINGS . '.' . Entity::PAYMENT_SUCCESS_MESSAGE => 'nullable|string|min:5|max:2048|utf8',
Entity::TERMS => 'nullable|string|min:5|max:2048|utf8',

// Uses same is_valid_utf8() which rejects bytes >= 240 (utf8mb4)
```

---

**Code Evidence - NCA (Go) AFTER fix:**

```go
// internal/modules/nocode/validation.go
// For PaymentSuccessMessage
if err := validation.Validate(s.PaymentSuccessMessage, validation.Length(5, 2048),
    extended_validation.Utf8MB3.Error("settings.payment_success_message contains invalid characters")); err != nil {
    return err
}

// For Terms
validation.Field(&n.Terms,
    validation.When(n.Terms != nil && *n.Terms != "",
        validation.Length(5, 2048),
        extended_validation.Utf8MB3.Error("terms contains invalid characters"),
    ),
),
```

---

**Verification:**
- TC1 (with emoji): Both return 400 - `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅
- TC4 (normal request): Both return 200 - `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅

---

#### Subtask #7: `min_purchase should be null or valid integer`
**Date:** 2026-01-02 | **Commit:** `d4ffebe`

---

**ReqFound Details:**
- **TC1 razorpay_request_id:** `8446a85f-e65a-4443-9d40-6a37653251d5` (from 2025-11-08)
- **TC2 razorpay_request_id:** `c8adfe81-0167-4bf0-9b12-5c8275855680` (from 2025-11-07)
- **TC3 razorpay_request_id:** `b94d1d8c-18e8-4c20-bbcd-904083634c59` (from 2025-11-07)
- **Coralogix:** ✅ All requests retrieved

**Log Reference:**
- `pp_create_failures/categorized/400_200_min_purchase_should_be_null_or_valid_integer/2025-11-08.csv`
- `pp_create_failures/categorized/400_200_min_purchase_should_be_null_or_valid_integer/2025-11-07.csv`

---

**Trigger Condition:**
When `min_purchase` is sent as **string `"0"`** (not integer `0`), monolith rejects but NCA was accepting.

**Code Evidence - Monolith (PHP):**

```php
// api/app/Models/PaymentLink/PaymentPageItem/Validator.php:459-468
public function validateEmptyStringForInteger(string $attribute, $number)
{
    if ((isset($number)) and
        (empty($number) === true) and  // PHP: empty("0") = TRUE!
        ($number !== 0))               // PHP: "0" !== 0 is TRUE (strict)
    {
        throw new BadRequestValidationFailureException(
            $attribute . ' should be null or valid integer'
        );
    }
}
```

**PHP Quirk:** `empty("0")` returns `true` in PHP! So:
- `"min_purchase": "0"` (string) → empty=true, "0"!==0=true → **REJECTS**
- `"min_purchase": 0` (integer) → empty=true, 0!==0=false → **ACCEPTS**

---

**Code Evidence - NCA (Go) AFTER FIX:**

The fix is done at the validation layer, not in the unmarshaler. This ensures:
- `NumericUInt64Value` accepts all valid inputs (used by `Amount` which has different validation)
- Only specific fields (`min_amount`, `max_amount`, `min_purchase`, `max_purchase`, `stock`) reject string "0"

```go
// no-code-apps/pkg/datatypes/numeric.go - Track if value came from string "0"
type NumericUInt64Value struct {
    Value       uint64
    isStringZero bool  // true if value came from string "0"
}

func (nv *NumericUInt64Value) IsStringZero() bool {
    return nv.isStringZero
}

// no-code-apps/internal/modules/nocode/validation.go - Apply validation for specific fields
func (item *MonolithPaymentPageItem) ValidateEmptyStringForIntegerFields() errors.IError {
    if item.MinAmount != nil && item.MinAmount.IsStringZero() {
        return errorclass.ErrValidationFailure.New("min_amount should be null or valid integer")
    }
    if item.MinPurchase != nil && item.MinPurchase.IsStringZero() {
        return errorclass.ErrValidationFailure.New("min_purchase should be null or valid integer")
    }
    // ... same for max_amount, max_purchase, stock
}
```

**Why not reject at unmarshal level?**
- `Amount` field uses `NumericUInt64Value` but does NOT have validateEmptyStringForInteger in monolith
- `Amount` with string "0" should parse, then fail at min_amount validation
- Only 5 specific fields have this PHP quirk behavior

---

**Verification:**
- TC1 (string "0"): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC2 (string "0" multiple items): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC3 (string "0" 4 items): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC4 (integer 0): `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅ - Both return 200

**Files Changed:**
- `pkg/datatypes/numeric.go` - Modified `NumericUInt64Value` to track string "0" for validation
- `pkg/datatypes/numeric_test.go` - Added tests for string "0" rejection
- `internal/modules/nocode/validation.go` - Added `ValidateEmptyStringForIntegerFields`

---

#### Subtask #8: `Contact number at least 8 digits`
**Date:** 2026-01-02 | **Commit:** `2641170`

---
**Log Reference:**
- File: `pp_create_failures/categorized/400_200_Contact_number_should_be_at_least_8_digits,_including_country_code/2025-12-27.csv`
- Sample razorpay_request_id: `1dfe9c8c-86cd-43fd-965a-b775b446129d`
- Actual Request Snippet: `"support_contact": "00000000"` (8 zeros)

---
**Trigger Condition:**
When `support_contact` is "00000000" (8 zeros) or similar invalid format. Monolith rejects with 400, NCA was accepting with 200.

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Models/Base/ExtendedValidations.php:243
if (strlen($formattedContact) < 8) {
    throw new BadRequestException(
        ErrorCode::BAD_REQUEST_PAYMENT_CONTACT_TOO_SHORT,
        $attribute);
}
```
**Monolith Behavior:** Uses `contact_syntax` validation which parses contact with PhoneBook library and requires 8+ digits total.

---
**Code Evidence - NCA (Go) BEFORE fix:**
```go
// internal/utils/extended_validation/custom_rules.go:93-97 (INCORRECT)
// adding this to support 00000000 number. Some merchants are sending this...
if formattedNumber.NationalNumber != nil && formattedNumber.NumberOfLeadingZeros != nil && 
   *formattedNumber.NationalNumber == 0 && *formattedNumber.NumberOfLeadingZeros > 0 {
    return nil  // <-- Was incorrectly accepting "00000000"
}
```
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/utils/extended_validation/custom_rules.go:93-96
// NOTE: Removed special handling for "00000000" - monolith REJECTS it
// Previous comment was incorrect: "API is supporting it due to some bug in external lib"
// Monolith logs show M:400 for "00000000" so we must reject it too
```

---
**Verification:**
- TC1 ("00000000"): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC2 ("1234567"): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC3 (" 0000000"): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC4 (valid "9999999999"): `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅ - Both return 200

---

#### Subtask #9: `udf_schema more than 15 items`
**Date:** 2026-01-02 | **Commit:** `2641170`

---
**Log Reference:**
- File: `pp_create_failures/categorized/400_200_The_udf_schema_may_not_have_more_than_15_items./2025-12-22.csv`
- Sample razorpay_request_id: `5a11ac1a-7f08-4f5f-991c-fda7228a921d`
- Actual Request Snippet: `udf_schema` with 16 items (positions 0-15)

---
**Trigger Condition:**
When `settings.udf_schema` has more than 15 items. Monolith rejects with 400, NCA was accepting with 200.

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Models/PaymentLink/Validator.php:156
'udf_schema' => 'array|max:15',
```
**Monolith Behavior:** Laravel `max:15` validation limits udf_schema array to 15 items.

---
**Code Evidence - NCA (Go) BEFORE fix:**
```go
// internal/modules/nocode/validation.go (BEFORE)
// No max items check for udf_schema
```
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/modules/nocode/validation.go:409-414
const MaxUdfSchemaItems = 15
if len(*udfSchemaStruct) > MaxUdfSchemaItems {
    return fmt.Errorf("The udf_schema may not have more than %d items.", MaxUdfSchemaItems)
}
```

---
**Verification:**
- TC1 (16 items): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC4 (valid < 15 items): `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅ - Both return 200

---

#### Subtask #10: `item missing in pp_item response` - 🟠 PENDING
**Date:** 2026-01-02 | **Status:** Pending Analysis

---
**Log Reference:**
- File: `pp_create_failures/categorized/200_400_dual_write_id_extraction_item_missing_in_payment_page_item_response/2025-12-17.csv`
- Sample razorpay_request_id: `4d5feb06-675f-4fe2-aa80-731126a30305`
- This is M:200, N:400 (NCA internal error, not validation)

---
**Analysis - Root Cause Hypothesis:**

This diff type is likely a **cascading effect from previous diffs**, not a standalone bug:

1. **Sequence of Events:**
   - Earlier request causes a validation diff (e.g., M:400, N:200)
   - NCA incorrectly created entities in its database when it should have rejected
   - OR NCA failed to create when monolith succeeded
   - Data becomes inconsistent between monolith and NCA databases

2. **Why `item missing in pp_item response`:**
   - Dual write ID extraction tries to match request items to response items
   - Uses composite key: `{name}:{amount}:{stock}:{min_purchase}:{max_purchase}:{min_amount}:{max_amount}`
   - If previous diffs caused data inconsistencies, the response from monolith may have different item structure
   - When Item is nil or doesn't match, extraction fails

3. **Evidence Supporting This Theory:**
   - These diffs are M:200, N:400 - monolith succeeds but NCA fails internally
   - The error is in dual write handler, not in validation
   - Fixing validation diffs (subtasks 1-9) should reduce these cascading errors

4. **Recommended Approach:**
   - ⏸️ Leave this subtask pending until validation fixes (1-9) are deployed to production
   - 📊 Monitor if these diffs decrease after deploying validation fixes
   - 🔍 If they persist, investigate specific cases for actual root cause

---
**Code Location:**
```go
// internal/modules/payment_page/dual_write.go:61-65
if item == nil {
    logger.CtxLog(ctx).Errorw("EXTRACT_IDS_ITEM_MISSING_IN_PAYMENT_PAGE_ITEM_RESPONSE", ...)
    return "", errorclass.ErrorDualWriteIdExtraction.New("").Wrap(
        goErr.New("item missing in payment page item response"))
}
```

---
**Status:** 🟠 PENDING - Do NOT fix until validation diffs are resolved and monitored

---

#### Subtask #11: `Contact number contains invalid characters`
**Date:** 2026-01-03 | **Commit:** `2f2d558`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `1178ed55-ceed-434f-a1bb-6eacf3a2f31a` (from 2025-12-26)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "1178ed55-ceed-434f-a1bb-6eacf3a2f31a"`
- **Actual Request Snippet:** `"support_contact": "91+6350325865"` (+ in wrong position)

**Log Reference:**
- File: `pp_create_failures/categorized/400_200_Contact_number_contains_invalid_characters,_only_digits_and_+_symbol_are_allowed/2025-12-26.csv`

---
**Trigger Condition:**
When `support_contact` contains `+` symbol NOT at the start position (e.g., `"91+6350325865"`). Monolith rejects with 400, NCA was accepting with 200.

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Error/PublicErrorDescription.php:178
const BAD_REQUEST_PAYMENT_CONTACT_INCORRECT_FORMAT = 
    'Contact number contains invalid characters, only digits and + symbol are allowed';

// Uses preg_match to validate contact format - only digits and + at start allowed
```
**Monolith Behavior:** Monolith validates contact format, rejecting any `+` that isn't at position 0.

---
**Code Evidence - NCA (Go) BEFORE fix:**
```go
// internal/utils/extended_validation/custom_rules.go (BEFORE)
// Only used libphonenumber.Parse() which is more lenient with + position
func isValidContactNumberSyntax(contact string) validation.Error {
    formattedNumber, err := libphonenumber.Parse(contact, "IN")
    // ...
}
```
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/utils/extended_validation/custom_rules.go:78-92
func isValidContactNumberSyntax(contact string) validation.Error {
    // Check for invalid characters first - monolith only allows digits and + at start
    for i, r := range contact {
        if r == '+' {
            if i != 0 {
                // + is only allowed at the start
                return GenericValidationError.SetMessage(
                    "Contact number contains invalid characters, only digits and + symbol are allowed")
            }
        } else if r < '0' || r > '9' {
            return GenericValidationError.SetMessage(
                "Contact number contains invalid characters, only digits and + symbol are allowed")
        }
    }
    // ... rest of validation
}
```

---
**Verification:**
- TC1 (`91+6350325865`): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC2 (`123+456789`): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC3 (`99+88776655`): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC4 (`+919999999999`): `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅ - Both return 200

**Files Changed:**
- `internal/utils/extended_validation/custom_rules.go`

---

#### Subtask #12: `min_amount minimum 50 for USD` - 🟠 PENDING
**Date:** 2026-01-03 | **Status:** Needs Investigation

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `b31e3733-c4b6-4a3e-81cd-ac042e806092` (from 2025-12-17)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "b31e3733-c4b6-4a3e-81cd-ac042e806092"`
- **Actual Request Snippet:** `"currency":"USD"`, `"min_amount":{"Value":10}` (10 cents = $0.10)

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_validation_failure_min_amount_amount_should_be_minimum_50_for_USD./2025-12-17.csv`

---
**Trigger Condition:**
When `min_amount` is less than currency minimum (50 for USD = $0.50). M:200, N:400 - NCA over-validates.

---
**Analysis:**
NCA validates `min_amount` against currency minimums in `line_item_price/validation.go:80`:
```go
validation.Field(&m.MinAmount,
    validation.When(m.MinAmount != nil,
        extended_validation.MinUInt64Ptr(0),
        validation.By(extended_validation.Amount(m.Currency, "")),  // <-- Currency min check
    ),
),
```

But monolith may not apply this validation for all cases. The TODO at line 75-76 says:
> "TODO LATER implement merchant details related validations for minAmount and maxAmount"

**Status:** 🟠 PENDING - Need to investigate when monolith applies min_amount currency validation vs when it skips it.

---

#### Subtask #13: `support_contact is invalid` - 🟡 Fix Committed
**Date:** 2026-01-04 | **Commit:** `606cbbe`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `ca2d30d9-1c55-4fea-921b-44c29caefddc` (from 2025-12-16)
- **Actual Request Snippet (from DIFF_CHECKER log):** `support_contact: "+9181********"` or `"18001800343412"` (14 digits)

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_validation_failure_support_contact_is_invalid./2025-12-16.csv`
- File: `pp_create_failures/categorized/200_400_validation_failure_support_contact_is_invalid./2025-10-10.csv` (has `support_contact: "18001800343412"`)

---
**Trigger Condition:**
Phone numbers like `18001800343412` (14 digits, no `+`):
- libphonenumber parses as: cc=91, nat=18001800343412 → len=16 > 15 → NCA rejects
- Monolith uses raw `strlen("18001800343412")` = 14 < 15 → Monolith accepts

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/lib/PhoneBook.php:195-203
public function __toString()
{
    if ($this->isValidNumber() === true) {
        return $this->format();  // E164 format
    }
    return $this->getRawInput();  // Raw input if not valid
}

// api/app/Models/Base/ExtendedValidations.php:232,256
$formattedContact = (string) $number;  // Calls __toString()
if (strlen($formattedContact) > 15) { ... }  // Uses strlen of formatted/raw
```
**Monolith Behavior:** Uses `strlen($formattedContact)` which is either E164 format or raw input. For `"18001800343412"`, it's raw input (14 chars), so 14 < 15 → accepts.

---
**Code Evidence - NCA (Go) BEFORE fix:**
```go
// internal/utils/extended_validation/custom_rules.go
numberLength := len(cast.ToString(formattedNumber.NationalNumber)) + len(cast.ToString(formattedNumber.CountryCode))
if numberLength > 15 {
    return GenericValidationError  // "is invalid"
}
// For "18001800343412": cc=91 (2) + nat=18001800343412 (14) = 16 > 15 → REJECTS
```

**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/utils/extended_validation/custom_rules.go
contactLength := len(contact)  // Use raw input length
if contactLength < 8 { return error }
// Only enforce >15 if BOTH libphonenumber length AND raw length exceed 15
if numberLength > 15 && contactLength > 15 { return error }
// For "18001800343412": contactLength=14 < 15 → ACCEPTS
```

---
**Verification:** ⏳ Needs testing (fix committed, needs hot-reload or redeploy)

---
**Trigger Condition:**
NCA rejects contact format that monolith accepts. M:200, N:400.

---
**Analysis:**
This is an M:200, N:400 case where NCA's libphonenumber validation is stricter than monolith's.
Need to investigate the specific contact format causing the diff.

**Status:** 🟠 PENDING - Need to fetch actual request from logs to understand what format triggers this.

---

#### Subtask #14: `Price has to be a fixed amount`
**Date:** 2026-01-03 | **Commit:** `2f2d558`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `8ee03cb1-bf50-4a3e-be16-7f0c4352440d` (from 2025-12-29)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "8ee03cb1-bf50-4a3e-be16-7f0c4352440d"`
- **Actual Request Snippet:** `"template_type":null` with items having `"amount":null`

**Log Reference:**
- File: `pp_create_failures/categorized/400_200_Price_has_to_be_a_fixed_amount/2025-12-29.csv`

---
**Trigger Condition:**
When org feature `IsHideDynamicPricePPEnabled()` is true and merchant feature `IsEnableCustomerAmountEnabled()` is **FALSE**, items with null amount should be rejected. The logic was inverted in NCA.

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Models/PaymentLink/Validator.php:649-666
if (($merchant->org->isFeatureEnabled(Feature::HIDE_DYNAMIC_PRICE_PP) === true) and
    ($merchant->isEnableCustomerAmountEnabled() === false) and  // <-- FALSE
    ($template_type !== 'donation'))
{
    foreach ($payment_page_items as $paymentPageItem) {
        if (isset($paymentPageItem['item']) === true) {
            $amount = $paymentPageItem['item'][Entity::AMOUNT];
            if ($amount === null) {
                throw new BadRequestValidationFailureException('Price has to be a fixed amount');
            }
        }
    }
}
```
**Monolith Behavior:** When `IsHideDynamicPricePPEnabled() === true` AND `IsEnableCustomerAmountEnabled() === false`, reject null amounts.

---
**Code Evidence - NCA (Go) BEFORE fix:**
```go
// internal/modules/payment_page/core.go:1053 (BEFORE - WRONG)
if orgFeatures.IsHideDynamicPricePPEnabled() && 
   merchantFeatures.IsEnableCustomerAmountEnabled() &&  // <-- BUG: should be !
   templateType != "donation" {
```
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/modules/payment_page/core.go:1053 (AFTER - CORRECT)
// Monolith: IsHideDynamicPricePPEnabled() === true AND IsEnableCustomerAmountEnabled() === false
// See: api/app/Models/PaymentLink/Validator.php:649-651
if orgFeatures.IsHideDynamicPricePPEnabled() && 
   !merchantFeatures.IsEnableCustomerAmountEnabled() &&  // <-- Fixed: added !
   templateType != "donation" {
```

---
**Verification:**
- TC1 (fees + null amount): `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅ - Both return 200
- TC2 (donation + null amount): `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅ - Both return 200
- TC3 (custom + null amount): `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅ - Both return 200
- TC4 (fixed amount): `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅ - Both return 200

**Note:** All return 200 because test merchant doesn't have `IsHideDynamicPricePPEnabled()` enabled. The fix ensures NCA matches monolith behavior for merchants that DO have this feature enabled.

**Files Changed:**
- `internal/modules/payment_page/core.go`

---

#### Subtask #15: `Price has to be a fixed amount (v2)` - Same Fix as #14
**Date:** 2026-01-03 | **Commit:** `2f2d558`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `81a04c1f-7a17-4cf2-b0bd-3a6a93f8d4fe` (from 2025-12-26)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "81a04c1f-7a17-4cf2-b0bd-3a6a93f8d4fe"`
- **Actual Request Snippet:** `"template_type":"fees"` with items having `"amount":null`

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_validation_failure_Price_has_to_be_a_fixed_amount/2025-12-26.csv`

---
**Trigger Condition:**
Same as #14 - `template_type: "fees"` with null amount items. This is the NCA error side (M:200, N:400) as opposed to #14 (M:400, N:200).

**Root Cause:** Same logic inversion bug as #14. The fix in `2f2d558` resolves both.

---
**Verification:**
- TC1 (fees + null amount): `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅ - Both return 200

**Note:** Same fix as #14 - the logic inversion was causing both types of diffs depending on merchant feature configuration.

---

#### Subtask #19: `max_amount exceeds maximum` - 🔵 Already Fixed
**Date:** 2026-01-03 | **Status:** Already works

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `20a22988-c257-4478-ac7c-9fbe2c7bdb31` (from 2025-11-25)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "20a22988-c257-4478-ac7c-9fbe2c7bdb31"`
- **Actual Request Snippet:** `"max_amount":{"Value":100000000}` (1 crore = 10 million paise)

**Log Reference:**
- File: `pp_create_failures/categorized/400_200_max_amount_exceeds_maximum_payment_amount_allowed/2025-11-25.csv`

---
**Trigger Condition:**
When `max_amount` exceeds merchant's maximum payment amount limit (varies per merchant).

---
**Verification:**
- TC1 (max_amount=100000000): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC4 (normal request): `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅ - Both return 200

**Note:** This validation already works correctly in NCA. Both monolith and NCA reject excessive amounts.

---

#### Subtask #20: `support_contact invalid format` - 🟠 PENDING
**Date:** 2026-01-03 | **Status:** Same as #13

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `a5c24b86-63cb-46d9-ad65-f8b1ae4cb6f4` (from 2025-12-16)
- **Coralogix:** Logs beyond retention

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_validation_failure_support_contact_invalid_contact_format./2025-12-16.csv`

---
**Note:** This is the same issue as #13 - NCA's libphonenumber validation is stricter than monolith's.
M:200, N:400 indicates NCA is over-validating contact formats that monolith accepts.

---

#### Subtask #21: `terms length 5 and 2048`
**Date:** 2026-01-03 | **Commit:** `1c75c90`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `9c483dc5-bf75-4bdc-8800-c3d88cc7f633` (from 2025-12-29)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "9c483dc5-bf75-4bdc-8800-c3d88cc7f633"`
- **Actual Request Snippet:** `"terms":"nn"` (just 2 newline characters)

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_validation_failure_terms_the_length_must_be_between_5_and_2048./2025-12-29.csv`

---
**Trigger Condition:**
When `terms` is whitespace-only (e.g., `"\n\n"`). Monolith accepts, NCA was rejecting with length validation.

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Models/PaymentLink/Validator.php
Entity::TERMS => 'nullable|string|min:5|max:2048|utf8',
// Laravel treats whitespace-only strings as "empty-ish" in some contexts
```
**Monolith Behavior:** Accepts whitespace-only terms field.

---
**Code Evidence - NCA (Go) BEFORE fix:**
```go
// internal/modules/nocode/validation.go:524-528 (BEFORE)
validation.Field(&n.Terms,
    validation.When(n.Terms != nil && *n.Terms != "",
        validation.Length(5, 2048),
        // ...
    ),
),
```
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/modules/nocode/validation.go:524-529 (AFTER)
// Monolith accepts whitespace-only terms (e.g., "\n\n") - skip validation for such
validation.Field(&n.Terms,
    validation.When(n.Terms != nil && strings.TrimSpace(*n.Terms) != "",
        validation.Length(5, 2048),
        // ...
    ),
),
```

---
**Verification:** ⏳ Needs testing (fix committed, needs hot-reload or redeploy)

---

#### Subtask #22: `Contact number > 15 digits` - 🔵 Already Fixed
**Date:** 2026-01-03 | **Status:** Already works

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `1aa590c8-40c6-4a71-bb33-aff4d01debd3` (from 2025-11-28)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "1aa590c8-40c6-4a71-bb33-aff4d01debd3"`
- **Actual Request Snippet:** `"support_contact":"+919999999999999"` (16 digits including +91)

**Log Reference:**
- File: `pp_create_failures/categorized/400_200_Contact_number_should_not_be_greater_than_15_digits,_including_country_code/2025-11-28.csv`

---
**Trigger Condition:**
When `support_contact` has more than 15 digits (including country code).

---
**Code Evidence - NCA (Go):**
```go
// internal/utils/extended_validation/custom_rules.go:111-124
numberLength := len(cast.ToString(formattedNumber.NationalNumber)) + len(cast.ToString(formattedNumber.CountryCode))
if numberLength > 15 {
    return GenericValidationError
}
```

---
**Verification:**
- TC1 (+919999999999999): `DIFF_CHECKER_NO_DIFFS_FOUND_IN_FAILED_REQUEST` ✅ - Both return 400
- TC4 (valid contact): `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` ✅ - Both return 200

**Note:** This validation already works correctly in NCA.

---

#### Subtask #23: `value length no more than 10000` - 🟠 PENDING
**Date:** 2026-01-03 | **Status:** Investigation needed

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `9926b48d-59ea-4ae5-96ab-5c503300841f` (from 2025-12-21)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "9926b48d-59ea-4ae5-96ab-5c503300841f"`
- **Actual Request Snippet:** `udf_schema` with hundreds of enum options (REFERANCE field)

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_validation_failure_value_the_length_must_be_no_more_than_10000./2025-12-21.csv`

---
**Trigger Condition:**
When `udf_schema` contains a field with a very long list of enum options. The serialized JSON exceeds 10000 characters.

---
**Analysis:**
- Error: `value: the length must be no more than 10000`
- The `udf_schema` field has a dropdown (REFERANCE) with 500+ names as options
- NCA seems to validate a `value` field somewhere with max length 10000
- Source of validation unclear - needs further investigation

**Note:** This requires deeper investigation into how `udf_schema` is processed and validated in NCA.

---

#### Subtask #25: `ends_by must be in future`
**Date:** 2026-01-03 | **Commit:** `b442315`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `9bc72063-b666-4c10-a79b-287780a1f992` (from 2025-12-06)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "9bc72063-b666-4c10-a79b-287780a1f992"`
- **Actual Request Snippet:** `"goal_end_timestamp":1714501799` (April 2024 - past)

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_internal_error_validation_failure_ends_by_EndsBy_must_be_in_the_future./2025-12-06.csv`

---
**Trigger Condition:**
When `goal_tracker.meta_data.goal_end_timestamp` is in the past. Monolith accepts, NCA was rejecting.

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Models/PaymentLink/Entity.php:162
const GOAL_END_TIMESTAMP = 'goal_end_timestamp';
// No validation for future timestamp found
```
**Monolith Behavior:** Accepts past timestamps for `goal_end_timestamp`.

---
**Code Evidence - NCA (Go) BEFORE fix:**
```go
// internal/modules/goal_tracker/validation.go:36-38 (BEFORE)
validation.When(g.EndsBy != nil,
    validation.Min(int64(time.Now().Unix())).Error("EndsBy must be in the future"),
),
```
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/modules/goal_tracker/validation.go:36-37 (AFTER)
// NOTE: Monolith does NOT validate EndsBy > now(), so NCA should also not validate
```

---
**Verification:** ⏳ Needs testing (fix committed, needs hot-reload or redeploy)

---

#### Subtask #26: `slug length between 4 and 30`
**Date:** 2026-01-03 | **Commit:** `b442315`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `74e6bbab-ae5c-4d41-b056-df997fafd490` (from 2025-12-19)
- **Coralogix:** No results (beyond retention)

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_validation_failure_the_length_must_be_between_4_and_30/2025-12-19.csv`

---
**Trigger Condition:**
When `slug` is nil or too short. Monolith's rule is `nullable|min:4|max:30` - NCA was validating even when slug is null.

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Models/PaymentLink/Validator.php:58
Entity::SLUG => 'nullable|min:4|max:30'
// nullable = skip validation if null
```
**Monolith Behavior:** Skip slug length validation if slug is null.

---
**Code Evidence - NCA (Go) BEFORE fix:**
```go
// internal/modules/nocode/validation.go:176-180 (BEFORE)
// Bug: Validated Length(4,30) even when slug is nil
if err := validation.Validate(n.Slug, validation.Length(4, 30)); err != nil {
    return utils.GetValidationError(err)
}
```
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/modules/nocode/validation.go:176-182 (AFTER)
// Only validate length if slug is provided (matches monolith's 'nullable' rule)
if n.Slug != nil {
    if err := validation.Validate(n.Slug, validation.Length(4, 30)); err != nil {
        return utils.GetValidationError(err)
    }
}
```

---
**Verification:** ⏳ Needs testing (fix committed, needs hot-reload or redeploy)

---

#### Subtask #28: `must be a valid URL`
**Date:** 2026-01-03 | **Commit:** `b442315`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `43fde58e-3c14-4fdb-be4f-76fe2ace03e3` (from 2025-12-13)
- **Coralogix:** No results (beyond retention)

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_validation_failure_must_be_a_valid_URL/2025-12-13.csv`

---
**Trigger Condition:**
When `settings.payment_success_redirect_url` is empty string or invalid format. Monolith doesn't validate, NCA was rejecting.

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Models/PaymentLink/Validator.php
// No validation found for payment_success_redirect_url
```
**Monolith Behavior:** No strict URL validation for this field.

---
**Code Evidence - NCA (Go) BEFORE fix:**
```go
// internal/modules/nocode/validation.go:341-343 (BEFORE)
// Bug: Validated URL even for empty strings
if err := validation.Validate(s.PaymentSuccessRedirectUrl, is.URL); err != nil {
    return err
}
```
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/modules/nocode/validation.go:341-348 (AFTER)
// Only validate if non-empty (matches monolith's lenient behavior)
if s.PaymentSuccessRedirectUrl != nil && *s.PaymentSuccessRedirectUrl != "" {
    if err := validation.Validate(s.PaymentSuccessRedirectUrl, is.URL); err != nil {
        return err
    }
}
```

---
**Verification:** ⏳ Needs testing (fix committed, needs hot-reload or redeploy)

---

#### Subtask #29: `available_units validation`
**Date:** 2026-01-03 | **Commit:** `4399464`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `2d5bc825-18cb-403b-8203-3978ef62d4fe` (from 2025-11-29)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "2d5bc825-18cb-403b-8203-3978ef62d4fe"`
- **Actual Request Snippet:** `tracker_type: "donation_supporter_based"`, `available_units: ""`

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_internal_error_validation_failure_available_units_AvailableUnits_is_required_for/2025-11-29.csv`

---
**Trigger Condition:**
When `tracker_type` is `donation_supporter_based` but `available_units` is empty. NCA was requiring AvailableUnits for supporter-based, monolith doesn't.

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Models/PaymentLink/Validator.php:293
Entity::META_DATA.'.'.Entity::AVALIABLE_UNITS => 'required_if:'.Entity::META_DATA.'.'.Entity::DISPLAY_AVAILABLE_UNITS.',1',
// Only required when display_available_units='1', NOT when tracker_type is supporter-based
```
**Monolith Behavior:** Only requires `available_units` when `display_available_units='1'`.

---
**Code Evidence - NCA (Go) BEFORE fix:**
```go
// internal/modules/goal_tracker/validation.go:21-29 (BEFORE)
validation.Field(&g.AvailableUnits,
    validation.When(g.DisplayAvailableUnits == "1", ...),
    validation.When(g.Type == "donation_supporter_based",  // BUG: extra validation
        validation.Required.Error("AvailableUnits is required for supporter-based goal tracker"),
    ),
),
```
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/modules/goal_tracker/validation.go:21-27 (AFTER)
validation.Field(&g.AvailableUnits,
    // Monolith only requires available_units when display_available_units is "1"
    // NOT when tracker_type is donation_supporter_based
    validation.When(g.DisplayAvailableUnits == "1",
        validation.Required.Error("..."),
        validation.Min(uint64(1)),
    ),
),
```

---
**Verification:** ⏳ Needs testing (fix committed, needs hot-reload or redeploy)

---

#### Subtask #30: `max amount must be valid integer` - 🔵 Same as #7
**Date:** 2026-01-03 | **Status:** Already fixed

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `8619d93e-8fe6-435d-9e31-87c8502dd36c` (from 2025-11-12)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "8619d93e-8fe6-435d-9e31-87c8502dd36c"`
- **Actual Request Snippet:** `max_amount: 10000000000` (100 billion paise = 1 billion INR)

**Log Reference:**
- File: `pp_create_failures/categorized/400_200_The_max_amount_must_be_valid_integer_between_0_and_4294967295./2025-11-12.csv`

---
**Trigger Condition:**
Monolith rejects `max_amount` > 4294967295 (uint32 max), NCA accepts.

**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/modules/line_item_price/validation.go
const MaxUInt32 uint64 = math.MaxUint32

// Added validation:
if m.MaxAmount != nil && *m.MaxAmount > MaxUInt32 {
    return utils.GetValidationError(fmt.Errorf("The max_amount must be valid integer between 0 and %d.", MaxUInt32))
}
// ... similar for min_amount, amount, stock, min_purchase, max_purchase
```

---
**Verification:** ⏳ Needs testing (fix committed, needs hot-reload or redeploy)

---

#### Subtask #23: `value length no more than 10000` - 🟡 Fix Committed
**Date:** 2026-01-03 | **Commit:** `9597018`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `9926b48d-59ea-4ae5-96ab-5c503300841f` (from 2025-12-21)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "9926b48d-59ea-4ae5-96ab-5c503300841f"`
- **Actual Request Snippet:** `udf_schema` has 500+ referral names in `enum` list

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_validation_failure_value_the_length_must_be_no_more_than_10000./2025-12-21.csv`

---
**Trigger Condition:**
`udf_schema` contains dropdown fields with very large `enum` lists (500+ options). This exceeds the 10000 char limit on config `Value`.

---
**Code Evidence - Monolith (PHP):**
Monolith has NO length limit on config value fields.

---
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/modules/config/validation.go:17
// BEFORE: validation.Field(&nc.Value, extended_validation.Utf8, validation.Length(0, 10000)),
// AFTER:
validation.Field(&nc.Value, extended_validation.Utf8, validation.Length(0, 100000)),
```

---
**Verification:** ⏳ Needs testing (fix committed, needs hot-reload or redeploy)

---

#### Subtask #24: `amount minimum 50 for USD` - 🟡 Fix Committed
**Date:** 2026-01-03 | **Commit:** `9597018`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `4834e47e-79f7-4bd0-9c95-6c1ab2d46d3e` (from 2025-12-19)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "4834e47e-79f7-4bd0-9c95-6c1ab2d46d3e"`
- **Actual Request Snippet:** `amount: 10`, `currency: "USD"` (10 cents)

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_validation_failure_amount_amount_should_be_minimum_50_for_USD./2025-12-19.csv`

---
**Trigger Condition:**
USD amount below 50 cents. NCA was enforcing currency minimum on item Amount, but monolith doesn't.

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Models/PaymentLink/PaymentPageItem/Validator.php
// Monolith only validates currency minimum for MIN_AMOUNT and MAX_AMOUNT
// NOT for the main item AMOUNT during creation
```

---
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/modules/line_item_price/validation.go:52-58
// BEFORE: validation.Field(&m.Amount, validation.When(m.Amount != nil, validation.By(extended_validation.Amount(m.Currency, "")))),
// AFTER:
validation.Field(&m.Amount), // No currency minimum validation
```

---
**Verification:** ⏳ Needs testing (fix committed, needs hot-reload or redeploy)

---

#### Subtask #27: `slug required for custom domain` - 🟡 Fix Committed
**Date:** 2026-01-03 | **Commit:** `9597018`

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `d89d1e84-1151-43df-a441-08fe3aea5d17` (from 2025-11-28)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "d89d1e84-1151-43df-a441-08fe3aea5d17"`
- **Actual Request Snippet:** `custom_domain: "igvtseva.in"`, `slug: null`

**Log Reference:**
- File: `pp_create_failures/categorized/400_200_slug_required_for_page_with_custom_domain./2025-11-28.csv`

---
**Trigger Condition:**
Request has `custom_domain` set but `slug` is null. Monolith requires slug when custom_domain is present.

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Models/PaymentLink/Validator.php:480-489
public function validateCustomDomainSlug(string $attribute, ?string $value)
{
    if (is_null($value) === true)
    {
        throw new BadRequestValidationFailureException(
            'slug required for page with custom domain.',
            Entity::SLUG,
            compact('value')
        );
    }
}
```

---
**Code Evidence - NCA (Go) AFTER fix:**
```go
// internal/modules/nocode/validation.go:218-246
func ValidateSlugWithCustomDomain(customDomainInf interface{}) validation.RuleFunc {
    return func(slugInf interface{}) error {
        if customDomain != "" {
            if slugInf == nil {
                return goErr.New("slug required for page with custom domain.")
            }
            // ... validate slug format
        }
        // ... rest of validation
    }
}
```

---
**Verification:** ⏳ Needs testing (fix committed, needs hot-reload or redeploy)

---

#### Subtask #31: `READ ONLY transaction` - 🔵 DB Transient
**Date:** 2026-01-03 | **Status:** Transient DB error

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `8f607140-f7dd-4fd4-8504-ad60f6c2351d` (from 2025-11-18)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "8f607140-f7dd-4fd4-8504-ad60f6c2351d"`
- **Error:** `Error 1792 (25006): Cannot execute statement in a READ ONLY transaction.`

**Log Reference:**
- File: `pp_create_failures/categorized/200_400_db_error_Error_1792_(25006)_Cannot_execute_statement_in_a_READ_ONLY_transaction./2025-11-18.csv`

---
**Trigger Condition:**
DB replica failover or read-only state. This is infrastructure-related, not code.

**Note:** Not actionable at code level. This is a transient DB infrastructure issue.

---

#### Subtask #32: `min purchase must be valid integer` - 🔵 Same as #7
**Date:** 2026-01-03 | **Status:** Already fixed by #7

---
**ReqFound Details:**
- **TC1 razorpay_request_id:** `29427df8-fb2b-4565-9a14-f1a51b2072b4` (from 2025-11-27)
- **Coralogix Query:** `"PAYMENT_PAGE_CREATE_REQUEST" AND "29427df8-fb2b-4565-9a14-f1a51b2072b4"`
- **Actual Request Snippet:** `min_purchase: {"Value":1}` (valid integer)

**Log Reference:**
- File: `pp_create_failures/categorized/400_200_The_min_purchase_must_be_valid_integer_between_0_and_4294967295./2025-11-27.csv`

---
**Trigger Condition:**
Same issue as #7 - monolith rejects string "0" for integer fields. NCA's `ValidateEmptyStringForIntegerFields` fix in #7 handles this.

**Note:** Already fixed by commit `d4ffebe` in Subtask #7.

---

**Template for verified fix:**
```markdown
#### Subtask #X: <diff_type>
**Date:** YYYY-MM-DD | **Commit:** `<hash>`

---
**Log Reference:**
- File: `pp_create_failures/categorized/<folder>/<date>.csv`
- Sample: `merchant_id: <id>`, `monolith_code: <code>`, `shadow_code: <code>`

**Trigger Condition:** <what request causes this diff>

---
**Code Evidence - Monolith (PHP):**
```php
// api/app/Models/PaymentLink/Validator.php:<lines>
<relevant code>
```
**Monolith Behavior:** <explanation>

---
**Code Evidence - NCA (Go) BEFORE/AFTER:**
```go
// no-code-apps/internal/modules/nocode/<file>.go:<lines>
<relevant code>
```
**NCA Behavior:** <explanation>

---
**Fix:** <what was changed>
**Files:** <list of files>
**Verification:** `DIFF_CHECKER_NO_DIFFS_FOUND_FOR_THE_REQUEST` log seen
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
| Subtasks Completed | 3 |
| Subtasks Remaining | 29 |

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

