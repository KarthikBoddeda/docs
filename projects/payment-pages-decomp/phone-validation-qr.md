# Phone Validation Failure on Payment Page QR Payments

**Date:** 2026-04-21
**Issue Thread:** https://razorpay.slack.com/archives/C7WEGELHJ/p1776754281213499
**DevRev:** ISS-2045161
**Status:** Under Investigation

---

## Problem Statement

Multiple merchants (~7-8) report that payments on payment pages are succeeding initially but then getting refunded. The root cause is a phone number validation failure during QR payment callback processing.

---

## Affected Payment (Primary Example)

| Field | Value |
|-------|-------|
| Payment ID | `Se5xW3CXazWEHN` |
| Merchant ID | `EfxlXB6w5kNjhZ` |
| Amount | 99,900 (₹999) |
| Method | UPI |
| Status | Refunded |
| QR Code ID | `SdjyZBhflcRWd5` |
| Payment Page | `pages.razorpay.com/gumastamaharashtra` |
| VPA | `dineshgupta612-1@okicici` |
| Gateway | `upi_yesbank` |

### Payment Notes (from payment entity data provided by PSE)

```json
{"uid":"GEC-7125","email":"spazespri@gmail.com","phone":"+91+917777059120"}
```

> **Note on `+91+917777059120`:** This value was taken directly from the payment entity's `notes` column in the payment details provided by PSE. We have not independently verified from the datalake whether the stored value is literally `+91+917777059120` (double prefix) or was a display artifact. The core issue is the same regardless — any phone value containing `+` fails the `type: number` JSON Schema validation.

---

## Evidence from `qr_payment_request` Datalake Table

**Query:**
```sql
select * from realtime_hudi_api.qr_payment_request
where qr_code_id='SdjyZBhflcRWd5' and created_date>='2020-01-01'
```

### Row 1 — First callback (2026-04-15): PAYMENT CREATION FAILED

| Field | Value |
|-------|-------|
| id | `SdjyxKyxs27Zqa` |
| created_at | 1776250022 (2026-04-15) |
| qr_code_id | `SdjyZBhflcRWd5` |
| **is_created** | **0** (payment NOT created) |
| **expected** | **1** (payment WAS expected) |
| transaction_reference | `647193641792` |
| **failure_reason** | **`The phone field is invalid. String value found, but a number is required`** |
| request_source | `{"source":"callback","request_from":"bank"}` |
| request_payload | `{"success":true,"external_trace_id":"baaa6227-8984-49ba-b8a1-69805e121dc8","data":{"version":"v2","payment":{"currency":"INR","amount_authorized":99900,"payer_account_type":"bank_account"},"status":"payment_successful","upi":{"gateway_status_code":"00","status_code":"00","npci_reference_id":"647193641792","merchant_reference":"RZPYSdjyZBhflcRWd5qrv2","account_number":"XXXXXX7697",...,"vpa":"dineshgupta612-1@okicici"},"terminal":{"vpa":"rzpyzcgoodwilleservices@yesbank","gateway":"upi_yesbank"}},"error":null,...}` |

### Row 2 — Second callback (2026-04-16): Created but QR already closed

| Field | Value |
|-------|-------|
| id | `Se5xVrOCK0PAHv` |
| created_at | 1776327415 (2026-04-16) |
| qr_code_id | `SdjyZBhflcRWd5` |
| **is_created** | **1** (payment created) |
| **expected** | **0** (payment NOT expected — QR already closed) |
| transaction_reference | `647193641792` (same txn as row 1) |
| failure_reason | (empty) |
| request_source | `{"source":"file","request_from":"bank"}` |

### Refund Reason (from Coralogix)

```json
"refund_reason": "The checkout order associated to the QR is closed"
```

---

## Production Error Log

**Source:** Coralogix, 2026-04-15T10:47:02Z

```json
{
  "channel": "Razorpay API",
  "cluster": "cde-blue-eks",
  "level": 400,
  "level_name": "ERROR",
  "message": "QR_PAYMENT_PROCESSING_FAILED",
  "datetime": "2026-04-15T10:47:02.825886+00:00",
  "context_str_code": "BAD_REQUEST_VALIDATION_FAILURE",
  "context_str_message": "The phone field is invalid. String value found",
  "extra": {
    "code": "QR_PAYMENT_PROCESSING_FAILED",
    "environment": "production",
    "request": {
      "merchant_id": "EfxlXB6w5kNjhZ",
      "method": "POST",
      "route_name": "gateway_payment_callback_post",
      "task_id": "baaa6227-8984-49ba-b8a1-69805e121dc8",
      "url": "https://api.razorpay.com/v1/callback/upi_yesbank"
    }
  }
}
```

### Full Stack Trace

```
#0  UdfSchema->validate(Array)
      at app/Models/PaymentLink/Template/UdfSchema.php
#1  PaymentLink\Core->validateIsPaymentInitiatable(PaymentLink, Payment)
      at app/Models/PaymentLink/Core.php(1167)
#2  Payment\Processor->validateAndSetPaymentLinkIfApplicable(Payment, Array)
      at app/Models/Payment/Processor/Processor.php(13428)
#3  Payment\Processor->createPaymentEntity(Array, Payment)
      at app/Models/Payment/Processor/Processor.php(12544)
#4  Payment\Processor->process(Array, Array)
      at app/Models/Payment/Processor/Processor.php(6249)
      ↓ (transaction wrapper)
#8  QrPayment\Processor->createPayment(Array, Array)
      at app/Models/QrPayment/Processor.php(465)
#9  QrPayment\Processor->processPaymentAfterRemovingNestedTransactionBlock(...)
      at app/Models/QrPayment/Processor.php(1402)
      ↓ (mutex)
#14 QrPayment\Processor->processPayment(QrPayment)
      at app/Models/QrPayment/Processor.php(219)
#15 QrPayment\Processor->process(QrPayment)
      at app/Models/QrPayment/Processor.php(110)
#16 QrPayment\Core->processPayment(...)
      at app/Models/QrPayment/Core.php(56)
      ↓ (mutex)
#20 BharatQr\Service->processQrCodePayment(Array, Terminal, QrPaymentRequest)
      at app/Models/BharatQr/Service.php(174)
#21 BharatQr\Service->processPayment(Array, 'upi_yesbank')
      at app/Models/BharatQr/Service.php(137)
#22 QrGatewayModule->processExistingGatewayCallbackThroughOldFlow(Array, 'SdjyZBhflcRWd5', 'upi_yesbank')
      at app/Models/QrGatewayModule/QrGatewayModule.php(240)
#23 QrGatewayModule->checkForQrPaymentProcessing(Array, 'upi_yesbank', 'SdjyZBhflcRWd5qrv2')
      at app/Models/QrGatewayModule/QrGatewayModule.php(90)
#24 GatewayController->processServerCallbackWithGatewayResponse(Array, 'upi_yesbank')
      at app/Http/Controllers/GatewayController.php(469)
#25 GatewayController->callbackGateway('upi_yesbank')
      at app/Http/Controllers/GatewayController.php(1068)
```

### Call Chain Summary

```
Bank UPI callback
  → GatewayController::callbackGateway('upi_yesbank')
    → QrGatewayModule::checkForQrPaymentProcessing()
      → BharatQr\Service::processPayment()
        → QrPayment\Core::processPayment()
          → QrPayment\Processor::process()
            → QrPayment\Processor::processPayment()
              → QrPayment\Processor::createPayment()
                → Payment\Processor::process()
                  → Payment\Processor::createPaymentEntity()
                    → Payment\Processor::validateAndSetPaymentLinkIfApplicable()
                      → PaymentLink\Core::validateIsPaymentInitiatable()
                        → UdfSchema::validate()  ← THROWS HERE
```

---

## How Payment Notes Flow Through the System

### Step 1: Order Creation (payment page frontend → monolith)

Frontend sends `POST /v1/payment_pages/{id}/order`:
```json
{"line_items":[...],"notes":{"email":"...","phone":"+91917013605095"}}
```

**File:** `api/app/Models/PaymentLink/Core.php:1523-1558` (createOrder)

Notes are stored on the Order entity **without UDF schema validation**:
```php
$orderReq = [
    Order\Entity::NOTES => $input[Order\Entity::NOTES] ?? [],  // passed as-is
    // ...
];
```

### Step 2: Checkout Opens → Checkout Order Created

Checkout SDK creates a `checkout_order` entity that stores:
- `contact`: customer phone from `prefill.contact`
- `notes`: from checkout options (same UDF notes from order creation)
- `payment_link_id`: the payment page ID

**File:** `api/app/Models/Checkout/Order/Entity.php:124-139`

`CREATE_PAYMENT_ATTRIBUTES` includes both `NOTES` and `PAYMENT_LINK_ID`.

### Step 3: QR Created from Checkout Order

The QR code is associated with the checkout order.

### Step 4: Bank QR Callback → Payment Creation

**File:** `api/app/Models/QrPayment/Processor.php:509-627` (getPaymentArray)

```php
// Line 518: Initial notes from QR code
$paymentArray = [
    Payment\Entity::NOTES => $this->qrCode->getNotes()->toArray(),
    // ...
];

// Line 608-612: MERGED with checkout order's payment attributes
if ($this->checkoutOrder !== null && $qrPayment->isExpected()) {
    $paymentArrayFromCheckoutOrder =
        (new CheckoutOrder\Core())->getPaymentArrayFromCheckoutOrder($this->checkoutOrder);
    $paymentArray = array_merge($paymentArray, $paymentArrayFromCheckoutOrder);
    // ↑ This OVERRIDES notes with checkout order's notes (which contain phone with +91)
    // ↑ This also adds payment_link_id (which triggers UDF validation)
}
```

**This is the critical merge.** The checkout order's attributes include:
- `notes` → `{"phone": "+91917013605095"}` (the UDF values with `+91` prefix)
- `payment_link_id` → triggers `validateIsPaymentInitiatable()` in Payment Processor

### Step 5: Payment Processor Validates Notes Against UDF Schema

**File:** `api/app/Models/Payment/Processor/Processor.php:13420-13431`

```php
protected function validateAndSetPaymentLinkIfApplicable(Payment\Entity $payment, array $input)
{
    if (isset($input[Payment\Entity::PAYMENT_LINK_ID]) === false) {
        return;  // only runs if payment_link_id is present
    }
    $paymentLinkId = $input[Payment\Entity::PAYMENT_LINK_ID];
    $paymentLink = $this->repo->payment_link->findByPublicIdAndMerchant($paymentLinkId, $this->merchant);
    (new PaymentLink\Core)->validateIsPaymentInitiatable($paymentLink, $payment);
    // ↑ This calls UdfSchema::validate() which fails on phone with +91
}
```

### Step 6: UDF Schema Validation Fails

**File:** `api/app/Models/PaymentLink/Template/UdfSchema.php:120-148`

```php
$validator->validate(
    $data,                                          // notes: {"phone": "+91917013605095"}
    $this->getSchemaInRfcFormatForValidation(),     // schema: phone type=number
    JsonSchemaConstraint::CHECK_MODE_COERCE_TYPES   // tries to coerce string→number
);
// "+91917013605095" contains '+' → cannot coerce to number → FAILS
// Error: "String value found, but a number is required"
// Formatted: "The phone field is invalid. String value found, but a number is required"
```

---

## Root Cause Details

### UDF Phone Schema Definition (V1 pages)

**File:** `api/app/Models/PaymentLink/ViewSerializer.php:432-443`

```php
[
    'title'     => 'Phone',
    'name'      => 'phone',
    'type'      => 'number',     // ← JSON Schema type: expects numeric
    'pattern'   => 'phone',      // ← maps to regex: ^([0-9]){8,}$
    'required'  => true,
    'minLength' => '8',
]
```

> Note: For V2 pages (`getVersion() === Version::V2`), the default UDFs are NOT prepended (line 416-419). V2 pages use merchant-defined UDF schemas which may also have the phone field as `type: number`.

### Phone Pattern Regex

**File:** `api/app/Models/PaymentLink/Template/UdfSchema.php:18-28`

```php
const PATTERN_NAME_TO_REGEX_MAP = [
    Pattern::PHONE  => '^([0-9]){8,}$',     // digits only, 8+, NO + sign allowed
    Pattern::NUMBER => '^[+-]?([0-9]*[.])?[0-9]+$',  // allows +/- (but this is for NUMBER pattern, not PHONE)
];
```

### The Two-Bug Combo

1. **Bug 1 (frontend):** The phone value sent in notes contains `+91` prefix. The exact code path that adds `+91` to the UDF phone value is not yet identified — the stores `ContactTextInput` has it as visual-only prefix, but the actual order creation request contains it.

2. **Bug 2 (backend):** The UDF schema defines phone as `type: number`. Even a clean phone like `+919876543210` fails because `+` can't be coerced to a number. This validation runs during payment creation (QR callback), NOT during order creation — so the error surfaces asynchronously after the customer has already left.

---

## Where `+91` Comes From — ROOT CAUSE FOUND

### The Change: `PhoneInput.svelte` by Aakash Raina (March 2026)

Three commits introduced and re-added a new `PhoneInput` component for international dial code support:

| Commit | Date | Description |
|--------|------|-------------|
| `47c8143b5` | Mar 5, 2026 | **feat: add dial code support to payment pages phone input (#3404)** |
| `2f9931c22` | Mar ~8 | **Revert** the above (#3406) |
| `e7c1c7b72` | Mar 12, 2026 | **fix(Payment Pages): re-add dial code support with PhoneInput component (#3407)** — currently live |
| `caef2f4b6` | Apr 9, 2026 | **fix(PhoneInput): handle change event to capture browser autofill values (#3435)** |

**Author:** Aakash Raina (`aakashraina9@gmail.com`)

### The Code

**File:** `static/svelte2/src/hosted/wysiwyg/ui-components/PhoneInput.svelte`

The component has:
1. A **country dial code dropdown** (select) — defaults to `+91` for Indian merchants
2. A **visible text input** — where customer types their local number (no `name` attribute, NOT serialized)
3. A **hidden input** — carries `combinedValue` as the submitted field value

```svelte
<!-- Hidden input: carries dialCode + localNumber as the submitted field value -->
<input type="hidden" name={field.name} value={combinedValue} />
```

The `combinedValue` is computed as:

```js
combinedValue: ({ selectedDialCode, prettyVal }) =>
  prettyVal.trim() ? `${selectedDialCode}${prettyVal}` : '',
```

**This always prepends the dial code (e.g. `+91`) to whatever the user typed.**

### How the Double-Prefix Bug Happens

The `onInput` handler tries to detect and strip dial codes when the user types `+`:

```js
onInput(e) {
  let val = e.target.value;
  if (val && val.startsWith('+')) {
    try {
      const parsed = parsePhoneNumber(val);
      if (parsed.dialCode && parsed.phoneNumber) {
        // Update dropdown and strip dial code from input
        val = parsed.phoneNumber;
        e.target.value = val;
      }
    } catch (_) {
      // parsePhoneNumber couldn't parse it — leave val as-is
    }
  }
  this.set({ prettyVal: val });
}
```

| Customer types | `parsePhoneNumber` result | `prettyVal` | `selectedDialCode` | `combinedValue` (submitted) |
|----------------|--------------------------|-------------|--------------------|-----------------------------|
| `7777059120` (10 digits) | N/A (no `+`) | `7777059120` | `+91` | `+917777059120` ✓ |
| `917777059120` (12 digits) | N/A (no `+`) | `917777059120` | `+91` | **`+91917777059120`** (22 chars, invalid) |
| `+917777059120` | Parsed → dialCode:`+91`, phone:`7777059120` | `7777059120` | `+91` (updated) | `+917777059120` ✓ |
| `+917777059120` (parse fails) | Exception caught | `+917777059120` (as-is) | `+91` | **`+91+917777059120`** (double prefix!) |

**The `+91+917777059120` case:** Customer types or pastes `+917777059120`. If `parsePhoneNumber()` fails (e.g. due to partial input, or i18nify can't parse it), the catch block leaves `prettyVal = "+917777059120"` and `combinedValue = "+91" + "+917777059120"` = `+91+917777059120`.

**The `+91917777059120` case:** Customer types `917777059120` (12 digits, starting with country code but without `+`). Since it doesn't start with `+`, the `onInput` handler skips the parsing entirely. `prettyVal = "917777059120"` and `combinedValue = "+91" + "917777059120"` = `+91917777059120`.

### How This Is Wired In

**File:** `static/svelte2/src/hosted/wysiwyg/ui-components/Form.svelte`

The `PhoneInput` component is used for any UDF field with `pattern === 'phone'`:

```js
// In getComponent()
if (field.pattern === 'phone') {
  return PhoneInput;
}
```

So ALL payment pages with a phone UDF field now go through this component, which always prepends the dial code to the submitted value.

### Timeline

- **Mar 5:** Feature added (`#3404`)
- **Mar ~8:** Reverted (`#3406`) — likely due to issues found
- **Mar 12:** Re-added with fixes (`#3407`) — **currently live on production**
- **Apr 9:** Autofill fix (`#3435`)
- **Apr 15:** First reported failure (this payment)
- **Apr 21:** PSE ticket raised (7-8 merchants)

---

## Recent Code Changes Audit

**FOUND: `static` repo change by Aakash Raina on Mar 12, 2026 is the root cause.**

| Area | Repo | Recent Changes | Impact |
|------|------|---------------|--------|
| **`PhoneInput.svelte`** | **static** | **`e7c1c7b72` (Mar 12) — dial code support (#3407)** | **ROOT CAUSE: prepends `+91` to phone in notes** |
| **`PhoneInput.svelte`** | **static** | **`caef2f4b6` (Apr 9) — autofill fix (#3435)** | **Fixed autofill but dial code prepend still occurs** |
| `UdfSchema.php` | api | No changes | None |
| `Core.php:validateIsPaymentInitiatable` | api | No changes | None |
| `Payment/Processor/Processor.php` | api | Unrelated (UPI autopay, DFB, etc.) | None |
| `QrPayment/Processor.php` | api | SQR payment tags — in_person SQR only | None |
| `checkout/contact-prefill.ts` | checkout | No changes | None |
| `qr-codes` service | qr-codes | Thumbs logo, splitz refactors only | None |

**Conclusion:** The `PhoneInput.svelte` component introduced on Mar 12, 2026 always prepends the dial code (`+91`) to the phone value submitted in notes. This breaks the backend UDF schema validation (`type: number`) during QR payment callback processing. The ~1 month gap between deploy (Mar 12) and PSE ticket (Apr 21) is consistent with gradual discovery by affected merchants.

---

## Potential Fixes

### Fix 1 (Frontend — addresses root cause): Submit only local number in notes

**File:** `static/svelte2/src/hosted/wysiwyg/ui-components/PhoneInput.svelte`

The `combinedValue` computed property should NOT prepend the dial code for the value stored in notes, since the backend UDF schema expects a plain number. Options:

**Option A:** Submit only the local number (no dial code):
```js
// Before
combinedValue: ({ selectedDialCode, prettyVal }) =>
  prettyVal.trim() ? `${selectedDialCode}${prettyVal}` : '',

// After — only submit local number
combinedValue: ({ prettyVal }) => prettyVal.trim() || '',
```

**Option B:** Strip any leading country code before combining:
```js
combinedValue: ({ selectedDialCode, prettyVal }) => {
  if (!prettyVal.trim()) return '';
  let local = prettyVal.replace(/[^\d]/g, '');  // digits only
  if (local.length === 12 && local.startsWith('91')) {
    local = local.slice(2);
  }
  return local;
},
```

### Fix 2 (Backend — defense in depth): Change UDF phone type to `string`

**File:** `api/app/Models/PaymentLink/ViewSerializer.php:435`

```php
// Before
'type' => 'number',

// After
'type' => 'string',
```

The `pattern: phone` regex (`^([0-9]){8,}$`) already validates the format. The `type` should be `string` since phone numbers are not numeric values. This prevents the JSON Schema type coercion failure.

### Fix 3 (Backend — fail early): Validate notes at order creation

**File:** `api/app/Models/PaymentLink/Core.php:1523`

Add `$udfSchema->validate($input[Order\Entity::NOTES])` during `createOrder()` so invalid phone values are rejected immediately with a clear 400 error, rather than silently passing through and failing asynchronously during QR callback.

### Fix 4 (Backend — normalize): Strip country code in UDF validation

**File:** `api/app/Models/PaymentLink/Template/UdfSchema.php:120`

Before JSON Schema validation, normalize phone values:
```php
if (isset($input['phone']) && is_string($input['phone'])) {
    $phone = preg_replace('/^\+?91/', '', $input['phone']);
    if (strlen($phone) === 10 && preg_match('/^[6-9]/', $phone)) {
        $input['phone'] = $phone;
    }
}
```

---

## Not Related to NCA Decomposition

- Zero `no-code-apps` or `nocode` references in Coralogix logs for this payment
- The `dual_write` hits in logs were from `transactions/core.go` (ledger), not payment page dual write
- Order creation always goes through monolith
- QR callback and payment creation are entirely in monolith
- UDF schema validation is monolith-only code (`PaymentLink/Template/UdfSchema.php`)
