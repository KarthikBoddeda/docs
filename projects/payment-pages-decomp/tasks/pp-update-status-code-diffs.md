# Task: Fix payment_page_update Status Code Diffs

**Status:** ⬜ Not Started  
**Priority:** P1  
**API:** `payment_page_update` (`PATCH /payment_pages/{id}`)

---

## Problem Statement

The `payment_page_update` API is currently in **dual-write state**. During dual-write, both monolith and NCA execute the same request, and their responses are compared. This task addresses **status code diffs** - cases where monolith and NCA return different HTTP status codes.

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
3. **Failure logs are accessible** at `/pythonscripts/decomp-scripts/failure_logs/pp_update/`

> **⚠️ STOP:** If you don't have the **NCA commit**, **ABORT** and ask the user. API and Gimli have defaults (see Devstack Configuration section).

---

## How-To References

| Action | Reference |
|--------|-----------|
| Deploy to devstack | [/docs/agent-actions/deploy-to-devstack.md](/docs/agent-actions/deploy-to-devstack.md) |
| Hot reload (test code changes) | [/docs/agent-actions/hot-reload-devspace.md](/docs/agent-actions/hot-reload-devspace.md) |
| Sample API requests | [/docs/projects/payment-pages-decomp/payment-pages-api.http](/docs/projects/payment-pages-decomp/payment-pages-api.http) |
| Failure logs location | `/pythonscripts/decomp-scripts/failure_logs/pp_update/` |
| Analysis report | `/pythonscripts/decomp-scripts/failure_logs/pp_update/analysis.md` |
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
| `payment_page_update` | `"PAYMENT_PAGE_UPDATE_REQUEST" AND "<razorpay_request_id>"` | `no-code-apps` |
| `payment_page_create` | `"PAYMENT_PAGE_CREATE_REQUEST" AND "<razorpay_request_id>"` | `no-code-apps` |
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
| 🟠 | Pending investigation / blocked |
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

| # | Diff Type | Count | M | N | Deployed | ReqFound | Reproduced | CodeEvidence | HotReload | TC1 | TC2 | TC3 | TC4 | DiffCheck | Status | Commit | Review | Notes |
|---|-----------|-------|---|---|----------|----------|------------|--------------|-----------|-----|-----|-----|-----|-----------|--------|--------|--------|-------|
| 1 | `ends_by field is required when display_days_left` | 4,370 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 2 | `description contains invalid characters` | 3,288 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 3 | `type cannot be blank` | 1,391 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | GoalTracker type validation |
| 4 | `item count mismatch` (dual write) | 967 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 5 | `invalid payment_page_item.settings` | 521 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 6 | `payment_success_message invalid chars` | 520 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 7 | `min_purchase null or valid integer` | 263 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 8 | `title contains invalid characters` | 144 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 9 | `notes is not an array` | 131 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 10 | `terms contains invalid characters` | 114 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 11 | `udf_schema more than 15 items` | 110 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 12 | `slug already exists` | 86 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 13 | `length no more than 16` | 66 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Unknown field |
| 14 | `support_contact length 8-255` | 48 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 15 | `original must be a valid URL` | 46 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 16 | `Mandatory field Expires By` | 21 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 17 | `max_amount exceeds maximum` | 20 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 18 | `terms length 5-2048` | 17 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 19 | `AvailableUnits required for supporter-based` | 17 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 20 | `READ ONLY transaction` (DB error) | 13 | 200 | 400 | ⬜ | ⬜ | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | ⬜ | | | DB transient error |
| 21 | `length no more than 20` | 12 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | button_label/text |
| 22 | `amount minimum 50 for USD` | 9 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 23 | `EndsBy must be in the future` | 8 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 24 | `min_amount minimum 50 for USD` | 8 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 25 | `value length no more than 10000` | 8 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 26 | `max_amount valid integer 0-4294967295` | 8 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 27 | `min_amount exceeds maximum` | 5 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 28 | `must be a valid URL` | 4 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 29 | `item missing in pp_item response` (dual write) | 4 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 30 | `trouble completing your request` (500) | 4 | 500 | 200 | ⬜ | ⬜ | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | ⬜ | | | Monolith 500 - transient |
| 31 | `failed to unmarshal monolith response` (dual write) | 3 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 32 | `length between 4 and 30` (slug) | 3 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 33 | `stock cannot be lesser than quantity sold` (NCA) | 2 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 34 | `support_contact length 8-255` (v2) | 2 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | Same as #14 |
| 35 | `Duplicate entry` (DB error) | 1 | 200 | 400 | ⬜ | ⬜ | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | ⬜ | | | DB transient error |
| 36 | `expire_by atleast 900 seconds` | 1 | 200 | 400 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 37 | `stock cannot be lesser than quantity sold` (Monolith) | 1 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |
| 38 | `goal_end_timestamp 30 minutes after current` | 1 | 400 | 200 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | | | |

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
   ls /Users/boddedakarthik.s/rzp/pythonscripts/decomp-scripts/failure_logs/pp_update/categorized/
   
   # Read a recent log file and extract razorpay_request_id
   head -5 "<categorized_folder>/<recent_date>.csv"
   # Look for: "razorpay_request_id":"<uuid>"
   ```

2. **Get ACTUAL request body from Coralogix (MCP):**
   
   > **🔴 IMPORTANT: Don't guess the request - fetch the actual one!**
   
   Use `mcp_razorpay-cora-mcp-server_search_logs` with:
   - `search_string`: `"PAYMENT_PAGE_UPDATE_REQUEST" AND "<razorpay_request_id>"`
   - `applicationName`: `no-code-apps`
   - **For recent logs:** `relative_hours`: `48`
   - **For older logs:** Use `start_time` + `end_time` (RFC3339 format)
   
   **Example queries:**
   ```
   # Recent logs (last 48 hours)
   search_string: "PAYMENT_PAGE_UPDATE_REQUEST" AND "fc3302ff-a3d0-4116-ab54-d069daffab65"
   relative_hours: 48
   
   # Historical logs (specific date)
   search_string: "PAYMENT_PAGE_UPDATE_REQUEST" AND "fc3302ff-a3d0-4116-ab54-d069daffab65"
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
   > - Use `payment_page_update` request as base template
   > - All headers, auth, and variables are already configured!
   > - Just modify the request body to trigger the specific diff

   > **⚠️ CRITICAL:** 
   > - Use test merchant ID `LJ3P0FyFtOULha` - NOT production IDs from logs!
   > - Use `X-Proxy-State: dual_write_shadow_read_no_external` to enable comparison!
   > - DON'T `kubectl exec` into pods - hit URL directly!
   > - **You need a valid payment page ID** - create one first if needed!

   **If using curl directly (not recommended):**
   ```bash
   curl --location --request PATCH 'https://nca.dev.razorpay.in/v1/payment_pages/<payment_page_id>' \
     --header 'X-Razorpay-Merchant-Id: LJ3P0FyFtOULha' \
     --header 'X-Razorpay-Mode: live' \
     --header 'X-Proxy-State: dual_write_shadow_read_no_external' \
     --header 'rzpctx-dev-serve-user: <devstack-label>' \
     --header 'Content-Type: application/json' \
     --header 'Authorization: Basic UkFORE9NX05DQV9VU0VSOlJBTkRPTV9OQ0FfUEFTU1dPUkQ=' \
     --data-raw '<request_body_with_diff_trigger>'
   ```

   **Modify the body** to include the field that triggers the diff

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
   > - Use `payment_page_update` request as base
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

*(Empty - work not started)*

---

### Investigation Notes

*(Empty - start fresh)*

---

## Devstack Configuration

| Service | Commit | Label | Notes |
|---------|--------|-------|-------|
| NCA | `<ask user>` | `pp-decomp-<label>` | **User input required** - always ask for latest |
| API | `d54e3b9afaf981785390805c70dde2b48761ae5c` | `pp-decomp-<label>` | Default (use unless specified) |
| Gimli | `4bf1861181c41e61b7994bbc5658012b430a4530` | `pp-decomp-<label>` | Default (use unless specified) |

> **⚠️ NCA commit is mandatory user input.** API and Gimli commits above are defaults - use them unless user specifies otherwise.

---

## Statistics

| Metric | Value |
|--------|-------|
| **Total Logs** | 13,034 |
| Monolith 200, NCA 400/500 | 7,738 (59.4%) |
| Monolith 400/500, NCA 200 | 4,499 (34.5%) |
| Timeouts | 789 (6.1%) |
| **Subtasks Total** | 38 |

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
6. **NEVER assume a fix from create API works for update API** - always verify each API independently
