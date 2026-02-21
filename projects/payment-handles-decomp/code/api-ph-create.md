# Monolith: payment_handle_create Code Flow

Route: `POST /payment_handle` → `PaymentLinkController@createPaymentHandle`

## Route Definition

```
app/Http/Route.php
  'payment_handle_create' => ['post', 'payment_handle', 'PaymentLinkController@createPaymentHandle']
```

## Controller → Service

```
app/Http/Controllers/PaymentLinkController.php
  └─ createPaymentHandle()
      └─ (new PaymentLink\Service)->createPaymentHandleNCA($merchantId)  ← NEW (calls NCA)
```

**Before decomp:** directly called `createPaymentHandle($merchantId)` → Core → DB.
**After decomp:** calls `createPaymentHandleNCA($merchantId)` → NoCodeAppsService → NCA HTTP.

## createPaymentHandleNCA (Service.php)

```
app/Models/PaymentLink/Service.php
  └─ createPaymentHandleNCA(string $merchantId)
      ├─ getPrevAuthAndSetVariables($merchantId)   // set up live mode + merchant auth
      ├─ (new NoCodeAppsService($app))->createPaymentHandle()
      │   └─ POST {NCA_BASE_URL}/v1/payment_handle  (with merchant auth headers)
      │       └─ NCA: DualWriteHandlerForHandleWrites.Handle(...)
      │           ├─ monolith_only → proxy back to monolith createPaymentHandle
      │           └─ dual_write → proxy + NCA DB write (entity saved with reused ID)
      └─ restore prev auth
```

## Original Flow (still used by NCA's monolith_only proxy)

```
app/Models/PaymentLink/Core.php
  └─ createPaymentHandle(string $merchantId)
      ├─ validatePaymentHandlePrecreateAndMode($merchant)
      │   ├─ Check mode == live
      │   └─ Check no existing handle for merchant
      ├─ createPaymentHandleV2()
      │   ├─ Create PaymentPage entity with view_type = payment_handle
      │   ├─ Store slug in merchant settings (default_payment_handle)
      │   └─ Store handlePageId in settings (default_payment_handle_page_id)
      └─ Return {id, slug, url, title, ...}
```

## Merchant Activation Flow

`createPaymentHandleNCA` is called from:
- `app/Models/Merchant/Activate.php` (line ~232): first activation
- `app/Models/Merchant/Activate.php` (line ~401): retry activation

Both were previously calling `createPaymentHandle` directly and now route through NCA.
