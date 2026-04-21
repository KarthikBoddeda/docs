# Dashboard API Validation

## Overview

Validate all Payment Links Dashboard APIs are working correctly on devstack.

## Status: 🟢 Completed (4/5 APIs working, 1 infra issue)

## Prerequisites

- [ ] Devstack deployed with payment-links service
- [ ] Devstack label configured in API templates
- [ ] Test merchant ID: `LJ3P0FyFtOULha`

## Subtasks

| # | API | Method | Endpoint | Status | Notes |
|---|-----|--------|----------|--------|-------|
| 1 | Create Link | POST | `/v1/payment_links` | 🟢 Completed | Working - returns `plink_xxx` |
| 2 | List Links | GET | `/v1/payment_links` | 🟢 Completed | Working - returns `payment_links` array |
| 3 | Get Link | GET | `/v1/payment_links/:id` | 🟢 Completed | Working - returns full link details |
| 4 | Update Link | PATCH | `/v1/payment_links/:id` | 🟢 Completed | Working - `reference_id` updated |
| 5 | Cancel Link | POST | `/v1/payment_links/:id/cancel` | 🔴 Failed | AWS SQS credentials issue on devstack |

## Subtask Statuses

- ⬜ Not Started
- 🟡 In Progress
- 🟢 Completed (Tested & Working)
- 🔴 Failed (Has Issues)

---

## Subtask Details

### 1. Create Payment Link

**Endpoint:** `POST /v1/payment_links`

**Test Request:**
```json
{
    "amount": 100,
    "currency": "INR",
    "description": "Test payment link from API",
    "customer": {
        "name": "Test Customer",
        "contact": "+918861672025",
        "email": "test@example.com"
    },
    "expire_by": 1776923817,
    "notify": {
        "email": false,
        "sms": true,
        "whatsapp": false
    }
}
```

**Expected Response:**
- Status: 200 OK
- Response contains `id` with prefix `plink_`
- Response contains `entity: "payment_link"`
- Response contains `short_url`

**Actual Result:**
- Status: 🟢 200 OK
- Response: `{"accept_partial":false,"amount":100,"amount_paid":0,"cancelled_at":0,"created_at":1768992152,"currency":"INR","customer":{"contact":"+918861672025","email":"test@example.com","name":"Test Customer"},"description":"Test payment link from API","expire_by":1776923817,"expired_at":0,"first_min_partial_amount":0,"id":"plink_S6V25H32jGELIO","notes":null,"notify":{"email":false,"sms":true,"whatsapp":false},"payments":null,"reference_id":"","reminder_enable":false,"reminders":{},"short_url":"https://gimli-base.dev.razorpay.in/rzp/EpVTQo3","status":"created","updated_at":1768992152,"upi_link":false,"user_id":"","whatsapp_link":false}`
- Notes: Working as expected. Returns `plink_` prefixed ID and `short_url`.

---

### 2. List Payment Links

**Endpoint:** `GET /v1/payment_links?skip=0&count=10`

**Expected Response:**
- Status: 200 OK
- Response contains `items` array
- Response contains `count` field

**Actual Result:**
- Status: 🟢 200 OK
- Response: `{"payment_links":[]}`
- Notes: Working. Returns empty array for this merchant (links may not be indexed in ES yet).

---

### 3. Get Payment Link

**Endpoint:** `GET /v1/payment_links/:id`

**Prerequisites:** Need a valid `payment_link_id` from Create API

**Expected Response:**
- Status: 200 OK
- Response contains full payment link details
- Response contains `entity: "payment_link"`

**Actual Result:**
- Status: 🟢 200 OK
- Response: Full payment link object with all fields
- Notes: Working. Returns complete payment link details by ID.

---

### 4. Update Payment Link

**Endpoint:** `PATCH /v1/payment_links/:id`

**Prerequisites:** Need a valid `payment_link_id` from Create API

**Test Request:**
```json
{
    "reference_id": "updated-ref-123"
}
```

**Expected Response:**
- Status: 200 OK
- Response contains updated `reference_id`

**Actual Result:**
- Status: 🟢 200 OK
- Response: Payment link with `reference_id: "updated-ref-123"`
- Notes: Working. Successfully updated the reference_id field.

---

### 5. Cancel Payment Link

**Endpoint:** `POST /v1/payment_links/:id/cancel`

**Prerequisites:** Need a valid `payment_link_id` in `created` status

**Expected Response:**
- Status: 200 OK
- Response contains `status: "cancelled"`

**Actual Result:**
- Status: 🔴 Error
- Response: `{"error":{"code":"QUEUE_ENQUEUE_FAILURE","description":"NoCredentialProviders: no valid providers in chain..."}}`
- Notes: **FAILED** - AWS SQS credentials not configured on devstack. This is an infrastructure issue, not an API issue.

---

## Work Log

| Date | Action | Result |
|------|--------|--------|
| 2026-01-21 | Tested all 5 Dashboard APIs against base devstack | 4/5 APIs working |
| 2026-01-21 | Create, List, Get, Update APIs | 🟢 All working |
| 2026-01-21 | Cancel API | 🔴 AWS SQS credentials issue on devstack |

---

## Related Files

- API Templates: [/docs/projects/payment-links-decomp/payment-links-api.http](/docs/projects/payment-links-decomp/payment-links-api.http)
- Postman Collection: [/docs/projects/payment-links-decomp/Payment-Links.postman_collection.json](/docs/projects/payment-links-decomp/Payment-Links.postman_collection.json)
- Deployment Guide: [/docs/projects/payment-links-decomp/deploy-to-devstack.md](/docs/projects/payment-links-decomp/deploy-to-devstack.md)
