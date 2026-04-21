# SLIT (Service Level Integration Test) Reference Guide for Merchants-Risk

## Table of Contents
1. [Overview](#overview)
2. [What is SLIT?](#what-is-slit)
3. [Architecture & How SLITs Work](#architecture--how-slits-work)
4. [Test Structure](#test-structure)
5. [Test Case Patterns](#test-case-patterns)
6. [Validation Patterns](#validation-patterns)
7. [Mock Patterns](#mock-patterns)
8. [Common Helper Functions](#common-helper-functions)
9. [Best Practices](#best-practices)
10. [Quick Start Template](#quick-start-template)
11. [Running Tests](#running-tests)
12. [Troubleshooting](#troubleshooting)

---

## Overview

**SLIT (Service Level Integration Tests)** are integration tests that validate the functionality of application APIs when all external dependencies are mocked. These tests run against deployed application pods in devstack environments.

### Key Characteristics
- Tests run against **real deployed services** in devstack
- **External services are mocked** via test case IDs or mock framework
- Tests validate **end-to-end API behavior**
- Uses **testify/suite** for test organization
- Uses **ITF (Integration Test Framework)** for infrastructure
- Tests can validate **database state** through entity fetch APIs

---

## What is SLIT?

**Service Level Integration Tests** test the functionality of your Application and its APIs when everything outside the application (other services on which your APIs depend) are mocked.

### Benefits
- ✅ Fast feedback on API changes
- ✅ Validates integration between components
- ✅ Tests real HTTP requests/responses
- ✅ Validates database persistence
- ✅ No need for actual external services
- ✅ Isolated test environment

---

## Architecture & How SLITs Work

### CI/CD Flow

```
Pull Request → GitHub Action → Rundeck/Argo Workflow
    ↓
1. Clone secrets of required dependencies
2. Deploy application Pods in devstack
3. Deploy SLIT Job to test application
4. Run SLIT tests against deployed pods
```

### Components

1. **ITF Suite** (`github.com/razorpay/goutils/itf`) - Test framework
2. **Mock Dependency** - Mock external services (varies by service)
3. **Test Spec** - Test specification structure
4. **Call Service** (`goutils/itf/utilities/callservice`) - HTTP client for tests

### How It Works

1. Application is deployed to devstack with SLIT environment configuration
2. External services are mocked via:
   - Test case IDs in headers (`X-RZP-TESTCASE-ID`)
   - Mock services in devstack
   - Configuration-based mocking
3. Tests make HTTP requests to deployed pods
4. Tests validate responses and database state

---

## Test Structure

### Directory Organization

```
slit/
├── common/                    # Shared utilities and modules
│   ├── utils.go              # Common utility functions
│   ├── request_helpers.go    # Request preparation helpers
│   └── validation_helpers.go  # Validation helpers
├── tests_<feature>/           # Feature-specific tests
│   ├── setup_<feature>_suite_test.go
│   ├── <feature>_positive_test.go
│   └── <feature>_negative_test.go
└── testdata/                 # Test data and fixtures
    └── <feature>_testdata.go
```

### Suite Structure

```go
package tests_<feature>

import (
    "testing"
    "github.com/razorpay/goutils/itf"
    "github.com/razorpay/merchants-risk/slit"
    "github.com/stretchr/testify/suite"
)

// <Feature>Suite extends base MerchantsRiskSuite
type <Feature>Suite struct {
    slit.MerchantsRiskSuite
}

// SetupSuite initializes the suite
func (s *<Feature>Suite) SetupSuite() {
    s.Suite.SetupSuite()
    // Custom setup code here
    // Example: Seed test data, setup mocks, etc.
}

// TearDownSuite runs after all tests
func (s *<Feature>Suite) TearDownSuite() {
    // Cleanup logic if needed
}

// Test<Feature>Suite runs the suite
func Test<Feature>Suite(t *testing.T) {
    // Optional: Override devstack label for local testing
    // callservice.OverrideDevstackLabel("your-label")
    
    suite.Run(t, &<Feature>Suite{
        slit.MerchantsRiskSuite{
            Suite: itf.NewSuite(itf.WithPriority(itf.PriorityP0)),
        },
    })
}
```

### File Naming Convention
- `setup_<feature>_suite_test.go` - Suite setup and shared test data
- `<feature>_positive_test.go` - Success scenarios
- `<feature>_negative_test.go` - Failure scenarios
- `<feature>_validation_test.go` - Input validation tests

---

## Test Case Patterns

### Test Function Naming Convention

```
Test[Feature][Scenario][ExpectedResult]
```

**Examples:**
- `TestQueryAlertCreateSuccess` - Success scenario
- `TestQueryAlertValidationInvalidMerchantID` - Validation failure
- `TestQueryAlertExternalService4XX` - External service error (4XX)
- `TestQueryAlertExternalService5XX` - External service error (5XX)

### Basic Test Function Structure

```go
func (s *<Feature>Suite) Test<Feature><Scenario>Success() {
    // ============================================
    // STEP 1: Setup Test Data
    // ============================================
    log.Printf("Starting test: Test<Feature><Scenario>Success")
    
    merchantID := "test_merchant_id"
    requestData := map[string]interface{}{
        "merchant_id": merchantID,
        "field1":      "value1",
        // ... other fields
    }
    
    // ============================================
    // STEP 2: Prepare Request
    // ============================================
    resp, err := callservice.CallService(callservice.RequestParams{
        ServiceName: callservice.Services.MerchantsRiskTest,
        AuthType:    callservice.Authorization.MerchantsRiskTestApiUserAuth,
        Method:      http.MethodPost,
        Path:        "/v1/your-endpoint",
        RequestBody: requestData,
        CustomHeaders: map[string]string{
            "X-RZP-TESTCASE-ID": "OPTIONAL_TEST_CASE_ID", // For mocking
        },
    })
    
    // ============================================
    // STEP 3: Validate HTTP Response
    // ============================================
    assert.Nil(s.T(), err, "Service call should not fail")
    assert.Equal(s.T(), http.StatusOK, resp.StatusCode, 
        "Response should be 200 OK")
    
    // ============================================
    // STEP 4: Parse and Validate Response Body
    // ============================================
    respBody := make(map[string]interface{})
    byteBody, _ := io.ReadAll(resp.Body)
    json.Unmarshal(byteBody, &respBody)
    
    assert.NotNil(s.T(), respBody["data"], "Response should contain data")
    assert.Equal(s.T(), "expected_value", respBody["data"].(map[string]interface{})["field"])
    
    // ============================================
    // STEP 5: Validate Database State (if applicable)
    // ============================================
    // Fetch entity and validate persistence
    fetchResp, fetchErr := callservice.CallService(callservice.RequestParams{
        ServiceName: callservice.Services.MerchantsRiskTest,
        AuthType:    callservice.Authorization.MerchantsRiskTestApiUserAuth,
        Method:      http.MethodGet,
        Path:        fmt.Sprintf("/v1/entities/%s", entityID),
    })
    
    assert.Nil(s.T(), fetchErr)
    assert.Equal(s.T(), http.StatusOK, fetchResp.StatusCode)
    
    log.Printf("Test completed successfully: Test<Feature><Scenario>Success")
}
```

### Request Body Patterns

**Shared Request Maps:**
- Define reusable request maps as package-level variables
- Use descriptive names: `QueryAlertReqMap`, `QueryAlertReqMapInvalid`, etc.
- Group related requests together

```go
var QueryAlertReqMap = map[string]interface{}{
    "merchant_id": "test_merchant_id",
    "query":       "SELECT * FROM merchants",
    "alert_type":  "risk_score",
    "threshold":   0.8,
}

// Variant for specific scenarios
var QueryAlertReqMapInvalid = map[string]interface{}{
    "merchant_id": "",  // Invalid: empty merchant ID
    "query":       "SELECT * FROM merchants",
    "alert_type":  "risk_score",
    "threshold":   0.8,
}
```

---

## Validation Patterns

### Status Code Validation

```go
// Success
assert.Equal(s.T(), http.StatusOK, resp.StatusCode)

// Client Error
assert.Equal(s.T(), http.StatusBadRequest, resp.StatusCode)

// Server Error
assert.Equal(s.T(), http.StatusInternalServerError, resp.StatusCode)

// Not Found
assert.Equal(s.T(), http.StatusNotFound, resp.StatusCode)
```

### Error Response Validation

Error responses typically have `error` and `internal` fields:

```go
respBody := make(map[string]interface{})
byteBody, _ := io.ReadAll(resp.Body)
json.Unmarshal(byteBody, &respBody)

respBodyError := respBody["error"].(map[string]interface{})
respBodyInternal := respBody["internal"].(map[string]interface{})

assert.NotNil(s.T(), respBodyError)
assert.NotNil(s.T(), respBodyInternal)
assert.Equal(s.T(), "BAD_REQUEST_ERROR", respBodyError["code"])
assert.Equal(s.T(), "BAD_REQUEST_INVALID_MERCHANT_ID", respBodyInternal["code"])
```

### Response Structure Validation

```go
// Check field existence
assert.NotNil(s.T(), respBody["data"])

// Pattern matching (e.g., ID format)
assert.Regexp(s.T(), regexp.MustCompile(`^[a-zA-Z0-9_]+$`), respBody["id"])

// Nested field access
if data, ok := respBody["data"].(map[string]interface{}); ok {
    assert.NotEmpty(s.T(), data["field"])
    assert.Equal(s.T(), "expected_value", data["field"])
}

// Array validation
if items, ok := respBody["items"].([]interface{}); ok {
    assert.Greater(s.T(), len(items), 0, "Items array should not be empty")
}
```

### Field Value Validation

```go
// Exact match
assert.Equal(s.T(), "expected_value", respBody["field"])

// Nil check
assert.Nil(s.T(), respBody["error"])

// Type assertions
if value, ok := respBody["numeric_field"].(float64); ok {
    assert.Equal(s.T(), float64(100), value)
}
```

---

## Mock Patterns

### Test Case ID Header

The `X-RZP-TESTCASE-ID` header controls mock responses from external services.

**How it works:**
1. Test sets `X-RZP-TESTCASE-ID` header in request
2. Middleware extracts header and adds to context
3. Context propagates to downstream service calls
4. Mock services return responses based on test case ID

### Mock Scenarios

**Success Scenarios (2XX):**
```go
// No test case ID = default success mock
resp, _ := callservice.CallService(callservice.RequestParams{
    // ... no X-RZP-TESTCASE-ID header
})
```

**Error Scenarios (4XX/5XX):**
```go
resp, _ := callservice.CallService(callservice.RequestParams{
    CustomHeaders: map[string]string{
        "X-RZP-TESTCASE-ID": "EXTERNAL_SERVICE_4XX", // Triggers 4XX mock
    },
})
```

### Common Test Case IDs

| Test Case ID | Purpose | Expected Response |
|-------------|---------|-------------------|
| `EXTERNAL_SERVICE_4XX` | External service returns 4XX | 400 Bad Request |
| `EXTERNAL_SERVICE_5XX` | External service returns 5XX | 500 Internal Server Error |
| `EXTERNAL_SERVICE_TIMEOUT` | External service timeout | 500 Internal Server Error |
| `EXTERNAL_SERVICE_INVALID_RESPONSE` | Invalid response format | 500 Internal Server Error |

### Mock Pattern Examples

**External Service Mock:**
```go
// Success
func (s *<Feature>Suite) Test<Feature>ExternalService2XX() {
    resp, _ := callservice.CallService(callservice.RequestParams{
        // No test case ID = success
    })
    assert.Equal(s.T(), http.StatusOK, resp.StatusCode)
}

// 4XX Error
func (s *<Feature>Suite) Test<Feature>ExternalService4XX() {
    resp, _ := callservice.CallService(callservice.RequestParams{
        CustomHeaders: map[string]string{
            "X-RZP-TESTCASE-ID": "EXTERNAL_SERVICE_4XX",
        },
    })
    assert.Equal(s.T(), http.StatusBadRequest, resp.StatusCode)
}

// 5XX Error
func (s *<Feature>Suite) Test<Feature>ExternalService5XX() {
    resp, _ := callservice.CallService(callservice.RequestParams{
        CustomHeaders: map[string]string{
            "X-RZP-TESTCASE-ID": "EXTERNAL_SERVICE_5XX",
        },
    })
    assert.Equal(s.T(), http.StatusInternalServerError, resp.StatusCode)
}
```

---

## Common Helper Functions

### Request Helpers

```go
// Prepare request with default values
func PrepareDefaultRequest(merchantID string, additionalFields map[string]interface{}) map[string]interface{}

// Prepare invalid request for negative tests
func PrepareInvalidRequest(baseRequest map[string]interface{}, invalidField string, invalidValue interface{}) map[string]interface{}
```

### Validation Helpers

```go
// Parse response body
func ParseResponseBody(resp *http.Response) (map[string]interface{}, error)

// Extract error from response
func ExtractErrorFromResponse(respBody map[string]interface{}) (map[string]interface{}, map[string]interface{})

// Validate entity in database
func ValidateEntityExists(entityType string, entityID string, merchantID string) (map[string]interface{}, error)
```

### Test Data Helpers

```go
// Generate random merchant ID
func RandomMerchantID() string

// Generate random entity ID
func RandomEntityID() string

// Get test merchant ID
func GetTestMerchantID() string
```

---

## Best Practices

### 1. Test Organization
- ✅ **Group related tests** in separate files (validation, positive, negative)
- ✅ **Use descriptive test names** that clearly indicate scenario and expected result
- ✅ **Keep setup_test.go** for suite setup and shared request maps
- ✅ **Separate test data** into `testdata/` package

### 2. Request Maps
- ✅ **Define reusable request maps** as package-level variables
- ✅ **Use descriptive names** indicating the scenario
- ✅ **Create variants** by copying and modifying base maps

### 3. Assertions
- ✅ **Always check HTTP status code** first
- ✅ **Validate error structure** (error.code and internal.code) for failures
- ✅ **Use regex for pattern matching** (e.g., ID formats)
- ✅ **Check nested fields** safely with type assertions
- ✅ **Include context in assertion messages**

### 4. Mock Usage
- ✅ **Document test case IDs** used for mocking
- ✅ **Test both success and failure** scenarios for external services
- ✅ **Use consistent naming** for test case IDs

### 5. Error Handling
- ✅ **Always parse response body** even for errors
- ✅ **Validate both error and internal** error codes
- ✅ **Check for nil before accessing** nested fields

### 6. Test Coverage
- ✅ **Success scenarios** - Happy path
- ✅ **Validation failures** - Invalid inputs
- ✅ **External service errors** - 4XX and 5XX from dependencies
- ✅ **Edge cases** - Missing fields, wrong formats, etc.
- ✅ **Database state** - Validate persistence

### 7. Logging
- ✅ **Add logging at each major step** for debugging
- ✅ **Log important values** (IDs, statuses, etc.)
- ✅ **Include context in log messages**

### 8. Test Priority
- ✅ **P0**: Critical path tests (happy path, main flows)
- ✅ **P1**: Important edge cases
- ✅ **P2**: Less common scenarios
- ✅ **P3**: Rare edge cases

---

## Quick Start Template

### Step 1: Create Test Suite File

**File:** `slit/tests_<feature>/setup_<feature>_suite_test.go`

```go
package tests_<feature>

import (
    "testing"
    "github.com/razorpay/goutils/itf"
    "github.com/razorpay/merchants-risk/slit"
    "github.com/stretchr/testify/suite"
)

type <Feature>Suite struct {
    slit.MerchantsRiskSuite
}

func Test<Feature>Suite(t *testing.T) {
    suite.Run(t, &<Feature>Suite{
        slit.MerchantsRiskSuite{
            Suite: itf.NewSuite(itf.WithPriority(itf.PriorityP0)),
        },
    })
}

func (s *<Feature>Suite) SetupSuite() {
    s.Suite.SetupSuite()
}
```

### Step 2: Create Positive Test File

**File:** `slit/tests_<feature>/<feature>_positive_test.go`

```go
package tests_<feature>

import (
    "encoding/json"
    "io"
    "log"
    "net/http"
    "github.com/razorpay/goutils/itf/utilities/callservice"
    "github.com/razorpay/merchants-risk/slit/testdata"
    "github.com/stretchr/testify/assert"
)

func (s *<Feature>Suite) Test<Feature>Success() {
    log.Printf("Starting test: Test<Feature>Success")
    
    // Setup
    merchantID := testdata.GetTestMerchantID()
    requestData := testdata.GetDefaultRequest(merchantID)
    
    // Execute
    resp, err := callservice.CallService(callservice.RequestParams{
        ServiceName: callservice.Services.MerchantsRiskTest,
        AuthType:    callservice.Authorization.MerchantsRiskTestApiUserAuth,
        Method:      http.MethodPost,
        Path:        "/v1/your-endpoint",
        RequestBody: requestData,
    })
    
    // Validate
    assert.Nil(s.T(), err)
    assert.Equal(s.T(), http.StatusOK, resp.StatusCode)
    
    respBody := make(map[string]interface{})
    byteBody, _ := io.ReadAll(resp.Body)
    json.Unmarshal(byteBody, &respBody)
    
    assert.NotNil(s.T(), respBody["data"])
    
    log.Printf("Test completed: Test<Feature>Success")
}
```

### Step 3: Create Test Data File

**File:** `slit/testdata/<feature>_testdata.go`

```go
package testdata

func GetTestMerchantID() string {
    return "test_merchant_id"
}

func GetDefaultRequest(merchantID string) map[string]interface{} {
    return map[string]interface{}{
        "merchant_id": merchantID,
        "field1":      "value1",
    }
}
```

---

## Running Tests

### Prerequisites

1. **Devstack Setup**: Application must be deployed in devstack
2. **Environment Variables**: Required env vars must be set
3. **Secrets**: Required secrets must be available

### Local Testing Setup

#### Step 1: Configure Deployment

Ensure application is deployed with SLIT environment configuration.

#### Step 2: Set Environment Variables

```bash
export DEVSTACK_LABEL=your-label
export MERCHANTS_RISK_SERVICEAUTH_API_PASSWORD=api
```

#### Step 3: Run Tests

```bash
# Run all SLIT tests
go test ./slit/... -args -parallel=false

# Run specific test suite
go test ./slit/tests_<feature>/... -args -parallel=false

# Run with verbose output
go test -v ./slit/... -args -parallel=false

# Run specific test case
go test ./slit/tests_<feature>/... -run Test<Feature>Success -args -parallel=false
```

### IDE Configuration

For running tests from IDE (VS Code, GoLand, etc.):

1. Add environment variables to run configuration:
   - `DEVSTACK_LABEL=your-label`
   - `MERCHANTS_RISK_SERVICEAUTH_API_PASSWORD=api`

2. Add program arguments: `-parallel=false`

### CI/CD

SLITs run automatically on:
- Pull Request creation/update
- Via Rundeck/Argo workflows
- Against deployed devstack pods

---

## Troubleshooting

### Common Issues

#### 1. Test Fails with Connection Error

**Problem**: Cannot connect to service

**Solution**:
- Verify devstack is running
- Check `DEVSTACK_LABEL` is set correctly
- Verify service pods are deployed

#### 2. Mock Not Working

**Problem**: Mock response not being used

**Solution**:
- Verify test case ID is set correctly in headers
- Check middleware is extracting test case ID
- Ensure mock service is configured in devstack

#### 3. Response Mismatch

**Problem**: Expected response doesn't match actual

**Solution**:
- Check JSON formatting in expected response
- Verify field names match exactly
- Use `ParseResponseBody` to inspect actual response

#### 4. Authentication Errors

**Problem**: 401 Unauthorized errors

**Solution**:
- Verify `AuthType` is set correctly
- Check `MERCHANTS_RISK_SERVICEAUTH_API_PASSWORD` is set
- Verify auth credentials are correct

### Debug Tips

1. **Use Verbose Output**:
   ```bash
   go test -v ./slit/... -args -parallel=false
   ```

2. **Inspect Actual Response**:
   ```go
   respBody, _ := ParseResponseBody(resp)
   log.Printf("Response: %+v\n", respBody)
   ```

3. **Add Logging**:
   ```go
   log.Printf("Request: %+v\n", requestData)
   log.Printf("Response Status: %d\n", resp.StatusCode)
   ```

---

## Additional Resources

- [ITF Documentation](https://docs.google.com/document/d/1AkfRWlfmX7lkd45XeD55C99eI6tJruMpQ3dmSzqvEDc/edit#heading=h.s69zvavmq3n0)
- [Testify Suite Documentation](https://github.com/stretchr/testify/tree/master/suite)
- [Go Testing Documentation](https://golang.org/pkg/testing/)

---

## Summary

SLIT tests in merchants-risk follow these key patterns:

1. **Structure**: Testify suite pattern with `MerchantsRiskSuite` embedding
2. **Data**: Organized in `testdata/` package
3. **Mocking**: Use `X-RZP-TESTCASE-ID` header for controlling mocks
4. **Validation**: Comprehensive assertions on status codes, response structure, and database state
5. **Organization**: Group related tests, use descriptive names

Follow this guide to create maintainable, consistent SLIT tests for merchants-risk service!

