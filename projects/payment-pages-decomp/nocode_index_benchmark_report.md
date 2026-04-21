# Index Request: `nocode` table — composite index for list queries

## Table

- **Database:** nocode-apps (payment pages)
- **Table:** `nocode`
- **Engine:** InnoDB, utf8mb4

## Table stats

| Metric | Value |
|--------|-------|
| Total rows | 1,586,973 |
| Distinct merchants | 256,097 |
| Distinct modes | 2 |
| Distinct types | 2 |
| Distinct created_at | 1,544,169 |
| Data size | 4,788 MB |
| Current index size | 197 MB |

## Problem

The list API query runs with `ORDER BY created_at DESC`. With only `nocode_merchant_id_index(merchant_id)` available, MySQL does a filesort on all rows for the merchant (~85k for the heaviest merchant). This takes **~12s** in Redash. Removing `ORDER BY` from the same query brings it to **<1s**, confirming the sort is the bottleneck.

## Proposed index

```sql
CREATE INDEX idx_nocode_list ON nocode (merchant_id, mode, type, created_at DESC);
```

**Why these columns in this order:**
- `merchant_id, mode, type` — equality filters in the WHERE clause
- `created_at DESC` — satisfies ORDER BY without filesort

## Estimated impact

| Metric | Value |
|--------|-------|
| Estimated new index size | ~109 MB (raw), ~140–170 MB with InnoDB overhead |
| Total index size after | ~340–370 MB (from current 197 MB) |
| Index creation method | Online DDL (`ALGORITHM=INPLACE`, no table lock) |
| Expected creation time | Seconds to ~1 min (1.6M rows, 5 GB table) |
| Write overhead | Minimal — one extra index to maintain on INSERT/UPDATE/DELETE |

## Index to drop (redundant after creation)

```sql
DROP INDEX nocode_merchant_id_index ON nocode;
```

`nocode_merchant_id_index(merchant_id)` is fully covered by the leftmost prefix of `idx_nocode_list(merchant_id, mode, type, created_at)`.

**Keep:** `nocode_created_at_index(created_at)`, `idx_expire_by(expire_by)` — serve different queries.

## Existing indexes

```
PRIMARY KEY (`id`)
KEY `nocode_merchant_id_index` (`merchant_id`)       ← to be dropped (redundant)
KEY `nocode_created_at_index` (`created_at`)          ← keep
KEY `idx_expire_by` (`expire_by`)                     ← keep
```

## Query that benefits

```sql
SELECT * FROM nocode
WHERE merchant_id = ? AND mode = ? AND type = ?
ORDER BY created_at DESC
LIMIT 25 OFFSET 0;
```

Currently: uses `nocode_merchant_id_index` → filesort → **~12s** for heavy merchants.  
After index: uses `idx_nocode_list` → no filesort → expected **sub-second**.

## Verification (post-creation)

```sql
EXPLAIN SELECT * FROM nocode
WHERE merchant_id = 'Ha18e7jHMVjYEb'
  AND mode = 'live' AND type = 'page'
ORDER BY created_at DESC
LIMIT 25 OFFSET 0;
```

Expected: `key: idx_nocode_list`, no `Using filesort` in Extra.
