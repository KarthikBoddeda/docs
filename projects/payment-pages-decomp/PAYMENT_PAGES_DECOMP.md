# Overview

This document outlines the decomposition of **Payment Pages** functionality from the monolithic API service to the NoCodeApp (NCA) service, including current architecture, target state, migration flows, and implementation tasks.

---

# Target State Architecture

The target state after full migration - NCA service will serve all Payment Pages traffic independently.

```mermaid
flowchart LR
    subgraph Clients[" "]
        direction TB
        MD[Merchant Dashboard]
        HP[Hosted Pages]
        CR[Crons etc.]
    end

    subgraph EdgeBox[" "]
        AUTH[Auth<br/>Rate Lt]
    end

    subgraph Monolith[Monolith]
        direction TB
        MO[Merchant/Org<br/>Details]
        PGR[PG Router]
        PW[Payment<br/>Worker]
    end

    subgraph NCABox[" "]
        direction TB
        CURL[Custom URL]
        NCAS[NCAS]
        CACHE[(Cache)]
    end

    subgraph Storage[" "]
        direction TB
        DB[(DB)]
        ES[(ES)]
    end

    subgraph Queue[" "]
        MQ[/Queue/]
    end

    subgraph Workers[Workers]
        direction TB
        PWH[Partner Webhook]
        RW[Receipt Wrk]
        RISKW[Risk Worker]
        ESW[ES Worker]
        PEW[Payment Events<br/>Worker]
    end

    subgraph External[" "]
        direction TB
        STORK[Stork]
        IRG[Invoice Receipt<br/>Generation]
        RISKS[Risk Service]
    end

    MD --> AUTH
    HP --> AUTH
    CR --> AUTH
    AUTH --> NCAS

    NCAS --- CURL
    NCAS ---|fetch| MO
    NCAS -->|create order| PGR
    PW -->|payment events CB| NCAS

    NCAS --- CACHE
    NCAS --> DB
    NCAS --> ES

    NCAS --> MQ
    MQ --> PWH
    MQ --> RW
    MQ --> RISKW
    MQ --> ESW
    MQ --> PEW

    PWH --> STORK
    RW --> IRG
    RISKW --> RISKS
    ESW -->|update ES| ES
    PEW -->|update analytics| DB

    style EdgeBox fill:#f5f5f5,stroke:#333
    style NCABox fill:#f5f5f5,stroke:#333
    style Monolith fill:#fff,stroke:#333
    style Workers fill:#f5f5f5,stroke:#333
```

---

# Migration Phase Architecture

During migration, NCA acts as a proxy layer handling dual writes, shadowing, and gradual traffic shift.

```mermaid
graph LR
    Edge -->|1| NCA[no-code-app service]
    NCA -->|11| Edge
    NCA -->|2 proxy| Monolith_Apps[Existing Apps Module]
    Monolith_Apps -->|3| NCA
    NCA -.->|4,5| Monolith_Merchant[Merchant/Org Details]
    NCA -.->|6,7| Splitz[Splitz/Gimli/DCS]
    NCA -.->|8| NCADB[(NoCodeApps DB)]
    NCA -.->|9| ES[(Elasticsearch)]
    NCA -.->|10| Diff[Diff Logs/Metrics]
```

**Components:**
- **Edge**: Entry point, routes requests to NCA
- **NCA (no-code-app service)**: Central service handling proxying, dual writes, shadowing
- **Monolith**: Contains Existing Apps Module (proxied) and Merchant/Org Details
- **New NCA Infrastructure** (dotted lines): NoCodeApps DB, Elasticsearch, Diff Logs, Splitz/Gimli/DCS

**Migration Flow Steps:**
1. Edge routes request to NCA service
2. NCA proxies request to Monolith's Existing Apps Module
3. Monolith returns response
4. NCA fetches merchant/org details from Monolith
5. Merchant data returned
6. NCA checks Splitz/Gimli/DCS for experiment flags
7. Flag configuration returned
8. NCA performs dual write to its own DB
9. NCA indexes data to Elasticsearch
10. NCA logs diffs/metrics for comparison
11. Final response returned to Edge

---

# Request Flow during Migration

## Database Architecture & ID Reuse Pattern

The migration uses separate databases for Monolith and NCA services with a specific ID reuse strategy:

- **Monolith DB**: Existing database used by the monolith API
- **NCA DB**: New database used by NoCodeApp service
- **ID Reuse Pattern**:
    - **States `dual_write_no_reads_no_external` through `dual_write_read_no_external`**: Entities created in Monolith first, then NCA uses same IDs
    - **State `dual_write_read_external`**: Entities created in NCA first, then copied to Monolith with same IDs
    - **State `nca_only`**: Only NCA DB is used


## Request Flow - Write/Read APIs

**APIs covered by this flow:**

### Write APIs (Need NCA proxy for dual write)

| API Route Name | Route Signature | Description | Status |
|----------------|-----------------|-------------|--------|
| `payment_page_create` | `POST /payment_pages` | Create a payment page (shared by buttons, subscription_buttons, pages, file_upload_page) | |
| `payment_page_update` | `PATCH /payment_pages/{id}` | Update a payment page | |
| `payment_page_create_order` | `POST /payment_pages/{id}/order` | Create Order | |
| `payment_page_set_receipt_details` | `POST /payment_pages/{id}/receipt` | Set receipt details for a page | |
| `payment_page_activate` | `PATCH /payment_pages/{id}/activate` | Activate a payment page | |
| `payment_page_deactivate` | `PATCH /payment_pages/{id}/deactivate` | Deactivate a payment page | |
| `payment_page_item_update` | `PATCH /payment_pages/payment_page_item/{id}` | Update a payment page item | |

### Read APIs

| API Route Name | Route Signature | Description | Status |
|----------------|-----------------|-------------|--------|
| `pages_view` | `GET/POST /pages/{x_entity_id}/view` | Hosted page view by page id | |
| `pages_view_by_slug` | `GET/POST /pages/{slug}` | Hosted page view by slug | |
| `pages_view_by_slug_empty` | `GET/POST /pages` | Hosted page view by empty slug | |
| `payment_page_list` | `GET /payment_pages` | Get list of pages for a merchant | |
| `payment_page_get` | `GET /payment_pages/{id}` | Get payment page by ID | |
| `payment_page_get_details` | `GET /payment_pages/{id}/details` | Get detailed information on a page | |
| `payment_page_view_get` | `GET/POST /payment_pages/{x_entity_id}/view` | Hosted page view by page id | |
| `payment_page_get_invoice_details` | `GET /payment_pages/{payment_id}/receipt` | Fetch receipt details for a page | |
| `payment_page_notify` | `POST /payment_pages/{id}/notify` | Sends notification to end customer | |
| `payment_page_send_receipt` | `POST /payment_pages/{payment_id}/send_receipt` | Send receipt details to end user | |
| `payment_page_save_receipt_for_payment` | `POST /payment_pages/{payment_id}/save_receipt` | Save receipt for a payment | |
| `fetch_product_details_for_order` | `GET orders/{id}/product_details` | Get payment page details from order id (specific to pages and buttons) | |
| `payment_page_slug_exists` | `GET /payment_pages/{slug}/exists` | Check if slug exists already | |
| `payment_page_expire_cron` | `POST /payment_pages/expire` | Called from cron to expire a page (Internal) | |

```mermaid
sequenceDiagram
    participant Client
    participant Edge
    participant NCA as NoCodeApp Service
    participant NCADB as NCA DB
    participant API as Monolith API
    participant MDB as Monolith DB
    participant Ext as External Services

    Client->>Edge: API Request
    Edge->>NCA: Route to NCA (based on routing rules)

    Note over NCA: Splitz Experiment Check

    alt proxy_state = monolith_only
        NCA->>API: Forward request to monolith
        API->>MDB: Database operation
        API->>Ext: External entity calls
        API-->>NCA: Response
    else proxy_state = dual_write_no_reads_no_external
        Note over NCA: Only for writes. No change in read APIs behavior
        NCA->>API: Forward to monolith
        API->>MDB: Create entities in monolith
        API->>Ext: External entity calls
        API-->>NCA: Response
        NCA->>NCA: Process in NCA (skip external calls)
        NCA->>NCADB: Create entities with monolith IDs
        Note over NCA: Calculate diffs and use monolith response
    else proxy_state = dual_write_shadow_read_no_external
        Note over NCA: Writes same as above, for reads we enable shadowing
        NCA->>API: Forward to monolith
        API->>MDB: Database operations
        API-->>NCA: Response
        NCA->>NCA: Process in NCA
        NCA->>NCADB: Database operations
        Note over NCA: Compare responses, return monolith response
    else proxy_state = dual_write_read_no_external
        Note over NCA: Writes same as above, for reads we use nca response
        NCA->>NCA: Process in NCA
        NCA->>NCADB: Database operations
        Note over NCA: no monolith call here. just use NCA response
    else proxy_state = dual_write_read_external
        Note over NCA: Reads same as above, for writes, NCA creates IDs first and makes the external calls
        NCA->>NCA: Process in NCA
        NCA->>NCADB: Create entities in NCA (generates IDs)
        NCA->>API: Dual write to monolith with NCA IDs
        API->>MDB: Write to monolith db
        NCA->>Ext: External entities calls
    else proxy_state = nca_only
        NCA->>NCADB: Create entities
        NCA->>Ext: External entity calls
    end

    NCA-->>Edge: Final response
    Edge-->>Client: Response
```
