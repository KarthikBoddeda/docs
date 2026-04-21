# Settings Diff Queries (Monolith vs NCA)

Individual datalake queries to find mismatches between monolith and NCA for each setting field.

**Tables:**
- `realtime_hudi_api.payment_links` — monolith payment_links
- `realtime_hudi_api.settings` — monolith KV settings (key/value per entity)
- `realtime_prod_no_code_apps.nocode` — NCA nocode entity table
- `realtime_prod_no_code_apps.configs` — NCA config KV table (config_key/value per module)

**Merchant exclusion list** (test/internal merchants, same for all queries):
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

## 1. udf_schema

Monolith: `settings` key=`udf_schema`
NCA: `configs` config_key=`udf_schema` (stored as raw JSON string)

```sql
WITH monolith_settings AS (
    SELECT entity_id, value AS udf_schema
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'udf_schema'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
),
nca_configs AS (
    SELECT module_id,
        MAX(CASE WHEN config_key = 'udf_schema' THEN value END) AS udf_schema
    FROM realtime_prod_no_code_apps.configs
    WHERE config_key = 'udf_schema'
      AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    GROUP BY module_id
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.udf_schema    AS monolith_udf_schema,
    nc.udf_schema    AS nca_udf_schema
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
LEFT JOIN monolith_settings ms ON pl.id = ms.entity_id
LEFT JOIN nca_configs nc ON pl.id = nc.module_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND COALESCE(ms.udf_schema, '') != COALESCE(nc.udf_schema, '')
ORDER BY pl.merchant_id;
```

---

## 2. enable_receipt

Monolith: `settings` key=`enable_receipt`
NCA: `configs` config_key=`base_config`, `$.enable_receipt`

```sql
WITH monolith_settings AS (
    SELECT entity_id, value AS enable_receipt
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'enable_receipt'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
),
nca_configs AS (
    SELECT module_id,
        MAX(CASE WHEN config_key = 'base_config' THEN value END) AS base_config
    FROM realtime_prod_no_code_apps.configs
    WHERE config_key = 'base_config'
      AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    GROUP BY module_id
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.enable_receipt                                              AS monolith_enable_receipt,
    json_extract_scalar(nc.base_config, '$.enable_receipt')       AS nca_enable_receipt
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
LEFT JOIN monolith_settings ms ON pl.id = ms.entity_id
LEFT JOIN nca_configs nc ON pl.id = nc.module_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  -- Treat monolith "0" same as NCA absent (both = disabled)
  AND COALESCE(ms.enable_receipt, '0') != COALESCE(json_extract_scalar(nc.base_config, '$.enable_receipt'), '0')
ORDER BY pl.merchant_id;
```

---

## 3. enable_custom_serial_number

Monolith: `settings` key=`enable_custom_serial_number`
NCA: `configs` config_key=`receipt_config`, `$.enable_custom_serial_number`

```sql
WITH monolith_settings AS (
    SELECT entity_id, value AS enable_custom_serial
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'enable_custom_serial_number'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
),
nca_configs AS (
    SELECT module_id,
        MAX(CASE WHEN config_key = 'receipt_config' THEN value END) AS receipt_config
    FROM realtime_prod_no_code_apps.configs
    WHERE config_key = 'receipt_config'
      AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    GROUP BY module_id
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.enable_custom_serial                                                      AS monolith_enable_custom_serial,
    json_extract_scalar(nc.receipt_config, '$.enable_custom_serial_number')      AS nca_enable_custom_serial
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
LEFT JOIN monolith_settings ms ON pl.id = ms.entity_id
LEFT JOIN nca_configs nc ON pl.id = nc.module_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  -- Treat monolith "0" same as NCA absent (both = disabled)
  AND COALESCE(ms.enable_custom_serial, '0') != COALESCE(json_extract_scalar(nc.receipt_config, '$.enable_custom_serial_number'), '0')
ORDER BY pl.merchant_id;
```

---

## 4. selected_udf_field

Monolith: `settings` key=`selected_udf_field`
NCA: `configs` config_key=`receipt_config`, `$.selected_udf_field`

```sql
WITH monolith_settings AS (
    SELECT entity_id, value AS selected_udf_field
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'selected_udf_field'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
),
nca_configs AS (
    SELECT module_id,
        MAX(CASE WHEN config_key = 'receipt_config' THEN value END) AS receipt_config
    FROM realtime_prod_no_code_apps.configs
    WHERE config_key = 'receipt_config'
      AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    GROUP BY module_id
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.selected_udf_field                                              AS monolith_selected_udf_field,
    json_extract_scalar(nc.receipt_config, '$.selected_udf_field')    AS nca_selected_udf_field
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
LEFT JOIN monolith_settings ms ON pl.id = ms.entity_id
LEFT JOIN nca_configs nc ON pl.id = nc.module_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND COALESCE(ms.selected_udf_field, '') != COALESCE(json_extract_scalar(nc.receipt_config, '$.selected_udf_field'), '')
ORDER BY pl.merchant_id;
```

---

## 5. enable_80g_details

Monolith: `settings` key=`enable_80g_details`
NCA: `configs` config_key=`receipt_config`, `$.enable_80g_details`

```sql
WITH monolith_settings AS (
    SELECT entity_id, value AS enable_80g_details
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'enable_80g_details'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
),
nca_configs AS (
    SELECT module_id,
        MAX(CASE WHEN config_key = 'receipt_config' THEN value END) AS receipt_config
    FROM realtime_prod_no_code_apps.configs
    WHERE config_key = 'receipt_config'
      AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    GROUP BY module_id
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.enable_80g_details                                               AS monolith_enable_80g,
    json_extract_scalar(nc.receipt_config, '$.enable_80g_details')      AS nca_enable_80g
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
LEFT JOIN monolith_settings ms ON pl.id = ms.entity_id
LEFT JOIN nca_configs nc ON pl.id = nc.module_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  -- Treat monolith "0" same as NCA absent (both = disabled)
  AND COALESCE(ms.enable_80g_details, '0') != COALESCE(json_extract_scalar(nc.receipt_config, '$.enable_80g_details'), '0')
ORDER BY pl.merchant_id;
```

---

## 6. pp_fb_pixel_tracking_id

Monolith: `settings` key=`pp_fb_pixel_tracking_id`
NCA: `configs` config_key=`tracking_config`, `$.pp_fb_pixel_tracking_id`

```sql
WITH monolith_settings AS (
    SELECT entity_id, value AS fb_pixel
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'pp_fb_pixel_tracking_id'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
),
nca_configs AS (
    SELECT module_id,
        MAX(CASE WHEN config_key = 'tracking_config' THEN value END) AS tracking_config
    FROM realtime_prod_no_code_apps.configs
    WHERE config_key = 'tracking_config'
      AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    GROUP BY module_id
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.fb_pixel                                                                  AS monolith_fb_pixel,
    json_extract_scalar(nc.tracking_config, '$.pp_fb_pixel_tracking_id')         AS nca_fb_pixel
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
LEFT JOIN monolith_settings ms ON pl.id = ms.entity_id
LEFT JOIN nca_configs nc ON pl.id = nc.module_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND ms.fb_pixel IS NOT NULL AND ms.fb_pixel != '' AND ms.fb_pixel != '0'
  AND COALESCE(ms.fb_pixel, '') != COALESCE(json_extract_scalar(nc.tracking_config, '$.pp_fb_pixel_tracking_id'), '')
ORDER BY pl.merchant_id;
```

---

## 7. pp_ga_pixel_tracking_id

Monolith: `settings` key=`pp_ga_pixel_tracking_id`
NCA: `configs` config_key=`tracking_config`, `$.pp_ga_pixel_tracking_id`

```sql
WITH monolith_settings AS (
    SELECT entity_id, value AS ga_pixel
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'pp_ga_pixel_tracking_id'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
),
nca_configs AS (
    SELECT module_id,
        MAX(CASE WHEN config_key = 'tracking_config' THEN value END) AS tracking_config
    FROM realtime_prod_no_code_apps.configs
    WHERE config_key = 'tracking_config'
      AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    GROUP BY module_id
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.ga_pixel                                                                  AS monolith_ga_pixel,
    json_extract_scalar(nc.tracking_config, '$.pp_ga_pixel_tracking_id')         AS nca_ga_pixel
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
LEFT JOIN monolith_settings ms ON pl.id = ms.entity_id
LEFT JOIN nca_configs nc ON pl.id = nc.module_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND ms.ga_pixel IS NOT NULL AND ms.ga_pixel != '' AND ms.ga_pixel != '0'
  AND COALESCE(ms.ga_pixel, '') != COALESCE(json_extract_scalar(nc.tracking_config, '$.pp_ga_pixel_tracking_id'), '')
ORDER BY pl.merchant_id;
```

---

## 8. payment_success_redirect_url

Monolith: `settings` key=`payment_success_redirect_url`
NCA: `configs` config_key=`base_config`, `$.payment_success_redirect_url`

```sql
WITH monolith_settings AS (
    -- Pick the row with the latest created_at per entity — there can be multiple
    -- settings rows for the same key (e.g. after updates), and only the newest matters.
    SELECT entity_id, value AS redirect_url
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'payment_success_redirect_url'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
),
nca_configs AS (
    SELECT module_id,
        MAX(CASE WHEN config_key = 'base_config' THEN value END) AS base_config
    FROM realtime_prod_no_code_apps.configs
    WHERE config_key = 'base_config'
      AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    GROUP BY module_id
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.redirect_url                                                                    AS monolith_redirect_url,
    json_extract_scalar(nc.base_config, '$.payment_success_redirect_url')              AS nca_redirect_url
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
LEFT JOIN monolith_settings ms ON pl.id = ms.entity_id
LEFT JOIN nca_configs nc ON pl.id = nc.module_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND ms.redirect_url IS NOT NULL AND ms.redirect_url != ''
  AND COALESCE(ms.redirect_url, '') != COALESCE(json_extract_scalar(nc.base_config, '$.payment_success_redirect_url'), '')
ORDER BY pl.merchant_id;
```

---

## 9. partner_shiprocket (shiprocket webhook)

Monolith: `settings` key=`partner_webhook_settings.partner_shiprocket`
Value format: plain string `"0"` or `"1"` (NOT a JSON object — verified from datalake).
NCA: `configs` config_key=`webhook_config`, `$.shiprocket_webhook_enabled` (value: `"1"` or `"0"` or absent).

**Note on 0 vs absent:** Monolith `"0"` and NCA field absent both mean disabled.
The query treats absent NCA field as `"0"` to avoid false positives.

```sql
WITH monolith_settings AS (
    -- Value is a plain string "0" or "1" (not JSON).
    SELECT entity_id, value AS shiprocket_enabled
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'partner_webhook_settings.partner_shiprocket'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
),
nca_configs AS (
    SELECT module_id,
        MAX(CASE WHEN config_key = 'webhook_config' THEN value END) AS webhook_config
    FROM realtime_prod_no_code_apps.configs
    WHERE config_key = 'webhook_config'
      AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    GROUP BY module_id
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.shiprocket_enabled                                                           AS monolith_shiprocket_enabled,
    COALESCE(json_extract_scalar(nc.webhook_config, '$.shiprocket_webhook_enabled'), '0') AS nca_shiprocket_enabled
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
LEFT JOIN monolith_settings ms ON pl.id = ms.entity_id
LEFT JOIN nca_configs nc ON pl.id = nc.module_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  -- Treat monolith absent as "0"; treat monolith "0" same as NCA absent
  AND COALESCE(ms.shiprocket_enabled, '0') != COALESCE(json_extract_scalar(nc.webhook_config, '$.shiprocket_webhook_enabled'), '0')
ORDER BY pl.merchant_id;
```

---

## 10. version

Monolith: `settings` key=`version` (value: `'V1'` or `'V2'`; absent = V1)
NCA: `configs` config_key=`base_config`, `$.version` (null = V1)

Note: `version` is NOT user-editable — it's set by monolith during create/update to `V2` (hardcoded in `Core.php`). Pages missing `version` in NCA (migrated before version was added to data migration) will incorrectly show V1 behavior (prepend Email+Phone to udf_schema).

```sql
WITH monolith_settings AS (
    SELECT entity_id, value AS version
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'version'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
),
nca_configs AS (
    SELECT module_id,
        MAX(CASE WHEN config_key = 'base_config' THEN value END) AS base_config
    FROM realtime_prod_no_code_apps.configs
    WHERE config_key = 'base_config'
      AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    GROUP BY module_id
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.version                                                          AS monolith_version,
    json_extract_scalar(nc.base_config, '$.version')                    AS nca_version
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
LEFT JOIN monolith_settings ms ON pl.id = ms.entity_id
LEFT JOIN nca_configs nc ON pl.id = nc.module_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND COALESCE(ms.version, 'V1') != COALESCE(json_extract_scalar(nc.base_config, '$.version'), 'V1')
ORDER BY pl.merchant_id;
```

---

## 11. custom_domain

Monolith: `settings` key=`custom_domain`
NCA: `configs` config_key=`base_config`, `$.custom_domain`

Note: This is a denormalized copy of the domain in `nocode_custom_urls.domain`. The slug/domain query (comparing `custom_urls` tables) is the authoritative check, but this catches cases where the config value drifted independently.

```sql
WITH monolith_settings AS (
    SELECT entity_id, value AS custom_domain
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'custom_domain'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
),
nca_configs AS (
    SELECT module_id,
        MAX(CASE WHEN config_key = 'base_config' THEN value END) AS base_config
    FROM realtime_prod_no_code_apps.configs
    WHERE config_key = 'base_config'
      AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    GROUP BY module_id
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.custom_domain                                                    AS monolith_custom_domain,
    json_extract_scalar(nc.base_config, '$.custom_domain')              AS nca_custom_domain
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
LEFT JOIN monolith_settings ms ON pl.id = ms.entity_id
LEFT JOIN nca_configs nc ON pl.id = nc.module_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND ms.custom_domain IS NOT NULL AND ms.custom_domain != ''
  AND COALESCE(ms.custom_domain, '') != COALESCE(json_extract_scalar(nc.base_config, '$.custom_domain'), '')
ORDER BY pl.merchant_id;
```

---

## 12. image_url_80g and text_80g_12a

Monolith: `settings` keys `image_url_80g` and `text_80g_12a`
NCA: **NOT migrated** — these are merchant-level settings, not page-level configs. NCA stores them on the Settings struct but they are intentionally skipped during data migration and not mapped to any GroupedConfig/config_key.

This query finds pages that have these set in monolith (monolith-only, no NCA comparison).

```sql
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    ms.image_url_80g,
    ms.text_80g_12a
FROM realtime_hudi_api.payment_links pl
JOIN (
    SELECT
        COALESCE(a.entity_id, b.entity_id) AS entity_id,
        a.image_url_80g,
        b.text_80g_12a
    FROM (
        SELECT entity_id, value AS image_url_80g
        FROM (
            SELECT entity_id, value,
                ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
            FROM realtime_hudi_api.settings
            WHERE key = 'image_url_80g'
              AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
        ) ranked WHERE rn = 1
    ) a
    FULL OUTER JOIN (
        SELECT entity_id, value AS text_80g_12a
        FROM (
            SELECT entity_id, value,
                ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
            FROM realtime_hudi_api.settings
            WHERE key = 'text_80g_12a'
              AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
        ) ranked WHERE rn = 1
    ) b ON a.entity_id = b.entity_id
) ms ON pl.id = ms.entity_id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND (ms.image_url_80g IS NOT NULL AND ms.image_url_80g != ''
       OR ms.text_80g_12a IS NOT NULL AND ms.text_80g_12a != '')
ORDER BY pl.merchant_id;
```

---


---


## 15. short_url_mismatch

Monolith: `payment_links.short_url`
NCA: `nocode.short_url`

Finds pages where the stored short URL differs. Common causes: migration didn't copy `short_url`, slug was renamed post-migration, or NCA defaulted to slug instead of the original short code.

```sql
SELECT
    pl.id,
    pl.merchant_id,
    pl.slug,
    pl.status,
    pl.short_url    AS monolith_short_url,
    n.short_url     AS nca_short_url
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND COALESCE(pl.short_url, '') != COALESCE(n.short_url, '')
ORDER BY pl.merchant_id;
```

---

## 16. goal_tracker_mismatch

Monolith: `settings` key=`goal_tracker.tracker_type` (key-value table — `payment_links.settings`
JSON column is not replicated to the datalake)
NCA: `goal_tracker.type` (joined via `nocode_id = payment_link.id`)

Finds pages where `tracker_type` in monolith differs from `type` in NCA's goal_tracker table.

```sql
WITH monolith_tracker AS (
    SELECT entity_id, value AS tracker_type
    FROM (
        SELECT entity_id, value,
            ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY created_at DESC) AS rn
        FROM realtime_hudi_api.settings
        WHERE key = 'goal_tracker.tracker_type'
          AND _is_row_deleted IS NULL AND created_date >= '2012-01-01'
    ) ranked
    WHERE rn = 1
)
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    mt.tracker_type  AS monolith_tracker_type,
    gt.type          AS nca_tracker_type
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
JOIN monolith_tracker mt ON pl.id = mt.entity_id
JOIN realtime_prod_no_code_apps.goal_tracker gt
    ON gt.nocode_id = pl.id
    AND gt._is_row_deleted IS NULL AND gt.created_date >= '2012-01-01'
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND COALESCE(mt.tracker_type, '') != COALESCE(gt.type, '')
ORDER BY pl.merchant_id;
```

---

## 17. payment_page_items_mismatch

Three sub-queries covering the three root causes.

### 15a. Aggregation drift (total_amount_paid / quantity_sold)

Monolith: `payment_page_items.total_amount_paid`, `payment_page_items.quantity_sold`
NCA: `analytics.total_amount` (= total_amount_paid), `analytics.total_units` (= quantity_sold), joined via `module_id = line_item.id`

```sql
WITH nca_item_analytics AS (
    SELECT
        li.nocode_id,
        li.id        AS line_item_id,
        a.total_amount,
        a.total_units
    FROM realtime_prod_no_code_apps.line_items li
    JOIN realtime_prod_no_code_apps.analytics a
        ON a.module_id = li.id
        AND a._is_row_deleted IS NULL AND a.created_date >= '2012-01-01'
    WHERE li._is_row_deleted IS NULL AND li.created_date >= '2012-01-01'
)
SELECT
    pl.id                   AS page_id,
    pl.merchant_id,
    pl.status,
    ppi.id                  AS monolith_item_id,
    ppi.total_amount_paid   AS monolith_total_amount_paid,
    ppi.quantity_sold       AS monolith_quantity_sold,
    na.total_amount         AS nca_total_amount_paid,
    na.total_units          AS nca_quantity_sold
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
JOIN realtime_hudi_api.payment_page_items ppi
    ON ppi.payment_link_id = pl.id
    AND ppi._is_row_deleted IS NULL AND ppi.created_date >= '2012-01-01'
JOIN nca_item_analytics na
    ON na.nocode_id = pl.id
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND (
      COALESCE(CAST(ppi.total_amount_paid AS VARCHAR), '0') != COALESCE(CAST(na.total_amount AS VARCHAR), '0')
      OR COALESCE(CAST(ppi.quantity_sold AS VARCHAR), '0') != COALESCE(CAST(na.total_units AS VARCHAR), '0')
  )
ORDER BY pl.merchant_id;
```

### 15b. Items not linked in NCA (empty line_item data)

Finds pages where monolith `payment_page_items` has an `item_id` but the corresponding NCA `line_items` row has no `catalog_id` (i.e. the item was never linked during migration).

```sql
SELECT
    pl.id           AS page_id,
    pl.merchant_id,
    pl.status,
    ppi.id          AS monolith_ppi_id,
    ppi.item_id     AS monolith_item_id,
    li.id           AS nca_line_item_id,
    li.catalog_id   AS nca_catalog_id
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
JOIN realtime_hudi_api.payment_page_items ppi
    ON ppi.payment_link_id = pl.id
    AND ppi._is_row_deleted IS NULL AND ppi.created_date >= '2012-01-01'
    AND ppi.item_id IS NOT NULL AND ppi.item_id != ''
LEFT JOIN realtime_prod_no_code_apps.line_items li
    ON li.nocode_id = pl.id
    AND li._is_row_deleted IS NULL AND li.created_date >= '2012-01-01'
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND (li.id IS NULL OR li.catalog_id IS NULL OR li.catalog_id = '')
ORDER BY pl.merchant_id;
```

### 15c. Item description missing or different in NCA

Monolith: `payment_page_items.description` (via item join — requires `items` table)
NCA: `line_items.description`

```sql
SELECT
    pl.id           AS page_id,
    pl.merchant_id,
    pl.status,
    ppi.id          AS monolith_ppi_id,
    i.description   AS monolith_description,
    li.id           AS nca_line_item_id,
    li.description  AS nca_description
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
JOIN realtime_hudi_api.payment_page_items ppi
    ON ppi.payment_link_id = pl.id
    AND ppi._is_row_deleted IS NULL AND ppi.created_date >= '2012-01-01'
JOIN realtime_hudi_api.items i
    ON i.id = ppi.item_id
    AND i._is_row_deleted IS NULL AND i.created_date >= '2012-01-01'
    AND i.description IS NOT NULL AND i.description != ''
JOIN realtime_prod_no_code_apps.line_items li
    ON li.nocode_id = pl.id
    AND li._is_row_deleted IS NULL AND li.created_date >= '2012-01-01'
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND COALESCE(i.description, '') != COALESCE(li.description, '')
ORDER BY pl.merchant_id;

---

## 18. line_item_price.amount mismatch (fixed price drift)

**Context:** Category #12 in `018-all-merchants-status-code-mismatches.md` — 39 mismatches of
`amount should be equal to payment page item amount`. NCA validation and monolith validation are
identical in code. Mismatch means NCA's `line_item_prices.amount` has drifted from the monolith's
`items.amount`.

**Key schema difference:**
- Monolith `items.amount`: nullable — `NULL` means custom-amount (no fixed price).
- NCA `line_item_prices.amount`: `BIGINT NOT NULL` — `0` means no fixed price.
- If NCA has `amount > 0` but monolith has `amount IS NULL` → NCA incorrectly enforces a fixed price.
- If NCA has `amount = X` but monolith has `amount = Y` (X ≠ Y) → stale price in NCA.

Monolith: `items.amount` (catalog item fixed price)
NCA: `line_item_prices.amount` (via `line_item_prices.nocode_id = line_items.id`)

```sql
SELECT
    pl.id                   AS page_id,
    pl.merchant_id,
    pl.status,
    ppi.id                  AS monolith_ppi_id,
    i.amount                AS monolith_item_amount,
    li.id                   AS nca_line_item_id,
    lip.amount              AS nca_lip_amount
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
JOIN realtime_hudi_api.payment_page_items ppi
    ON ppi.payment_link_id = pl.id
    AND ppi._is_row_deleted IS NULL AND ppi.created_date >= '2012-01-01'
JOIN realtime_hudi_api.items i
    ON i.id = ppi.item_id
    AND i._is_row_deleted IS NULL AND i.created_date >= '2012-01-01'
JOIN realtime_prod_no_code_apps.line_items li
    ON li.nocode_id = pl.id
    AND li.catalog_id = ppi.item_id
    AND li._is_row_deleted IS NULL AND li.created_date >= '2012-01-01'
JOIN realtime_prod_no_code_apps.line_item_prices lip
    ON lip.nocode_id = li.id
    AND lip._is_row_deleted IS NULL AND lip.created_date >= '2012-01-01'
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND (
      -- NCA has a fixed price but monolith treats it as custom-amount (NULL)
      (i.amount IS NULL AND lip.amount > 0)
      -- OR both have a fixed price but values differ
      OR (i.amount IS NOT NULL AND CAST(i.amount AS BIGINT) != CAST(lip.amount AS BIGINT))
  )
ORDER BY pl.merchant_id, ppi.id;
```

**Targeted check for known affected pages from shadow mode analysis:**

```sql
SELECT
    pl.id                   AS page_id,
    pl.merchant_id,
    ppi.id                  AS monolith_ppi_id,
    i.amount                AS monolith_item_amount,
    lip.amount              AS nca_lip_amount,
    CASE
        WHEN i.amount IS NULL AND lip.amount > 0 THEN 'nca_has_fixed_price_monolith_custom'
        WHEN i.amount IS NOT NULL AND CAST(i.amount AS BIGINT) != CAST(lip.amount AS BIGINT) THEN 'fixed_price_value_drift'
        ELSE 'ok'
    END AS mismatch_type
FROM realtime_hudi_api.payment_links pl
JOIN realtime_hudi_api.payment_page_items ppi ON ppi.payment_link_id = pl.id AND ppi._is_row_deleted IS NULL AND ppi.created_date >= '2012-01-01'
JOIN realtime_hudi_api.items i ON i.id = ppi.item_id AND i._is_row_deleted IS NULL AND i.created_date >= '2012-01-01'
JOIN realtime_prod_no_code_apps.line_items li ON li.nocode_id = pl.id AND li.catalog_id = ppi.item_id AND li._is_row_deleted IS NULL AND li.created_date >= '2012-01-01'
JOIN realtime_prod_no_code_apps.line_item_prices lip ON lip.nocode_id = li.id AND lip._is_row_deleted IS NULL AND lip.created_date >= '2012-01-01'
WHERE pl.id IN ('pl_QUQELFFdCjHZ57', 'pl_RDdOoUSowsRT0B', 'pl_SP8sZYvbYB4D5X', 'pl_STWfXTizcVpcGc',
                'pl_RWqevgIie8QVER', 'pl_RYbgyMLWUidzjV', 'pl_SFAPeLMSaOiyRb', 'pl_QCvgo9DbCXWu39',
                'pl_RY5j7dNAOv1SSR', 'pl_SJH0iOlOOaOksh')
ORDER BY pl.id, ppi.id;
```

---

## 19. line_item_price.min_amount mismatch

**Context:** Category #12 — 205 mismatches of `amount should not be lesser than the payment page
item min amount`. Monolith and NCA code are identical; NCA's `min_amount` is stale.

**Key schema difference:**
- Monolith `payment_page_items.min_amount`: nullable — `NULL` means no minimum.
- NCA `line_item_prices.min_amount`: `BIGINT NOT NULL` — `0` means no minimum.
- If NCA has `min_amount > 0` but monolith has `min_amount IS NULL` → NCA incorrectly enforces a floor.
- If both set but values differ → stale min in NCA.

Monolith: `payment_page_items.min_amount`
NCA: `line_item_prices.min_amount`

```sql
SELECT
    pl.id                   AS page_id,
    pl.merchant_id,
    pl.status,
    ppi.id                  AS monolith_ppi_id,
    ppi.min_amount          AS monolith_min_amount,
    ppi.max_amount          AS monolith_max_amount,
    li.id                   AS nca_line_item_id,
    lip.min_amount          AS nca_min_amount,
    lip.max_amount          AS nca_max_amount,
    CASE
        WHEN ppi.min_amount IS NULL AND lip.min_amount > 0 THEN 'nca_has_min_monolith_none'
        WHEN ppi.min_amount IS NOT NULL AND CAST(ppi.min_amount AS BIGINT) != CAST(lip.min_amount AS BIGINT) THEN 'min_amount_value_drift'
        ELSE 'ok'
    END AS mismatch_type
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
JOIN realtime_hudi_api.payment_page_items ppi
    ON ppi.payment_link_id = pl.id
    AND ppi._is_row_deleted IS NULL AND ppi.created_date >= '2012-01-01'
JOIN realtime_prod_no_code_apps.line_items li
    ON li.nocode_id = pl.id
    AND li.catalog_id = ppi.item_id
    AND li._is_row_deleted IS NULL AND li.created_date >= '2012-01-01'
JOIN realtime_prod_no_code_apps.line_item_prices lip
    ON lip.nocode_id = li.id
    AND lip._is_row_deleted IS NULL AND lip.created_date >= '2012-01-01'
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  AND (
      -- NCA enforces a min floor but monolith has none
      (ppi.min_amount IS NULL AND lip.min_amount > 0)
      -- OR both have a min but values differ
      OR (ppi.min_amount IS NOT NULL AND CAST(ppi.min_amount AS BIGINT) != CAST(lip.min_amount AS BIGINT))
  )
ORDER BY pl.merchant_id, ppi.id;
```

**Targeted check for known affected pages (top pages from shadow mode analysis):**

```sql
SELECT
    pl.id                   AS page_id,
    pl.merchant_id,
    ppi.id                  AS monolith_ppi_id,
    ppi.min_amount          AS monolith_min_amount,
    lip.min_amount          AS nca_min_amount,
    CASE
        WHEN ppi.min_amount IS NULL AND lip.min_amount > 0 THEN 'nca_has_min_monolith_none'
        WHEN ppi.min_amount IS NOT NULL AND CAST(ppi.min_amount AS BIGINT) != CAST(lip.min_amount AS BIGINT) THEN 'min_amount_value_drift'
        ELSE 'ok'
    END AS mismatch_type
FROM realtime_hudi_api.payment_links pl
JOIN realtime_hudi_api.payment_page_items ppi ON ppi.payment_link_id = pl.id AND ppi._is_row_deleted IS NULL AND ppi.created_date >= '2012-01-01'
JOIN realtime_prod_no_code_apps.line_items li ON li.nocode_id = pl.id AND li.catalog_id = ppi.item_id AND li._is_row_deleted IS NULL AND li.created_date >= '2012-01-01'
JOIN realtime_prod_no_code_apps.line_item_prices lip ON lip.nocode_id = li.id AND lip._is_row_deleted IS NULL AND lip.created_date >= '2012-01-01'
WHERE pl.id IN ('pl_RZD1SzmGsOSzQX', 'pl_RDdOoUSowsRT0B', 'pl_SP8sZYvbYB4D5X', 'pl_STWfXTizcVpcGc',
                'pl_RWqevgIie8QVER', 'pl_RYbgyMLWUidzjV', 'pl_SFAPeLMSaOiyRb', 'pl_QCvgo9DbCXWu39',
                'pl_RY5j7dNAOv1SSR', 'pl_SJH0iOlOOaOksh')
ORDER BY pl.id, ppi.id;
```

---

## 20. title_mismatch

Monolith: `payment_links.title`
NCA: `nocode.title`

**Note on whitespace normalization:** 72.6% of raw mismatches are whitespace-only differences —
NCA stores a `\n` where monolith stored multiple spaces (e.g., `"foo  bar"` vs `"foo\nbar"`).
Both sides are normalized with `REGEXP_REPLACE(..., '\s+', ' ')` to collapse all whitespace runs
to a single space before comparing. The remaining 27.4% (~191 pages) are real title changes made
in monolith after migration that weren't synced to NCA — these need a data fix before cutover.

```sql
SELECT
    pl.id,
    pl.merchant_id,
    pl.status,
    pl.title  AS monolith_title,
    n.title   AS nca_title
FROM realtime_hudi_api.payment_links pl
JOIN realtime_prod_no_code_apps.nocode n
    ON pl.id = n.id
    AND n._is_row_deleted IS NULL AND n.created_date >= '2012-01-01'
WHERE pl.view_type = 'page'
  AND pl._is_row_deleted IS NULL
  AND pl.created_date >= '2012-01-01'
  AND pl.merchant_id NOT IN (
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
  -- Normalize whitespace on both sides before comparing to avoid false positives
  -- from NCA storing \n where monolith stored multiple spaces (same content, different encoding).
  AND REGEXP_REPLACE(pl.title, '\s+', ' ') != REGEXP_REPLACE(n.title, '\s+', ' ')
ORDER BY pl.merchant_id;
```
