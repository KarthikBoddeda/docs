# NCA: payment_handle_create Code Flow

Entry point: `POST /v1/payment_handle`

## Route & Controller

```
internal/router/payment_handle_routes.go
  └─ PaymentHandleRoutes.GetRouteConfigs()
      └─ {PaymentHandleCreateRouteName, POST, "", controllers.PaymentHandleCtrl.Create}
```

## Controller

```
internal/controllers/payment_handle.go
  └─ PaymentHandleController.Create(req)
      └─ handleDualWriteHandler.Handle(req, controller.ncaCreate)
```

The `handleDualWriteHandler` is a `DualWriteHandlerForHandleWrites` (in `internal/monolith_decomp/dual_write_handlers/payment_handle_write_handler.go`).

## Dual Write Handler

`Handle(req, ncaOperation)` (from `GenericDualWriteHandler`):

1. Call `HandleWriteProxyStateGetter.GetProxyState(req)`
   - Calls `core.GetPaymentHandleProxyStateFromSplitzAndSetToRequestContext(req)`
   - Hits `payment_handle_proxy_state` splitz experiment
   - Returns one of: `monolith_only`, `dual_write_no_reads_no_external`, ...

2. Based on proxy state:
   - `monolith_only`: proxy to monolith, return response (NCA op NOT called)
   - `dual_write_no_reads_no_external`: proxy to monolith → call ncaCreate → return monolith response
   - `nca_only`: call ncaCreate → return NCA response

## Monolith Proxy

`ProxyPaymentPageRequestToMonolith(req)` → forwards to monolith `POST /v1/payment_handle`.

Monolith runs `createPaymentHandle` / `createPaymentHandleV2` and returns the handle entity.

## NCA Operation (ncaCreate)

Only called in dual-write or nca_only states:

```
PaymentHandleController.ncaCreate(req, monolithResp)
  └─ handleCore.CreatePaymentHandle(ctx, proxyResp)
      ├─ parseHandleMonolithResponse(ctx, body)
      │   └─ Extract id (strip pl_), title, slug, short_url, status
      ├─ entity := GetEmptyEntity()
      ├─ entity.SetId(strippedId)        // reuses monolith ID
      ├─ entity.SetMerchantId(ctx)
      ├─ entity.SetMode(ctx)
      ├─ entity.SetTitle(title)
      ├─ entity.SetType("payment_handle")
      ├─ entity.SetShortUrl(shortUrl)
      ├─ entity.SetStatus(status)
      └─ repo.Create(ctx, &entity)       // INSERT into payment_handles table
```

## Diff Calculation

After both monolith and NCA operations complete, the handler logs the diff between responses.
Configure diff settings in `internal/monolith_decomp/diffs/configs.go`.

## Error Handling

- If NCA create fails: error is logged (`PH_DUAL_WRITE_CREATE_FAILED`), monolith response returned
- If proxy state fetch fails: falls back to `monolith_only`
- If monolith response extraction fails: NCA write is skipped, monolith response returned

## Validation Notes

Payment handle create validation in the monolith:
- Only one handle per merchant (enforced by `default_payment_handle` setting check)
- Merchant must be activated
- Mode must be `live`

In NCA dual-write phase, validation is NOT duplicated — monolith's validation result is used.
