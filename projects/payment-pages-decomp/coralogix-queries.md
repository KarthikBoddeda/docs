# Coralogix Queries for Payment Pages Decomposition

This file contains useful Coralogix queries for debugging and monitoring the Payment Pages decomposition project.

---

## Index

1. [Status Code Mismatch with Request Context](#1-status-code-mismatch-with-request-context)
2. [Status Code Mismatch - Grouped by Payment Link ID and Error](#2-status-code-mismatch---grouped-by-payment-link-id-and-error)
3. [Shadow Diff Paths - Response Body Diffs](#3-shadow-diff-paths---response-body-diffs)
4. [payment_page_list 5xx Failures](#4-payment_page_list-5xx-failures)
5. [Merchant-wise count of list APIs with title in the request](#5-merchant-wise-count-of-list-apis-with-title-in-the-request)

---

## 1. Status Code Mismatch with Request Context

**Summary:**
- Finds `DIFF_CHECKER_SHADOW_STATUS_CODE_MISMATCH` logs for `dual_write_shadow_read_no_external` mode, excluding context canceled errors
- Joins with `NEW_NCA_REQUEST_RECEIVED` logs to get the original request payload
- Returns route name, status codes, error message, and full logs for debugging

```sql
source logs
/* 1. Filter for DIFF_CHECKER_SHADOW_STATUS_CODE_MISMATCH logs */
| filter $l.applicationname == 'no-code-apps'
| wildfind 'SHADOW_STATUS_CODE_MISMATCH'
| wildfind 'dual_write_shadow_read_no_external'
| filter !$d.log.contains('context canceled')

/* 2. Extract fields from the diff checker log */
| extract $d.log into $d using regexp(/"route_name":"(?<route_name>[A-Za-z_]+)/)
| extract $d.log into $d using regexp(/"monolith_status_code":(?<monolith_code>\d+)/)
| extract $d.log into $d using regexp(/"shadow_status_code":(?<shadow_code>\d+)/)
| extract $d.log into $d using regexp(/"error_message":"(?<error_message>[^"]+)/)

/* 3. Join with the request log (NEW_NCA_REQUEST_RECEIVED) */
| join (
    source logs
    | filter $l.applicationname == 'no-code-apps'
    | filter $d.message == 'NEW_NCA_REQUEST_RECEIVED'
  )
  on left=>$d.task_id == right=>$d.task_id into request_log

/* 4. Display all fields + full logs */
| choose
    $d.route_name as route_name,
    $d.monolith_code as monolith_code,
    $d.shadow_code as shadow_code,
    $d.error_message as error_message,
    $d.task_id as task_id,
    $d.request_id as request_id,
    $d.log as diff_checker_log,
    request_log.log as request_log
```

---

## 2. Status Code Mismatch - Grouped by Payment Link ID and Error

**Summary:**
- Extracts payment link ID from the endpoint URL (e.g., `/v1/pages/pl_XXX/view` or `/v1/payment_pages/pl_XXX/order`)
- Groups by payment_link_id, route_name, and error_message with count
- Useful for identifying which specific payment pages are causing issues

```sql
source logs
/* 1. Filter for DIFF_CHECKER_SHADOW_STATUS_CODE_MISMATCH logs */
| filter $l.applicationname == 'no-code-apps'
| wildfind 'SHADOW_STATUS_CODE_MISMATCH'
| wildfind 'dual_write_shadow_read_no_external'
| filter !$d.log.contains('context canceled')

/* 2. Extract fields from the diff checker log */
| extract $d.log into $d using regexp(/"route_name":"(?<route_name>[A-Za-z_]+)/)
| extract $d.log into $d using regexp(/"monolith_status_code":(?<monolith_code>\d+)/)
| extract $d.log into $d using regexp(/"shadow_status_code":(?<shadow_code>\d+)/)
| extract $d.log into $d using regexp(/"error_message":"(?<error_message>[^"]+)/)

/* 3. Extract payment_link_id from endpoint URL */
/* Matches: /v1/pages/pl_XXX/... or /v1/payment_pages/pl_XXX/... */
| extract $d.log into $d using regexp(/"endpoint":"[^"]*\/pl_(?<payment_link_id>[A-Za-z0-9]+)/)

/* 4. Group by payment_link_id, route, and error */
| groupby $d.payment_link_id as payment_link_id, $d.route_name as route_name, $d.error_message as error_message count() as count
| orderby count desc
```

**Note:** For `payment_page_list` route, there's no specific payment link ID since it's a list operation. Use Query #1 to get full logs for list-related errors.

---

## 3. Shadow Diff Paths - Response Body Diffs



```sql
source logs
/* 1. Filter for DIFF_CHECKER_SHADOW_DIFF_PATHS logs with dual_write proxy state */
| filter $l.applicationname == 'no-code-apps'
| wildfind 'DIFF_CHECKER_SHADOW_DIFF_PATHS'
| wildfind 'dual_write_shadow_read_no_external'

/* 2. Extract fields from the diff checker log */
| extract $d.log into $d using regexp(/"route_name":"(?<route_name>[A-Za-z_]+)/)
| extract $d.log into $d using regexp(/"merchant_id":"(?<merchant_id>[^"]+)/)
| extract $d.log into $d using regexp(/"endpoint":"[^"]*\/pl_(?<payment_link_id>[A-Za-z0-9]+)/)

/* 3. Join with the request log (NEW_NCA_REQUEST_RECEIVED) */
| join (
    source logs
    | filter $l.applicationname == 'no-code-apps'
    | filter $d.message == 'NEW_NCA_REQUEST_RECEIVED'
  )
  on left=>$d.task_id == right=>$d.task_id into request_log

/* 4. Display all fields + full logs */
| choose
    $d.route_name as route_name,
    $d.merchant_id as merchant_id,
    $d.task_id as task_id,
    $d.log as diff_checker_log,
    request_log.log as request_log
| countby $d.route_name, $d.merchant_id
```



### Extracting count of missing/extra pages in NCA

From the `diffs` array in the log, each entry looks like:

- `{"Path":"pages_missing_in_nca","Value1":["pl_SEsByUP0zP1ytg"],"Value2":null,"Type":"count"}` → **count of missing = length of Value1 = 1**
- `{"Path":"pages_extra_in_nca","Value1":null,"Value2":["pl_SEslGtESdhTNfk"],"Type":"count"}` → **count of extra = length of Value2 = 1**

**Extract the array inner content** (so you can derive the count):

- **pages_missing_in_nca count** = length of `Value1` → extract the string inside `Value1`’s brackets; then **count = (number of commas in that string) + 1** (e.g. `"pl_XXX"` → 0 commas → 1; `"pl_A","pl_B"` → 1 comma → 2).
- **pages_extra_in_nca count** = length of `Value2` → same idea using `Value2`.

Add these **extract** steps after step 2 (and before the join) to get the raw value used for counting:

```sql
/* Extract Value1 inner content for pages_missing_in_nca (count = commas in value + 1) */
| extract $d.log into $d using regexp(/"Path":"pages_missing_in_nca","Value1":\[(?<pages_missing_value1>[^\]]*)\]/)

/* Extract Value2 inner content for pages_extra_in_nca (count = commas in value + 1) */
| extract $d.log into $d using regexp(/"Path":"pages_extra_in_nca","Value1":null,"Value2":\[(?<pages_extra_value2>[^\]]*)\]/)
```

Then add to your `choose`:

- `$d.pages_missing_value1 as pages_missing_value1` — e.g. `"pl_SEsByUP0zP1ytg"` → count **1**
- `$d.pages_extra_value2 as pages_extra_value2` — e.g. `"pl_SEslGtESdhTNfk"` → count **1**

If your query language supports string functions, you can compute the count as **`(occurrences of "," in pages_missing_value1) + 1`** (and same for `pages_extra_value2`). Otherwise use the extracted string and apply that formula offline or in a spreadsheet.

**Example: full query with count extraction and request join (from source logs):**

```sql
source logs
| filter $l.applicationname == 'no-code-apps'
| wildfind 'DIFF_CHECKER_SHADOW_DIFF_PATHS'
| wildfind 'dual_write_shadow_read_no_external'
| wildfind 'pages_extra_in_nca'

| extract $d.log into $d using regexp(/"route_name":"(?<route_name>[A-Za-z_]+)/)
| extract $d.log into $d using regexp(/"merchant_id":"(?<merchant_id>[^"]+)/)
| extract $d.log into $d using regexp(/"Path":"pages_missing_in_nca","Value1":\[(?<pages_missing_value1>[^\]]*)\]/)
| extract $d.log into $d using regexp(/"Path":"pages_extra_in_nca","Value1":null,"Value2":\[(?<pages_extra_value2>[^\]]*)\]/)

| join (
    source logs
    | filter $l.applicationname == 'no-code-apps'
    | filter $d.message == 'NEW_NCA_REQUEST_RECEIVED'
  )
  on left=>$d.task_id == right=>$d.task_id into request_log
| extract request_log.log into $d using regexp(/"title":"(?<title>[^"]*)/)

| choose
    $d.route_name as route_name,
    $d.merchant_id as merchant_id,
    $d.task_id as task_id,
    $d.pages_missing_value1 as pages_missing_value1,
    $d.pages_extra_value2 as pages_extra_value2,
    $d.log as diff_checker_log,
    request_log.log as request_log,
    $d.title as title
```

**Count from extracted fields:** `pages_missing_in_nca` count = **(number of commas in `pages_missing_value1`) + 1**; `pages_extra_in_nca` count = **(number of commas in `pages_extra_value2`) + 1**. For a single ID (e.g. `"pl_SEsByUP0zP1ytg"`) there are 0 commas → count = **1**.

### Exact array length and countby title

To **countby title** (or groupby title and sum the per-request array lengths), you need the **exact length of the Value1/Value2 array** as a numeric field. DataPrime supports this using:

1. **multi_regexp** – extracts all matches of a pattern into an array (one match per page ID).
2. **arrayLength** – returns the number of elements in that array.
3. **create** – stores the result in a new field (e.g. `pages_missing_count`).

After that you can **countby $d.title** (number of requests per title) or **groupby $d.title aggregate sum($d.pages_missing_count)** (total missing pages per title).

**Steps (use a dedicated keypath for the array, then create the count from it):**

```sql
/* Extract Value1 inner content first */
| extract $d.log into $d using regexp(/"Path":"pages_missing_in_nca","Value1":\[(?<pages_missing_value1>[^\]]*)\]/)
| extract $d.log into $d using regexp(/"Path":"pages_extra_in_nca","Value1":null,"Value2":\[(?<pages_extra_value2>[^\]]*)\]/)

/* Build array of page IDs from the inner string (matches "pl_XXX" tokens) */
| extract $d.pages_missing_value1 into $d.pages_missing_ids using multi_regexp(e=/pl_[A-Za-z0-9]+/)
| extract $d.pages_extra_value2 into $d.pages_extra_ids using multi_regexp(e=/pl_[A-Za-z0-9]+/)

/* Exact length of each array (numeric) */
| create pages_missing_count from arrayLength($d.pages_missing_ids)
| create pages_extra_count from arrayLength($d.pages_extra_ids)
```

(If the extractor overwrites or the keypath for multi_regexp differs in your environment, use the keypath that actually holds the array, e.g. if it becomes `$d.pages_missing_value1` as an array, use `arrayLength($d.pages_missing_value1)` in `create`.)

**Then either:**

- **Count requests by title:**  
  `| countby $d.title`  
  (one row per title with request count.)

- **Sum of missing/extra page counts by title:**  
  `| groupby $d.title aggregate sum($d.pages_missing_count) as total_missing, sum($d.pages_extra_count) as total_extra`

**Full example: exact length + countby title**

```sql
source logs
| filter $l.applicationname == 'no-code-apps'
| wildfind 'DIFF_CHECKER_SHADOW_DIFF_PATHS'
| wildfind 'dual_write_shadow_read_no_external'

| extract $d.log into $d using regexp(/"route_name":"(?<route_name>[A-Za-z_]+)/)
| extract $d.log into $d using regexp(/"merchant_id":"(?<merchant_id>[^"]+)/)
| extract $d.log into $d using regexp(/"Path":"pages_missing_in_nca","Value1":\[(?<pages_missing_value1>[^\]]*)\]/)
| extract $d.log into $d using regexp(/"Path":"pages_extra_in_nca","Value1":null,"Value2":\[(?<pages_extra_value2>[^\]]*)\]/)

| extract $d.pages_missing_value1 into $d.pages_missing_ids using multi_regexp(e=/pl_[A-Za-z0-9]+/)
| extract $d.pages_extra_value2 into $d.pages_extra_ids using multi_regexp(e=/pl_[A-Za-z0-9]+/)
| create pages_missing_count from arrayLength($d.pages_missing_ids)
| create pages_extra_count from arrayLength($d.pages_extra_ids)

| join (
    source logs
    | filter $l.applicationname == 'no-code-apps'
    | filter $d.message == 'NEW_NCA_REQUEST_RECEIVED'
  )
  on left=>$d.task_id == right=>$d.task_id into request_log
| extract request_log.log into $d using regexp(/"title":"(?<title>[^"]*)/)

| countby $d.title
```

To get **per-title sums of missing/extra counts** instead of request count, replace the last line with:

```sql
| groupby $d.title aggregate sum($d.pages_missing_count) as total_missing, sum($d.pages_extra_count) as total_extra
```

**Note:** If a log line has no `pages_missing_in_nca` (or `pages_extra_in_nca`), the regex extract may leave that field missing; `multi_regexp` on a missing field may yield an empty array, so `arrayLength` would be 0. If your engine treats missing differently, add defaults (e.g. `arrayLength($d.pages_missing_ids ?? [])`) if supported.

---

## 4. payment_page_list 5xx Failures

### Correlate using x-razorpay-request-id from Edge 5xx

**Workflow:**

1. **Get request IDs from Edge 5xx logs**  
   In Coralogix, search for **application: `edge`** and **status 500** (or **http_status 500**). From the edge log, read **`http_x_razorpay_request_id`** (or **`x-razorpay-request-id`**) from the log payload.

2. **Search by that request ID**  
   In Coralogix, run a **keyword search** for that UUID (e.g. `4b4301ad-8c0e-40a9-af13-296b41d366a5`) with no application filter. You get the full request flow:
   - **edge**: the 5xx response (request_uri, status, route_name)
   - **api**: trace logs with the same `x-razorpay-request-id` – including **traceException** with the real exception in **context_str** / **extra**

3. **Pinpoint root cause**  
   In the **api** log where **message** is **"Unhandled critical exception occured"**, the **context_str** (or **extra**) contains the actual exception type and message (e.g. Elasticsearch error body and stack trace).

### Exact root cause found (from logs)

For request **x-razorpay-request-id: 4b4301ad-8c0e-40a9-af13-296b41d366a5**:

- **Edge**: `GET /v1/payment_pages?count=100&skip=10000` → **500**
- **API** (traceException): **Elasticsearch** error:
  - **"Result window is too large, from + size must be less than or equal to: [10000] but was [10100]."**
  - Index: **api_payment_link_live**. The monolith list uses ES with `index.max_result_window` = 10000; this request had **skip=10000 + count=100 = 10100**.
- **Stack**: `PaymentLink/Service.php` → `fetch` → `EsRepository` → `EsClient::search`.

So one concrete cause of payment_page_list 5xx is **deep pagination** (skip + count > 10000) hitting ES’s result window limit. Fix options: cap skip+count in the API or use ES scroll/search_after for deep pagination.

**Coralogix search (by request ID):**  
Keyword search: **`<x-razorpay-request-id from edge 5xx log>`** (e.g. `4b4301ad-8c0e-40a9-af13-296b41d366a5`). No application filter so you see edge + api (and NCA if any) for that request.

---

## 5. Merchant-wise count of list APIs with title in the request

**Summary:**
- Finds `payment_page_list` requests that had a **title** parameter in the request (from DIFF_CHECKER_SHADOW_DIFF_PATHS, so these are list requests that produced a response-body diff)
- Joins with `NEW_NCA_REQUEST_RECEIVED` to get the request payload and extract `title`
- Filters to **top merchants** (from the migration / high-page-count CSV) so we only care about scale for these
- **Count by merchant_id** to get how many list-with-title requests per merchant
- **Use case:** If the count per merchant is on the order of hundreds or low thousands, list API with title filter can be supported without a new index. If it’s very high for some merchants, consider monitoring or a full-text index.

**Top merchants (filter list):** Use the merchant IDs from your CSV (e.g. `25887655_2026_02_11.csv`). Example set (first 26 from that file):

`Ha18e7jHMVjYEb`, `94tLpgbojcR85O`, `Jm5NuHPOevlGjc`, `CWPa3LEGx8jQjj`, `Bz2VyGKL8INUTQ`, `GZ0y9QNgstrY8z`, `EgG77e33eBDpZ4`, `JI4sdkUpF3pwhu`, `HZxddRNg91ugdZ`, `DJy3GWYGs76MnR`, `Mvw4KMeAYSbk06`, `Hb61rVyxlvfhzf`, `IYustKMd3RV7kx`, `GtF1h1XGshTs4m`, `DWcETDH14Y8og7`, `IKjFE6v42nMqNT`, `ELMSeANwMMUmeW`, `J5mbNZ7r6Axk3z`, `Ia00LSXkab6MoK`, `IAgMnZKEziBbVJ`, `IaQV7tLHcUDm4G`, `DQJLIFX9rkEzU2`, `F1HAgg15RSbB0G`, `HCvIiViYUiQhRZ`, `NPgDONnIGkLUCJ`, `F8UFRsOj7MpbLc`

**Query (with top-merchant filter and non-empty title):**

```sql
source logs
/* 1. Filter for DIFF_CHECKER_SHADOW_DIFF_PATHS for list, dual_write */
| filter $l.applicationname == 'no-code-apps'
| wildfind 'DIFF_CHECKER_SHADOW_DIFF_PATHS'
| wildfind 'dual_write_shadow_read_no_external'
| wildfind 'payment_page_list'

/* 2. Extract merchant_id from diff checker log */
| extract $d.log into $d using regexp(/"route_name":"(?<route_name>[A-Za-z_]+)/)
| extract $d.log into $d using regexp(/"merchant_id":"(?<merchant_id>[^"]+)/)

/* 3. Join with request log to get request payload */
| join (
    source logs
    | filter $l.applicationname == 'no-code-apps'
    | filter $d.message == 'NEW_NCA_REQUEST_RECEIVED'
  )
  on left=>$d.task_id == right=>$d.task_id into request_log

/* 4. Extract title from request input (query/body) */
| extract request_log.log into $d using regexp(/"title":"(?<title>[^"]*)"/)

/* 5. Only list requests that had a non-empty title in the request */
| filter $d.title != '' and $d.title != null

/* 6. Restrict to top merchants (from CSV). Use filter with || — do not use matches/regex. */
| filter $d.merchant_id == 'Ha18e7jHMVjYEb' || $d.merchant_id == '94tLpgbojcR85O' || $d.merchant_id == 'Jm5NuHPOevlGjc' || $d.merchant_id == 'CWPa3LEGx8jQjj' || $d.merchant_id == 'Bz2VyGKL8INUTQ' || $d.merchant_id == 'GZ0y9QNgstrY8z' || $d.merchant_id == 'EgG77e33eBDpZ4' || $d.merchant_id == 'JI4sdkUpF3pwhu' || $d.merchant_id == 'HZxddRNg91ugdZ' || $d.merchant_id == 'DJy3GWYGs76MnR' || $d.merchant_id == 'Mvw4KMeAYSbk06' || $d.merchant_id == 'Hb61rVyxlvfhzf' || $d.merchant_id == 'IYustKMd3RV7kx' || $d.merchant_id == 'GtF1h1XGshTs4m' || $d.merchant_id == 'DWcETDH14Y8og7' || $d.merchant_id == 'IKjFE6v42nMqNT' || $d.merchant_id == 'ELMSeANwMMUmeW' || $d.merchant_id == 'J5mbNZ7r6Axk3z' || $d.merchant_id == 'Ia00LSXkab6MoK' || $d.merchant_id == 'IAgMnZKEziBbVJ' || $d.merchant_id == 'IaQV7tLHcUDm4G' || $d.merchant_id == 'DQJLIFX9rkEzU2' || $d.merchant_id == 'F1HAgg15RSbB0G' || $d.merchant_id == 'HCvIiViYUiQhRZ' || $d.merchant_id == 'NPgDONnIGkLUCJ' || $d.merchant_id == 'F8UFRsOj7MpbLc'

/* 7. Merchant-wise count */
| countby $d.merchant_id
| orderby $d.count desc
```

**Without top-merchant filter (all merchants, list-with-title that produced a diff):**

```sql
source logs
| filter $l.applicationname == 'no-code-apps'
| wildfind 'DIFF_CHECKER_SHADOW_DIFF_PATHS'
| wildfind 'dual_write_shadow_read_no_external'
| wildfind 'payment_page_list'
| extract $d.log into $d using regexp(/"route_name":"(?<route_name>[A-Za-z_]+)/)
| extract $d.log into $d using regexp(/"merchant_id":"(?<merchant_id>[^"]+)/)
| join (
    source logs
    | filter $l.applicationname == 'no-code-apps'
    | filter $d.message == 'NEW_NCA_REQUEST_RECEIVED'
  )
  on left=>$d.task_id == right=>$d.task_id into request_log
| extract request_log.log into $d using regexp(/"title":"(?<title>[^"]*)"/)
| filter $d.title != '' and $d.title != null
| countby $d.merchant_id
| orderby $d.count desc
```

**Note:** These queries count **list requests that (1) produced a SHADOW_DIFF_PATHS log** and **(2) had a non-empty title in the request**. So it’s a proxy for “list API with title” volume that actually caused diffs. If the per-merchant count is on the order of hundreds or ~1k, supporting list-with-title without an index is typically fine; if it’s much higher, consider monitoring or a full-text index on `title`.
