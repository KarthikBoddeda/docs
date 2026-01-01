# Payment Pages Code Reference

This folder contains code documentation for Payment Pages APIs in NCA service.

> **⚠️ IMPORTANT:** NCA code is written to **exactly mimic monolith behavior**. Any mismatch between NCA and monolith is a bug that needs fixing. Monolith is the source of truth until NCA becomes reliable. Optimizations can be done later.

---

## Index

### NCA Code

| API | File | Description |
|-----|------|-------------|
| `payment_page_create` | [pp-create.md](./pp-create.md) | `POST /payment_pages` - Create payment page (NCA) |
| Proxying Logic | [proxying.md](./proxying.md) | How NCA proxies requests to monolith |

### Monolith (API) Code

| API | File | Description |
|-----|------|-------------|
| `payment_page_create` | [api-pp-create.md](./api-pp-create.md) | `POST /payment_pages` - Create payment page (Monolith) |
| **Navigation Guide** | [monolith-navigation-guide.md](./monolith-navigation-guide.md) | How to navigate PHP monolith code (start here!) |

---

## Code Organization

### NCA (no-code-apps repo)

```
no-code-apps/internal/
├── router/payment_page_private_routes.go    # Route definitions
├── controllers/payment_page.go              # HTTP handlers
├── modules/
│   ├── payment_page/                        # Payment Page module
│   │   ├── core.go                          # Business logic
│   │   ├── validation.go                    # PP-specific validations
│   │   ├── request.go, response.go          # Request/Response structs
│   │   └── constants.go                     # Proxy states
│   └── nocode/                              # Base nocode module
│       ├── validation.go                    # Base validations (TrackerType check!)
│       └── settings.go                      # Settings struct
└── monolith_decomp/
    ├── dual_write_handlers/base.go          # Dual write logic
    └── diffs/diff_checker.go                # Diff calculation
```

### Monolith (api repo)

> **Note:** Code uses `PaymentLink` naming for legacy reasons. See [monolith-navigation-guide.md](./monolith-navigation-guide.md).

```
api/app/
├── Http/
│   ├── Route.php                            # Route definitions
│   └── Controllers/PaymentLinkController.php
└── Models/PaymentLink/                      # Payment Page model folder
    ├── Service.php                          # Service layer
    ├── Core.php                             # Business logic
    ├── Validator.php                        # Validation rules (implicit!)
    ├── Entity.php                           # Entity model
    └── PaymentPageItem/                     # Line items
```

---

## Key Concepts

### Proxy States

The system can operate in different states (see [proxying.md](./proxying.md)):

| State | Source of Truth | Writes | Reads |
|-------|-----------------|--------|-------|
| `monolith_only` | Monolith | Proxy to monolith | Proxy to monolith |
| `dual_write_no_reads_no_external` | Monolith | Both, compare | Proxy to monolith |
| `dual_write_shadow_read_no_external` | Monolith | Both, compare | Both, compare, return monolith |
| `dual_write_read_no_external` | Monolith | Both, compare | NCA only |
| `dual_write_read_external` | NCA | Both (NCA first) | NCA only |
| `nca_only` | NCA | NCA only | NCA only |

### Validation Layers

Validations happen at multiple levels:
1. **Request Binding** - JSON parsing
2. **Request Validation** - `ValidateForCreate()` on request struct
3. **Merchant-based Validation** - `ValidateCreateRequestBasedOnMerchantDetails()`
4. **Entity Validation** - `Validate()` on entity struct

---

## Adding New API Docs

When documenting a new API:
1. Create `<api-name>.md` in this folder
2. Include: Route info, code flow (both NCA & monolith), validation points, key differences
3. Update this index
4. Reference from the relevant task doc in `tasks/`

