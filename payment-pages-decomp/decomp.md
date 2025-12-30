# Overview
This document outlines the decomposition of payment handle functionality from the monolithic API service to the NoCodeApp (NCA) service, including current patterns, migration flows, and implementation tasks.

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
<--TODO: update the APIs>
**Write APIs:**
- `payment_handle_create` - `POST /payment_handle`
- `payment_handle_update` - `PATCH /payment_handle`
- `payment_page_create_order` - `POST /payment_pages/{id}/order` (when view_type is handle)
- `payment_page_set_merchant_details` - For handle-related settings

**Read APIs:**
- `payment_handle_get` - `GET /payment_handle`
- `payment_handle_availability` - `GET /payment_handle/{slug}/exists`
- `payment_handle_suggestion` - `GET /payment_handle/suggestion`
- `payment_handle_amount_encryption` - `POST /payment_handle/custom_amount`
- `pages_view_by_slug` - `GET /pages/{slug}` (for payment handles)
- `payment_page_get_details` - For handle details from dashboard
- `payment_page_get` - Handle-related page data
- `payment_page_fetch_merchant_details` - For handle-related settings

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
