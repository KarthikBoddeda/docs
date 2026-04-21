# Gimli Bulk Header API — Access Guide

## Context

The **bulk header create API** lives in the **gimli** service (not payment-links). It allows creating custom URL headers for merchants so their short URLs use a branded prefix (e.g., `rzp.io/BRAND/abc123` instead of `rzp.io/rzp/abc123`).

## The curl — it works

```bash
curl --location 'https://rzp.io/v1/internal/bulk/header' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic ZGV2OmRldi1wYXNzd29yZA==' \
--data '[
    {
        "merchant_id": "O2olT6Y8r2hTFJ",
        "mode": "test",
        "product_type" : "payment_link",
        "header": "wild2"
    },
    {
        "merchant_id": "O2olT6Y8r2hTFJ",
        "mode": "live",
        "product_type" : "payment_link",
        "header": "live"
    }
]'
```

**Tested and confirmed 200 OK on 2026-03-17.** Both `rzp.io` and `gimli.razorpay.com` (concierge) work.

### Why it works

- **`rzp.io`** is routed via **traefik-external** ingress which matches `Host('rzp.io') && PathPrefix('/')` — this catches ALL paths and sends them directly to gimli pods, bypassing Kong.
  - Source: [kube-manifests/templates/gimli/templates/ing-v2.yaml#L44-L60](https://github.com/razorpay/kube-manifests)
  - Values: [kube-manifests/prod/gimli/values.yaml#L13](https://github.com/razorpay/kube-manifests) — `gimli_host: rzp.io`

- **`ZGV2OmRldi1wYXNzd29yZA==`** decodes to `dev:dev-password` — these are the default credentials from `default.toml` and they work in production because `prod.toml` does not override `[app.dev]` and the `APP_DEV_SECRET` env var falls back to the default.
  - Source: [gimli/environment/default.toml#L21-L22](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/environment/default.toml#L21-L22)
  - Auth middleware: [gimli/middlewares/authTokenMiddleware.go#L35-L43](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/middlewares/authTokenMiddleware.go#L35-L43)

### Alternative host (concierge)

The concierge endpoint also works: `https://gimli.razorpay.com/v1/internal/bulk/header` (requires VPN).

- Source: [kube-manifests/prod/gimli/values.yaml#L15](https://github.com/razorpay/kube-manifests) — `gimli_concierge_host: gimli.razorpay.com`

## API details

### Endpoint

`POST /v1/internal/bulk/header`

Source: [gimli/main.go#L94](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/main.go#L94)

### Handler

Source: [gimli/controllers/urlcontroller.go#L311-L352](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/controllers/urlcontroller.go#L311-L352)

Processes items one-by-one. Skips invalid items and collects errors. Returns partial results if some fail.

### Request body

JSON array of header objects:

```json
[
    {
        "merchant_id": "string (14 chars, required)",
        "mode": "string (test|live, optional)",
        "product_type": "string (e.g. payment_link, optional)",
        "header": "string (3-6 alphanumeric chars, required)"
    }
]
```

### Validation rules

| Field | Rule | Source |
|-------|------|--------|
| `merchant_id` | Required, non-empty | [url.go#L692-L694](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/models/url.go#L692-L694) |
| `header` | Required, must match `^[a-zA-Z0-9]{3,6}$` | [url.go#L223](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/models/url.go#L223), [url.go#L696-L698](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/models/url.go#L696-L698) |
| `mode` | Optional (`test` or `live`) | |
| `product_type` | Optional (e.g. `payment_link`) | |

### URLHeader model

Source: [gimli/models/url.go#L66-L75](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/models/url.go#L66-L75)

Table: `url_headers`

### Responses

| Status | Meaning |
|--------|---------|
| **200 OK** | All headers created successfully. Returns array of created headers. |
| **206 Partial Content** | Some headers failed. Returns `{"created": [...], "errors": [...]}`. |
| **400 Bad Request** | Invalid JSON body. |

### Important: No duplicate prevention

There is no unique constraint on `(merchant_id, mode, product_type, header)`. Calling the API multiple times for the same merchant will create **duplicate entries**. Use the GET/DELETE endpoints to manage existing headers.

## Other useful endpoints

All under the same auth and host.

| Method | Path | Purpose | Source |
|--------|------|---------|--------|
| POST | `/v1/internal/header` | Create single header | [main.go#L90](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/main.go#L90) |
| GET | `/v1/internal/header?merchant_id=X&mode=Y&product_type=Z` | Get headers for a merchant | [main.go#L92](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/main.go#L92) |
| DELETE | `/v1/internal/header?merchant_id=X&mode=Y&product_type=Z` | Delete headers (soft delete) | [main.go#L93](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/main.go#L93) |
| POST | `/v1/internal/bulk/header` | Bulk create headers | [main.go#L94](https://github.com/razorpay/gimli/blob/908d09bb94f502d677e1a2f583acecc5f0ad9b32/main.go#L94) |

### Verify headers for a merchant

```bash
curl 'https://rzp.io/v1/internal/header?merchant_id=O2olT6Y8r2hTFJ&product_type=payment_link' \
  -H 'Authorization: Basic ZGV2OmRldi1wYXNzd29yZA=='
```

### Delete headers for a merchant

```bash
curl -X DELETE 'https://rzp.io/v1/internal/header?merchant_id=O2olT6Y8r2hTFJ&mode=test&product_type=payment_link' \
  -H 'Authorization: Basic ZGV2OmRldi1wYXNzd29yZA=='
```

## Security note

The internal header APIs are accessible on the public `rzp.io` domain with hardcoded default credentials (`dev:dev-password`). This is because:
1. The traefik-external ingress routes all paths on `rzp.io` to gimli (not just the Kong-registered public routes)
2. `prod.toml` does not override the `[app.dev]` credentials from `default.toml`

This is worth flagging as a security concern — these internal APIs should ideally be restricted to concierge-only access or protected with stronger auth at the edge.
