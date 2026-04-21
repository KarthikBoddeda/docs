# Topic: TiDB Bulk Data Correction Optimization

## Definition

**Bulk data correction** is the process of fixing incorrect data across large numbers of rows in a database, typically triggered by an incident (wrong credentials, bad migration, corrupt import). Optimizing these jobs is critical during incidents because stakeholders are waiting on correct data.

## Common Performance Bottlenecks

### 1. Row-by-row updates

```sql
-- SLOW: one transaction per row
UPDATE merchants SET status = 'active' WHERE id = 'M001';
UPDATE merchants SET status = 'active' WHERE id = 'M002';
-- ... repeat 100,000 times
```

**Fix:** Batch updates

```sql
-- FAST: one transaction per batch
UPDATE merchants SET status = 'active'
WHERE id IN ('M001', 'M002', ..., 'M1000');
-- 100 batches instead of 100,000 individual updates
```

### 2. Missing indexes on filter columns

If the correction query filters on a non-indexed column, every batch requires a **full table scan**:

```sql
-- If 'corrupted_at' is not indexed, this scans entire table per batch
UPDATE merchants SET data = fix(data)
WHERE corrupted_at BETWEEN '2025-12-26' AND '2025-12-26'
LIMIT 1000;
```

**Fix:** Add a temporary index before correction, drop it after:

```sql
CREATE INDEX idx_temp_corrupted ON merchants(corrupted_at);
-- run correction
DROP INDEX idx_temp_corrupted ON merchants;
```

### 3. Large transactions

TiDB has a transaction size limit (default: 100MB). Very large batch updates can exceed this:

```sql
-- May exceed TiDB's transaction size limit
UPDATE merchants SET data = fix(data)
WHERE date = '2025-12-26';  -- millions of rows
```

**Fix:** Break into smaller batches using LIMIT + ORDER BY:

```sql
UPDATE merchants SET data = fix(data)
WHERE date = '2025-12-26' AND id > last_processed_id
ORDER BY id
LIMIT 1000;
```

### 4. No parallelism

Single-threaded correction on a distributed database wastes TiDB's multi-node architecture.

**Fix:** Partition by a shard key (e.g., date, merchant ID range) and run parallel workers:

```
Worker 1: date = '2025-12-25'
Worker 2: date = '2025-12-26'
Worker 3: date = '2025-12-27'
```

### 5. Excessive column selection

```sql
-- SLOW: reads all columns from disk
SELECT * FROM merchants WHERE date = '2025-12-26';

-- FAST: reads only needed columns
SELECT id, data FROM merchants WHERE date = '2025-12-26';
```

## The Two-Track Incident Pattern

From the [TiDB Data Correction 4x Speedup](/learnings/stories/tidb-data-correction-4x-speedup.md) story:

```
Track 1: Run the slow-but-correct job (safety net)
Track 2: Optimize the job in parallel

If optimization succeeds → switch to fast job for remaining work
If optimization fails → slow job is still running, no time lost
```

This hedging strategy ensures you don't delay the fix while pursuing optimization.

## Optimization Checklist

| Check | Action |
|---|---|
| Row-by-row? | Switch to batched updates (100-1000 rows per batch) |
| Full table scans? | Add temporary index on filter columns |
| Single-threaded? | Parallelize by date/shard key |
| Large transactions? | Break into smaller batches with LIMIT |
| SELECT *? | Select only required columns |
| Verification? | Run COUNT/checksum after correction to verify |

## TiDB-Specific Considerations

- **TiKV region splitting:** Large batch updates may cause region splits. Monitor with `pd-ctl` during correction.
- **GC lifetime:** If correction runs long, increase `tikv_gc_life_time` to prevent old versions from being garbage collected mid-correction.
- **Rate limiting:** Use `BATCH ON ... LIMIT ...` syntax (TiDB 6.0+) for built-in rate-limited batch DML.

## Related

- [Story: TiDB Data Correction 4x Speedup](/learnings/stories/tidb-data-correction-4x-speedup.md)
