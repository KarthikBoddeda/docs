# Technical Spec: Analytics Fields Cache Update on Payment Capture

**Created:** 2026-01-27  
**Updated:** 2026-01-23  
**Author:** AI Assistant  
**Status:** Draft  
**Related:** `/docs/projects/payment-pages-decomp/tasks/013-response-body-diffs.md`

---

## Problem Statement

Analytics fields in the hosted view response show diffs between Monolith and NCA during dual-write comparison. The root cause is **NOT** a difference in caching behavior - both systems update cache on payment capture.

### Key Finding: Both Systems Update Cache on Payment Capture

| System | Cache Update Trigger | Code Location |
|--------|---------------------|---------------|
| **Monolith** | `$this->updateHostedCache($paymentLink)` | `Core.php:1381` |
| **NCA** | `BuildHostedPayloadAndUpdateCache()` | `payment_page.go:198` |

### The Real Issue: NCA Splitz Gate

NCA has a **splitz experiment gate** before processing payment events:

```go
// payment_page.go:50-54
if !c.shouldExecutePaymentCallback(ctx, req) {
    logger.CtxLog(ctx).Info(trace.PAYMENT_CALLBACK_SPLITZ_CONTROL)
    return nil  // SKIPS processing if not in experiment!
}
```

**If the payment page is NOT in the splitz experiment (`PaymentCallback`), NCA will:**
1. ❌ NOT process the payment event
2. ❌ NOT update analytics in NCA DB
3. ❌ NOT update the hosted cache

**Result:** Monolith cache is updated, NCA cache stays stale → Diff!

---

## Affected Fields

### Goal Tracker Fields (pages_view)
| Field | Location in Response | Diff Count |
|-------|---------------------|------------|
| `collected_amount` | `payment_link.settings.goal_tracker.meta_data.collected_amount` | 1,326 |
| `sold_units` | `payment_link.settings.goal_tracker.meta_data.sold_units` | 1,326 |
| `supporter_count` | `payment_link.settings.goal_tracker.meta_data.supporter_count` | 1,326 |

### Payment Page Item Fields (payment_page_list)
| Field | Location in Response | Diff Count |
|-------|---------------------|------------|
| `quantity_sold` | `items[].payment_page_items[].quantity_sold` | 783 |
| `total_amount_paid` | `items[].payment_page_items[].total_amount_paid` | 783 |

---

## Monolith Code Reference: Cache Update on Payment Capture

### 1. Payment Capture Handler

**File:** `api/app/Models/PaymentLink/Core.php`

```php
// Lines 1369-1383: Payment capture processing
protected function processPaymentPagePaid(Entity $paymentLink, Payment\Entity $payment)
{
    if ($paymentLink->isPaymentPageOnlyPL() === true)
    {
        return;
    }

    $this->doPostPaymentRiskActions($paymentLink, $payment);

    $this->eventPaymentPagePaid($paymentLink, $payment);

    // KEY LINE: Update hosted cache after payment capture
    $this->updateHostedCache($paymentLink);
}
```

### 2. Cache Update Function

**File:** `api/app/Models/PaymentLink/Core.php`

```php
// Lines 4234-4239: Clear and rebuild cache
public function updateHostedCache(Entity $paymentLink)
{
    // Step 1: Clear existing cache
    Entity::clearHostedCacheForPageId($paymentLink->getPublicId());

    // Step 2: Rebuild with fresh data from DB (includes analytics)
    $this->buildHostedCacheAndGet($paymentLink);
}
```

### 3. Cache Build Function (includes fresh analytics)

**File:** `api/app/Models/PaymentLink/Core.php`

```php
// Lines 4246-4254: Build cache from fresh DB data
private function buildHostedCacheAndGet(Entity $paymentLink): array
{
    // serializeForHosted() fetches fresh data from DB including:
    // - goal_tracker analytics (collected_amount, sold_units, supporter_count)
    // - payment_page_item analytics (quantity_sold, total_amount_paid)
    $serialized = (new ViewSerializer($paymentLink))->serializeForHosted();

    $cacheKey = Entity::getHostedCacheKey($paymentLink->getPublicId());

    $this->cache->put($cacheKey, $serialized, Entity::getHostedCacheTTL());

    $this->trace->count(Metric::PAYMENT_PAGE_HOSTED_CACHE_BUILD_COUNT, $paymentLink->getMetricDimensions());
    
    return $serialized;
}
```

### 4. ViewSerializer fetches fresh analytics

**File:** `api/app/Models/PaymentLink/ViewSerializer.php`

```php
// Lines 274-289: Fresh DB fetch for each payment page item
protected function serializePaymentPageItems(array & $paymentLink)
{
    $PPICore = new PaymentPageItem\Core;

    for ($i = 0; $i < count(array_get($paymentLink, Entity::PAYMENT_PAGE_ITEMS, [])); $i++)
    {
        $paymentPageItem = $paymentLink[Entity::PAYMENT_PAGE_ITEMS][$i];

        // FRESH DB FETCH - gets latest quantity_sold, total_amount_paid
        $paymentPageItem = $PPICore->fetch($paymentPageItem[PaymentPageItem\Entity::ID], $this->paymentLink->merchant);

        $paymentPageItem->settings = $paymentPageItem->getSettings();
        $paymentPageItemSerialized = $paymentPageItem->toArrayHosted();

        $paymentPageItemSerialized['quantity_available'] = $paymentPageItem->getQuantityAvailable();

        $this->serializePPItemSettings($paymentPageItemSerialized);
        $paymentLink[Entity::PAYMENT_PAGE_ITEMS][$i] = $paymentPageItemSerialized;
    }
}

// Lines 474-492: Fresh DB fetch for goal tracker analytics
protected function populateDonationGoalTrackerWithAdditionalKeys(array & $settings): void
{
    // getComputedSettings() reads from DB - includes fresh analytics
    $computedSettings = $this->paymentLink->getComputedSettings()->toArray();
    $metaData = array_get($computedSettings, Entity::GOAL_TRACKER.'.'.Entity::META_DATA, []);
    $goalTrackerMetaData = array_get($settings, Entity::GOAL_TRACKER.'.'.Entity::META_DATA, []);

    if (empty($goalTrackerMetaData) === true)
    {
        return;
    }

    // Fresh values from DB
    $collectedAmount = (string) array_get($metaData, Entity::COLLECTED_AMOUNT, 0);
    $supporterCount  = (string) array_get($metaData, Entity::SUPPORTER_COUNT, 0);
    $soldUnits       = (string) array_get($metaData, Entity::SOLD_UNITS, 0);

    $settings[Entity::GOAL_TRACKER][Entity::META_DATA][Entity::COLLECTED_AMOUNT] = $collectedAmount;
    $settings[Entity::GOAL_TRACKER][Entity::META_DATA][Entity::SUPPORTER_COUNT]  = $supporterCount;
    $settings[Entity::GOAL_TRACKER][Entity::META_DATA][Entity::SOLD_UNITS]       = $soldUnits;
}
```

---

## NCA Code Reference: Cache Update on Payment Capture

### 1. Payment Event Handler

**File:** `internal/modules/payments/payment_page.go`

```go
// Lines 30-54: Payment event handling with splitz gate
func (c *Core) HandleNoCodePaymentEvent(ctx context.Context, source string, req *PaymentRequest) errors.IError {

    logger.CtxLog(ctx).Infow(trace.NOCODE_PAYMENT_EVENT_RECEIVED, map[string]interface{}{
        "productId":     req.Order.ProductId,
        "productType":   req.Order.ProductType,
        "source":        source,
        "paymentStatus": req.Status,
        "paymentId":     req.GetId(),
        "orderId":       req.Order.GetID(),
    })

    if req.Order.ProductType != constants.ProductTypePaymentPage.ToString() {
        return nil
    }

    // ⚠️ SPLITZ GATE - If not in experiment, NCA skips processing!
    if !c.shouldExecutePaymentCallback(ctx, req) {
        logger.CtxLog(ctx).Info(trace.PAYMENT_CALLBACK_SPLITZ_CONTROL)
        return nil  // EXITS HERE - no cache update!
    }

    // ... processing continues only if splitz allows ...
}
```

### 2. Splitz Check Function

**File:** `internal/modules/payments/payment_page.go`

```go
// Lines 353-375: Splitz experiment check
func (c *Core) shouldExecutePaymentCallback(ctx context.Context, req *PaymentRequest) bool {
    uniqueId, _ := uniqueid.New()
    request := splitz.Request{
        Id: uniqueId,
        RequestData: map[string]string{
            constants.ProductIdKey: req.Order.ProductId,
        },
    }

    splitzResponse, err := c.clients.GetSplitz().GetVariant(
        ctx,
        app.Config.Experiments.PaymentCallback,  // Experiment name
        request,
    )
    if err != nil {
        logger.CtxLog(ctx).Errorw(trace.PAYMENT_CALLBACK_SPLITZ_ERROR, ...)
        return false  // On error, skip processing
    }
    return splitzResponse != nil && splitzResponse.Name == splitz.SplitzVariantOn
}
```

### 3. Cache Update After Analytics Update

**File:** `internal/modules/payments/payment_page.go`

```go
// Lines 119-198: After analytics update, cache is rebuilt
err = c.repo.Transaction(ctx, func(ctx context.Context) errors.IError {
    // ... update line item analytics ...
    // ... update goal tracker analytics ...
    err = c.updateLineItemAndNocodeAnalytics(ctx, req, ppEntity, orderLineItems, &merchantDetails)
    if err != nil {
        return err
    }

    // ... update goal tracker ...
    if ppEntity.GoalTracker != nil {
        err = c.updateGoalTrackerOnPaymentCapture(ctx, ppEntity, orderLineItems)
    }

    return nil
})

if err != nil {
    return err
}

// KEY LINE: Update hosted cache with fresh analytics
_ = c.paymentPageModule.GetCore().BuildHostedPayloadAndUpdateCache(ctx, ppEntity, merchantDetails, merchantFeatures, orgFeatures)
```

---

## Root Cause Analysis

### Why Diffs Occur

| Scenario | Monolith | NCA | Result |
|----------|----------|-----|--------|
| Payment captured, NCA in splitz experiment | Cache updated ✅ | Cache updated ✅ | **No diff** |
| Payment captured, NCA NOT in experiment | Cache updated ✅ | Cache NOT updated ❌ | **DIFF** |
| Splitz error occurs | Cache updated ✅ | Cache NOT updated ❌ | **DIFF** |

### The Fix

**Ensure the `PaymentCallback` splitz experiment is enabled at 100% for all payment pages being validated.**

This will ensure:
1. NCA receives and processes all payment events
2. NCA updates analytics in DB
3. NCA updates hosted cache
4. Both caches have identical data → No diffs

---

## Proposed Solution

### Option A: Enable Splitz Experiment at 100% (Recommended)

1. **Verify current splitz configuration** for `PaymentCallback` experiment
2. **Set variant to 100% ON** for all payment pages
3. **Monitor logs** for `PAYMENT_CALLBACK_SPLITZ_CONTROL` (should be 0)
4. **Re-run diff analysis** to confirm diffs are resolved

**Pros:**
- No code changes required
- Identical behavior to monolith
- All analytics synced

**Cons:**
- Need splitz access/permissions

### Option B: Remove Splitz Gate (Code Change)

Remove the splitz check so NCA always processes payment events:

```go
// BEFORE:
if !c.shouldExecutePaymentCallback(ctx, req) {
    logger.CtxLog(ctx).Info(trace.PAYMENT_CALLBACK_SPLITZ_CONTROL)
    return nil
}

// AFTER: Remove these lines entirely
```

**Pros:**
- Guaranteed cache updates
- No dependency on splitz service

**Cons:**
- May have unintended consequences if splitz was intentionally gating
- Need to understand why splitz was added

### Option C: Skip Analytics in Diff Checker (Temporary Workaround)

Add analytics fields to diff checker skip list:

**File:** `internal/modules/diff_checker/configs.go`

```go
var PagesViewSkipPaths = []string{
    // ... existing skips ...
    "/payment_link/settings/goal_tracker/meta_data/collected_amount",
    "/payment_link/settings/goal_tracker/meta_data/sold_units",
    "/payment_link/settings/goal_tracker/meta_data/supporter_count",
}

var PaymentPageListSkipPaths = []string{
    // ... existing skips ...
    "/items/*/payment_page_items/*/quantity_sold",
    "/items/*/payment_page_items/*/total_amount_paid",
}
```

**Pros:**
- Quick fix for diff noise
- No risk to production

**Cons:**
- Hides real issue
- Doesn't fix the underlying problem
- NCA analytics may be stale

---

## Recommendation

1. **Short-term (Decomp validation):** Use **Option C** (skip in diff checker) to proceed with validation
2. **Medium-term:** Investigate and implement **Option A** (enable splitz 100%)
3. **Long-term:** Consider **Option B** (remove splitz) if the experiment is no longer needed

---

## Verification Steps

### Step 1: Check Current Splitz State

Search Coralogix for:
```
"PAYMENT_CALLBACK_SPLITZ_CONTROL" AND application="no-code-apps"
```

If you see many hits → splitz is blocking NCA from processing payments.

### Step 2: Check Splitz Configuration

Verify the `PaymentCallback` experiment configuration in splitz dashboard.

### Step 3: After Fix

Run diff analysis and verify:
- No more `collected_amount`, `sold_units`, `supporter_count` diffs
- No more `quantity_sold`, `total_amount_paid` diffs

---

## Files Reference

| System | File | Purpose |
|--------|------|---------|
| **Monolith** | `api/app/Models/PaymentLink/Core.php` | Payment capture → cache update |
| **Monolith** | `api/app/Models/PaymentLink/ViewSerializer.php` | Fresh analytics fetch during cache build |
| **NCA** | `internal/modules/payments/payment_page.go` | Payment event handler with splitz gate |
| **NCA** | `internal/modules/payment_page/core.go` | Cache build function |

---

## Appendix: Cache Keys (Separate Instances)

Even with both systems updating cache on payment capture, they use **separate cache instances**:

| System | Cache Key Format | TTL |
|--------|-----------------|-----|
| **Monolith** | `NOCODE:payment_link:serialize_pp:{id}` | 1 hour |
| **NCA** | `nca_{mode}:payment_page:{id}:hosted` | 1 hour |

This means even if both update at the same time, tiny timing differences can still cause diffs. The splitz gate is the primary issue, but separate caches contribute to edge cases.
