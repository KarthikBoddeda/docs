# Proxying Logic in NCA

This document explains how NCA proxies requests to monolith and handles dual writes.

---

## Overview

During migration, NCA acts as a proxy layer. Based on the **proxy state** (determined by Splitz experiment), NCA decides how to handle each request.

---

## Proxy States

Defined in `internal/modules/payment_page/constants.go`:

```go
const (
    MonolithOnlyProxyState                  = "monolith_only"
    DualWriteNoReadsNoExternalProxyState    = "dual_write_no_reads_no_external"
    DualWriteShadowReadNoExternalProxyState = "dual_write_shadow_read_no_external"
    DualWriteReadNoExternalProxyState       = "dual_write_read_no_external"
    DualWriteReadExternalProxyState         = "dual_write_read_external"
    NCASOnlyProxyState                      = "nca_only"

    DefaultFallbackProxyState = MonolithOnlyProxyState
)
```

### State Descriptions

| State | Description |
|-------|-------------|
| `monolith_only` | Just proxy to monolith, NCA does nothing |
| `dual_write_no_reads_no_external` | Execute both, compare responses, return monolith response. Skip external entity creation in NCA (use IDs from monolith) |
| `dual_write_shadow_read_no_external` | Same as above + enable shadowing on read APIs |
| `dual_write_read_no_external` | Writes: dual write. Reads: NCA only |
| `dual_write_read_external` | NCA is primary, dual write to monolith. External calls from NCA |
| `nca_only` | NCA handles everything, no monolith involvement |

---

## How Proxy State is Determined

**File:** `internal/modules/payment_page/core.go`

**Function:** `GetProxyStateFromSplitzAndSetToRequestContext()`

Flow:
1. Check if proxy state is set in request headers (for testing)
2. If not, call Splitz experiment to get state
3. Set state in request context
4. Return state

```
Request Headers → Check for override → Splitz Experiment → Set in Context
```

---

## Dual Write Handler

**File:** `internal/monolith_decomp/dual_write_handlers/base.go`

### GenericDualWriteHandler.Handle()

This is the main handler for write APIs.

**Entry:** Get proxy state from context

**Behavior by state:**
- `monolith_only` → Proxy to monolith, return monolith response
- `dual_write_*` → Proxy to monolith → Execute NCA → Compare responses → Return monolith response
- `nca_only` → Execute NCA only, return NCA response

### Key Functions

| Function | File | Purpose |
|----------|------|---------|
| `Handle()` | `dual_write_handlers/base.go` | Main entry, routes based on state |
| `proxyRequestToMonolith()` | `dual_write_handlers/base.go` | Sends request to monolith |
| `handleDiffCalculation()` | `dual_write_handlers/base.go` | Compares responses, logs diffs |
| `executeNCAOperationWithPanicRecovery()` | `dual_write_handlers/base.go` | Executes NCA logic safely |

---

## Diff Calculation

**File:** `internal/monolith_decomp/diffs/diff_checker.go`

**Function:** `HandleComparisonAndSendMetrics()`

What it does:
1. Compare status codes
2. If status codes differ → log `status_code_mismatch`
3. If status codes match → compare response bodies
4. Log diffs with paths
5. Push metrics

### Status Code Diff Log

When status codes differ, you'll see logs like:
```
status_code_mismatch: monolith error: <msg>, nca error: <msg>
```

### Response Body Diff

Configured per route in `diffs/configs.go`. Some paths are ignored (e.g., timestamps, IDs that are expected to differ).

---

## Proxy Request to Monolith

**File:** `pkg/clients/api/impl.go`

**Function:** `SendProxyRequestToApi()`

What it does:
1. Build URL with monolith base URL
2. Add query params
3. Set auth headers
4. Send request
5. Handle response (JSON or HTML)

```go
func (service ApiService) SendProxyRequestToApi(
    ctx context.Context,
    input interface{},
    merchantId, mode, method, url string,
    queryParams map[string][]string,
    requestHeaders map[string]string,
    skipAuth bool,
) (*proxy.ProxyResponse, rzperror.IError)
```

---

## Handler Types

Different handlers for different API patterns:

| Handler | Used For | File |
|---------|----------|------|
| `GenericDualWriteHandler` | Standard write APIs | `base.go` |
| `GenericDualReadHandler` | Standard read APIs | `base.go` |
| `GenericExternalEntityHandler` | APIs with external entity dependencies | `base.go` |

---

## Testing Proxy State

For testing, you can override proxy state via header:
```
rzpctx-proxy-state: dual_write_no_reads_no_external
```

This is useful for testing specific states on devstack.

---

## Related Files

| File | Purpose |
|------|---------|
| `internal/modules/payment_page/constants.go` | Proxy state definitions |
| `internal/modules/payment_page/core.go` | `GetProxyState*` functions |
| `internal/monolith_decomp/dual_write_handlers/base.go` | Handler implementations |
| `internal/monolith_decomp/diffs/diff_checker.go` | Diff calculation |
| `internal/monolith_decomp/diffs/configs.go` | Per-route diff configs |
| `pkg/clients/api/impl.go` | Monolith proxy client |

