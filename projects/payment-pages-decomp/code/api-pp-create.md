# payment_page_create - Monolith (API) Code Reference

**API:** `POST /payment_pages`  
**Route Name:** `payment_page_create`

> **Note:** Code uses `PaymentLink` naming but it's actually Payment Pages (legacy naming). See [monolith-navigation-guide.md](./monolith-navigation-guide.md).

---

## Route Definition

**File:** `app/Http/Route.php`

```php
'payment_page_create' => ['post', 'payment_pages', 'PaymentLinkController@create'],
```

---

## Monolith Code Flow

### 1. Controller Entry
**File:** `app/Http/Controllers/PaymentLinkController.php`  
**Function:** `create()`

```php
public function create()
{
    $input = Request::all();
    return $this->service()->create($input);
}
```

### 2. Service Layer
**File:** `app/Models/PaymentLink/Service.php`  
**Function:** `create()`

```php
public function create(array $input): array
{
    $entity = $this->core->create($input, $this->merchant, $this->user);
    return $entity->toArrayPublic();
}
```

### 3. Core Business Logic
**File:** `app/Models/PaymentLink/Core.php`  
**Function:** `create()`

Steps:
1. `validateBulkUploadFlow($input, $merchant)` - Check bulk upload restrictions
2. `(new Entity)->generateId()` - Create new entity with ID
3. `$paymentLink->merchant()->associate($merchant)` - Associate merchant
4. `$paymentLink->user()->associate($user)` - Associate user
5. `(new Validator())->validatePayerNameAndExpiryForCreate($merchant, $input)` - Pre-validation
6. **`$paymentLink->build($input)`** - **VALIDATION HAPPENS HERE** (implicit)
7. `$validator->validateGeneralSlug()` or `validateCDSSlug()` - Slug validation
8. `createAndSetShortUrl()` - Generate gimli short URL
9. **Transaction:**
   - `upsertSettings()` - Save settings
   - `repo->saveOrFail($paymentLink)` - Save to DB
   - `createPaymentPageItems()` - Create line items
   - `createCustomUrl()` - Custom URL entry
10. `repo->loadRelations($paymentLink)` - Load relations for response
11. Push events, metrics, etc.

---

## Validation Rules

**File:** `app/Models/PaymentLink/Validator.php`

### $createRules

```php
protected static $createRules = [
    Entity::CURRENCY        => 'filled|string|currency|custom',
    Entity::EXPIRE_BY       => 'sometimes|epoch|nullable|custom',
    Entity::TIMES_PAYABLE   => 'sometimes|mysql_unsigned_int|min:1|nullable',
    Entity::RECEIPT         => 'string|min:3|max:40|nullable',
    Entity::TITLE           => 'required|string|min:3|max:80|utf8',
    Entity::DESCRIPTION     => 'string|max:65535|nullable|utf8|custom',
    Entity::NOTES           => 'sometimes|notes',
    Entity::SLUG            => 'string',
    Entity::SUPPORT_CONTACT => 'nullable|contact_syntax',
    Entity::SUPPORT_EMAIL   => 'nullable|email',
    Entity::TERMS           => 'nullable|string|min:5|max:2048|utf8',
    Entity::SETTINGS        => 'nullable|array',
    Entity::TEMPLATE_TYPE   => 'sometimes|string|max:24',
    Entity::VIEW_TYPE       => 'sometimes|string|custom',

    // Settings nested validation
    Entity::SETTINGS . '.' . Entity::THEME                        => 'nullable|string|in:light,dark',
    Entity::SETTINGS . '.' . Entity::UDF_SCHEMA                   => 'nullable|json',
    Entity::SETTINGS . '.' . Entity::ALLOW_MULTIPLE_UNITS         => 'nullable|string|in:0,1',
    Entity::SETTINGS . '.' . Entity::ALLOW_SOCIAL_SHARE           => 'nullable|string|in:0,1',
    Entity::SETTINGS . '.' . Entity::PAYMENT_SUCCESS_REDIRECT_URL => 'nullable|url',
    Entity::SETTINGS . '.' . Entity::PAYMENT_SUCCESS_MESSAGE      => 'nullable|string|min:5|max:2048|utf8',
    Entity::SETTINGS . '.' . Entity::CHECKOUT_OPTIONS             => 'array',
    Entity::SETTINGS . '.' . Entity::PAYMENT_BUTTON_LABEL         => 'string|max:20',
    Entity::SETTINGS . '.' . Entity::GOAL_TRACKER                 => 'nullable|array',
    Entity::SETTINGS . '.' . Entity::PARTNER_WEBHOOK_SETTINGS     => 'nullable|array',

    Entity::PAYMENT_PAGE_ITEMS => 'required|sequential_array|min:1',
];
```

### Custom Validators

These are called when rule contains `custom`:

| Field | Method | What it validates |
|-------|--------|-------------------|
| `currency` | `validateCurrency()` | Currency code valid for merchant |
| `expire_by` | `validateExpireBy()` | Must be future timestamp |
| `description` | `validateDescription()` | Description format, content |
| `view_type` | `validateViewType()` | Valid view type enum |

---

## Key Differences from NCA

### TrackerType Validation

**Monolith:** `settings.goal_tracker` is validated as `nullable|array` only. No `tracker_type` required check.

**NCA:** Explicitly checks `settings.GoalTracker.TrackerType != nil` when GoalTracker exists.

**Result:** "tracker_type required" diff - NCA returns 400, Monolith returns 200.

### Validation Timing

**Monolith:** Validation via `build()` happens AFTER merchant/user association.

**NCA:** Validation in controller via `ValidateForCreate()` before core logic.

---

## Related Files

| File | Purpose |
|------|---------|
| `app/Http/Route.php` | Route definition |
| `app/Http/Controllers/PaymentLinkController.php` | Controller |
| `app/Models/PaymentLink/Service.php` | Service layer |
| `app/Models/PaymentLink/Core.php` | Business logic (create function) |
| `app/Models/PaymentLink/Validator.php` | Validation rules |
| `app/Models/PaymentLink/Entity.php` | Entity model |
| `app/Models/PaymentLink/PaymentPageItem/Core.php` | Line items logic |

---

## Debugging Tips

1. **Find validation rules:** Look at `$createRules` in Validator.php
2. **Find custom validation:** Search for `validateFieldName()` methods
3. **Trace execution:** Controller → Service → Core.php `create()` → `build()` → Validator
4. **Settings validation:** Check dot-notation rules like `settings.goal_tracker`



