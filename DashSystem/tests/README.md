# DashSystem V2 Tests

This directory contains all tests for the DashSystem V2 implementation.

## Test Files

### `test_dash_system_v2.py`
Comprehensive unit tests for DashSystem V2 with MongoDB integration.

**Test Coverage:**
- MongoDB operations (skill insertion, user creation, atomic updates)
- Memory strength calculation with exponential decay
- Prerequisite checking and cascading
- Intelligent question selection algorithm
- Complete learning session flow

**Run:**
```bash
python DashSystem/tests/test_dash_system_v2.py
```

### `test_dash.py`
Legacy test file for original DASH system.

### `test_grade3_breadcrumb_cascade.py`
Integration test for Grade 3 student with breadcrumb cascade logic.

**Tests:**
- Three-state initialization (0.9, 0.0, -1)
- Breadcrumb-based skill relationships
- Cascade updates (positive and negative)
- Grade-specific skill distribution
- Real Khan Academy curriculum data

**Run:**
```bash
python DashSystem/tests/test_grade3_breadcrumb_cascade.py
```

### `test_api_integration.py` ⭐ NEW
End-to-end API integration test - **Run this to verify everything works!**

**Tests:**
- All API endpoints
- User creation with cold start
- Question retrieval
- Answer submission with cascade
- Statistics and profile endpoints
- Complete learning session flow

**Run:**
```bash
# First, start the API server in another terminal:
python DashSystem/dash_api.py

# Then run the test:
python DashSystem/tests/test_api_integration.py
```

## Running All Tests

```bash
# 1. Unit tests (standalone)
python DashSystem/tests/test_dash_system_v2.py

# 2. Grade 3 cascade test (requires database with questions)
python DashSystem/tests/test_grade3_breadcrumb_cascade.py

# 3. API integration test (requires API server running)
python DashSystem/dash_api.py  # In terminal 1
python DashSystem/tests/test_api_integration.py  # In terminal 2
```

## Test Database

Tests use a separate database: `aitutor_test_db`

This ensures production data is not affected during testing.
