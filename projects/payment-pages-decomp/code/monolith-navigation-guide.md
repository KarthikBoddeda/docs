# Guide to Navigating Monolith (API) Code

This guide explains the tricky/confusing aspects of navigating the PHP monolith codebase for Payment Pages.

---

## Key Caveat: PaymentLink vs PaymentPage

**The code uses "PaymentLink" naming but it's actually Payment Pages.**

Payment Pages was built on top of the legacy Payment Links code, so file names, class names, and DB tables use `PaymentLink` or `payment_link`:

| What you see | What it actually is |
|--------------|---------------------|
| `PaymentLinkController` | Payment Page Controller |
| `app/Models/PaymentLink/` | Payment Page model folder |
| `payment_link` table | `payment_pages` (logical) |
| `$paymentLink` variable | Payment Page entity |

---

## Code Structure Pattern

All Payment Page code follows this pattern:

```
app/Models/PaymentLink/
├── Entity.php       # Entity model, DB fields, defaults
├── Service.php      # Entry point from controller, thin layer
├── Core.php         # Business logic
├── Validator.php    # Validation rules (implicit!)
├── Repository.php   # DB queries
└── ...
```

**Request flow:**
```
Route.php → Controller → Service.php → Core.php
                              ↓
                    (implicit validation via build())
```

---

## Routes

**File:** `app/Http/Route.php`

Format: `'route_name' => ['method', 'path', 'Controller@action']`

```php
'payment_page_create' => ['post', 'payment_pages', 'PaymentLinkController@create'],
'payment_page_update' => ['patch', 'payment_pages/{id}', 'PaymentLinkController@update'],
```

---

## Controller → Service → Core

**Controller** (`app/Http/Controllers/PaymentLinkController.php`) is just a pass-through:
```php
public function create()
{
    $input = Request::all();
    return $this->service()->create($input);  // → Service
}
```

**Service** (`app/Models/PaymentLink/Service.php`) also thin:
```php
public function create(array $input): array
{
    $entity = $this->core->create($input, $this->merchant, $this->user);  // → Core
    return $entity->toArrayPublic();
}
```

**Core** (`app/Models/PaymentLink/Core.php`) has the actual logic.

---

## Implicit Validation via build()

**This is the trickiest part!**

Validation in monolith happens implicitly when you call `build()` on an entity:

```php
// In Core.php
$paymentLink = (new Entity)->generateId();
$paymentLink->build($input);  // ← Validation happens HERE
```

The `build()` method (from Razorpay\Spine\Entity) does:
1. `modify($input)` - Transform input
2. `validateInput($operation, $input)` - **Runs validation rules**
3. `generate($input)` - Generate computed fields
4. `fill($input)` - Set attributes

**Validation rules are in Validator.php** but called implicitly.

---

## Validation Rules (Validator.php)

**File:** `app/Models/PaymentLink/Validator.php`

Rules are defined as static arrays per operation:

```php
protected static $createRules = [
    Entity::TITLE           => 'required|string|min:3|max:80|utf8',
    Entity::DESCRIPTION     => 'string|max:65535|nullable|utf8|custom',
    Entity::SETTINGS        => 'nullable|array',
    Entity::PAYMENT_PAGE_ITEMS => 'required|sequential_array|min:1',
    // ...
];

protected static $editRules = [
    // Similar but different rules for update
];
```

### Rule Types

| Rule | Type | Description |
|------|------|-------------|
| `required`, `nullable` | Built-in Laravel | Standard validation |
| `string`, `array`, `email` | Built-in Laravel | Type validation |
| `min:X`, `max:X` | Built-in Laravel | Length/value limits |
| `utf8` | Custom | Custom UTF-8 validation |
| `custom` | Custom | Calls `validateFieldName()` method |
| `contact_syntax` | Custom | Phone number format |
| `epoch` | Custom | Unix timestamp |
| `mysql_unsigned_int` | Custom | MySQL int range |

### Custom Validators

When a rule contains `custom`, it calls a method named `validate{FieldName}`:

```php
// Rule
Entity::CURRENCY => 'filled|string|currency|custom',

// Calls this method automatically
public function validateCurrency($attribute, $value)
{
    // Custom validation logic
}
```

---

## Entity Defaults and Attributes

**File:** `app/Models/PaymentLink/Entity.php`

```php
protected $defaults = [
    self::STATUS      => Status::ACTIVE,
    self::CURRENCY    => 'INR',
    self::VIEW_TYPE   => self::VIEW_TYPE_PAGE,
    // ...
];

protected $fillable = [
    self::TITLE,
    self::DESCRIPTION,
    // Fields that can be set via input
];
```

---

## Settings (Nested Validation)

Settings are validated using dot notation:

```php
protected static $createRules = [
    Entity::SETTINGS => 'nullable|array',
    Entity::SETTINGS . '.' . Entity::GOAL_TRACKER => 'nullable|array',
    Entity::SETTINGS . '.' . Entity::UDF_SCHEMA   => 'nullable|json',
    // ...
];
```

**Note:** GoalTracker's `tracker_type` validation is NOT in monolith's `$createRules`. This causes the common "tracker_type required" diff because NCA validates it but monolith doesn't.

---

## Common Gotchas

### 1. Validation happens in build(), not explicitly called

You won't find `$validator->validate()` calls. Look for `$entity->build($input)`.

### 2. Custom rules call magic methods

`'custom'` in rules → calls `validateFieldName()` method in Validator.php.

### 3. Nested settings validation

Settings fields are validated via dot notation: `settings.goal_tracker`.

### 4. PaymentLink = PaymentPage

Don't be confused by the naming. Same thing.

### 5. Validator class extends Base\Validator

Custom validation methods like `validateCurrency()`, `validateViewType()` are in the class.

---

## Finding Validation for a Specific Field

1. Open `app/Models/PaymentLink/Validator.php`
2. Search for `$createRules` (or `$editRules` for update)
3. Find the field name
4. If rule contains `custom`, search for `validateFieldName()` method

Example: Finding `view_type` validation:
```php
// In $createRules
Entity::VIEW_TYPE => 'sometimes|string|custom',

// Search for:
public function validateViewType($attribute, $value)
```

---

## Quick File Reference

| Need | File |
|------|------|
| Route definition | `app/Http/Route.php` |
| Controller | `app/Http/Controllers/PaymentLinkController.php` |
| Service layer | `app/Models/PaymentLink/Service.php` |
| Business logic | `app/Models/PaymentLink/Core.php` |
| Validation rules | `app/Models/PaymentLink/Validator.php` |
| Entity/Model | `app/Models/PaymentLink/Entity.php` |
| Constants | `app/Models/PaymentLink/Constants.php` |
| Payment Page Items | `app/Models/PaymentLink/PaymentPageItem/` |


