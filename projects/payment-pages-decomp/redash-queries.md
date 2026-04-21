# Redash Queries - Payment Pages Decomposition

Direct MySQL queries for the monolith and NCA DBs (via Redash).

**Merchant exclusion list** (test/internal merchants — same for all queries):
```
'RGzkFbQMhEVxhO', 'RFNMAWAYrA0hQD', 'RNpuBjh3LInMP1', 'QedWZefco2y2EA',
'Qq82BbjBr05Puh', 'DBeZ7DIU7L8wae', 'R1zuJZIHpAp6hf', 'R7Y2Dervg5gGGU',
'Oj581PzHLVRxC7', 'E3t3a2CPXQheb4', 'IcpNy3QUNDyNVE', 'Nb3LsbAB1ToDoA',
'G7NMeax5Gewf8a', 'H9OTnVWUomZFRH', 'Qqv3ROJPJbRIte', 'S2weyEuIGyJea4',
'OsfUYocg447V4q', 'I7xsnTCezlNBUx', 'QxnNidPPJVSamO', 'Rtqep4DUv7EmNC',
'RJ50Be6vFJ8jEc', 'RehuE0RHDiIaVC', 'R2QqWoGtqIMYZd', 'IgSJ0eqRBzyopb',
'Qxhak9YqVLOg2c', 'PfHRcImw0wXm5q', 'Q35jgV9BxiOLB7', 'F4nh3jBiH6yDGz',
'ReT7Pl4HOtZHCU', 'Jm5NuHPOevlGjc', 'GFgVQ22W7LOjwQ', 'QmiQDQbbz6M6RI',
'NSBm9qrpaKRUTq', 'PaS9HFGajwrJKL', 'JI4sdkUpF3pwhu', 'Ha18e7jHMVjYEb',
'ON0fLjgxT0piuQ', 'O5fUwEkTm6kG8P', 'M0xDktKEVkwjMu', 'N8NJICx3XDfP8U',
'Qqu5myFMhxgXtB', 'Q5lN5wEahShGn4', 'HVcrMm15PVZFNx', 'INm4viwxSqTTZo',
'RnV89DaE06b2kn', 'R0fO7IjFL9lEhT', 'RJ6JSVTlEIWlpr', 'RrRAhIezVg8VmB',
'DGpl8SzsSdc5MM', 'IgP1gE3lHWkQFc', 'HHhwpt2llhzbKS', 'RvOn6LUd6QKwqE',
'KKq8j9FkP5wa2A', 'KQ4Ou7uC2oJpgi', 'QefibgMIGGfG9M', 'FRJIooOPmPzW6Z',
'MtchSvbHI1IUlt', 'RGEeRPhcCv3zqO', 'IOi3H46aRzBFss', 'RN2uD47L3cZsWd',
'PrCuq0aEPFpu8z', 'QagXBwUNeuZFow', 'GD7mMjsQtkObxK'
```

---

## 1. Top payment pages by captured payments count

Finds the most-transacted recently-created pages, ordered by total payments captured.

**Monolith mapping:** `settings.key = 'captured_payments_count'`, value is a string → cast to UNSIGNED for numeric sort.
**NCA mapping:** `analytics.total_payments` (INT), joined via `analytics.module_id = nocode.id`.

### Monolith

**Fixes vs original query:**
- Added missing `AND` before `pl.view_type = 'page'` (syntax error)
- Cast `s.value` to `UNSIGNED` — stored as string, lexicographic sort would rank `"9"` above `"10"`

```sql
SELECT
    pl.id,
    pl.merchant_id,
    pl.title,
    pl.status,
    CAST(s.value AS UNSIGNED) AS captured_payments_count
FROM payment_links pl
JOIN settings s ON s.entity_id = pl.id
WHERE pl.merchant_id NOT IN (
    'RGzkFbQMhEVxhO', 'RFNMAWAYrA0hQD', 'RNpuBjh3LInMP1', 'QedWZefco2y2EA',
    'Qq82BbjBr05Puh', 'DBeZ7DIU7L8wae', 'R1zuJZIHpAp6hf', 'R7Y2Dervg5gGGU',
    'Oj581PzHLVRxC7', 'E3t3a2CPXQheb4', 'IcpNy3QUNDyNVE', 'Nb3LsbAB1ToDoA',
    'G7NMeax5Gewf8a', 'H9OTnVWUomZFRH', 'Qqv3ROJPJbRIte', 'S2weyEuIGyJea4',
    'OsfUYocg447V4q', 'I7xsnTCezlNBUx', 'QxnNidPPJVSamO', 'Rtqep4DUv7EmNC',
    'RJ50Be6vFJ8jEc', 'RehuE0RHDiIaVC', 'R2QqWoGtqIMYZd', 'IgSJ0eqRBzyopb',
    'Qxhak9YqVLOg2c', 'PfHRcImw0wXm5q', 'Q35jgV9BxiOLB7', 'F4nh3jBiH6yDGz',
    'ReT7Pl4HOtZHCU', 'Jm5NuHPOevlGjc', 'GFgVQ22W7LOjwQ', 'QmiQDQbbz6M6RI',
    'NSBm9qrpaKRUTq', 'PaS9HFGajwrJKL', 'JI4sdkUpF3pwhu', 'Ha18e7jHMVjYEb',
    'ON0fLjgxT0piuQ', 'O5fUwEkTm6kG8P', 'M0xDktKEVkwjMu', 'N8NJICx3XDfP8U',
    'Qqu5myFMhxgXtB', 'Q5lN5wEahShGn4', 'HVcrMm15PVZFNx', 'INm4viwxSqTTZo',
    'RnV89DaE06b2kn', 'R0fO7IjFL9lEhT', 'RJ6JSVTlEIWlpr', 'RrRAhIezVg8VmB',
    'DGpl8SzsSdc5MM', 'IgP1gE3lHWkQFc', 'HHhwpt2llhzbKS', 'RvOn6LUd6QKwqE',
    'KKq8j9FkP5wa2A', 'KQ4Ou7uC2oJpgi', 'QefibgMIGGfG9M', 'FRJIooOPmPzW6Z',
    'MtchSvbHI1IUlt', 'RGEeRPhcCv3zqO', 'IOi3H46aRzBFss', 'RN2uD47L3cZsWd',
    'PrCuq0aEPFpu8z', 'QagXBwUNeuZFow', 'GD7mMjsQtkObxK'
)
  AND pl.created_at > 1760000000
  AND pl.view_type = 'page'
  AND s.key = 'captured_payments_count'
ORDER BY CAST(s.value AS UNSIGNED) DESC
LIMIT 50;
```

### NCA

```sql
SELECT
    n.id,
    n.merchant_id,
    n.title,
    n.status,
    a.total_payments AS captured_payments_count
FROM nocode n
JOIN analytics a ON a.module_id = n.id
WHERE n.merchant_id NOT IN (
    'RGzkFbQMhEVxhO', 'RFNMAWAYrA0hQD', 'RNpuBjh3LInMP1', 'QedWZefco2y2EA',
    'Qq82BbjBr05Puh', 'DBeZ7DIU7L8wae', 'R1zuJZIHpAp6hf', 'R7Y2Dervg5gGGU',
    'Oj581PzHLVRxC7', 'E3t3a2CPXQheb4', 'IcpNy3QUNDyNVE', 'Nb3LsbAB1ToDoA',
    'G7NMeax5Gewf8a', 'H9OTnVWUomZFRH', 'Qqv3ROJPJbRIte', 'S2weyEuIGyJea4',
    'OsfUYocg447V4q', 'I7xsnTCezlNBUx', 'QxnNidPPJVSamO', 'Rtqep4DUv7EmNC',
    'RJ50Be6vFJ8jEc', 'RehuE0RHDiIaVC', 'R2QqWoGtqIMYZd', 'IgSJ0eqRBzyopb',
    'Qxhak9YqVLOg2c', 'PfHRcImw0wXm5q', 'Q35jgV9BxiOLB7', 'F4nh3jBiH6yDGz',
    'ReT7Pl4HOtZHCU', 'Jm5NuHPOevlGjc', 'GFgVQ22W7LOjwQ', 'QmiQDQbbz6M6RI',
    'NSBm9qrpaKRUTq', 'PaS9HFGajwrJKL', 'JI4sdkUpF3pwhu', 'Ha18e7jHMVjYEb',
    'ON0fLjgxT0piuQ', 'O5fUwEkTm6kG8P', 'M0xDktKEVkwjMu', 'N8NJICx3XDfP8U',
    'Qqu5myFMhxgXtB', 'Q5lN5wEahShGn4', 'HVcrMm15PVZFNx', 'INm4viwxSqTTZo',
    'RnV89DaE06b2kn', 'R0fO7IjFL9lEhT', 'RJ6JSVTlEIWlpr', 'RrRAhIezVg8VmB',
    'DGpl8SzsSdc5MM', 'IgP1gE3lHWkQFc', 'HHhwpt2llhzbKS', 'RvOn6LUd6QKwqE',
    'KKq8j9FkP5wa2A', 'KQ4Ou7uC2oJpgi', 'QefibgMIGGfG9M', 'FRJIooOPmPzW6Z',
    'MtchSvbHI1IUlt', 'RGEeRPhcCv3zqO', 'IOi3H46aRzBFss', 'RN2uD47L3cZsWd',
    'PrCuq0aEPFpu8z', 'QagXBwUNeuZFow', 'GD7mMjsQtkObxK'
)
  AND n.created_at > 1760000000
  AND n.type = 'page'
  AND n.deleted_at IS NULL
ORDER BY a.total_payments DESC
LIMIT 50;
```
