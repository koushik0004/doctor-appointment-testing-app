# FEATURE 2 INTEGRATION PLANNING AGENT

MODE: PLANNING ONLY

STRICT RULES:

* DO NOT modify application source code.
* DO NOT generate implementation code.
* DO NOT create new APIs.
* DO NOT edit FE or BE feature implementation files.
* DO NOT execute integration.
* ONLY perform analysis and planning.

Your responsibility is to prepare a complete Feature 2 Integration Execution Plan.

---

## STEP 1 — Read Project Context

Read and understand:

* AGENTS.md
* project-memory.md
* execution-status.json
* project-context.md
* architecture.md
* frontend-spec.md
* backend-spec.md
* api-spec.md
* db-schema.md

Also read any Feature 2 planning or execution documents that already exist.

---

## STEP 2 — Discover Feature 2 Backend

Identify:

* Feature 2 backend implementation files
* API endpoints
* Request DTOs
* Response DTOs
* Validation logic
* Service layer
* Repository layer
* Database entities
* Pagination model
* Filtering model
* Sorting model
* Error handling

Produce a backend integration inventory.

Document:

* endpoint path
* HTTP method
* request structure
* response structure
* status codes
* authentication requirements

---

## STEP 3 — Discover Feature 2 Frontend

Identify:

* Feature 2 UI screens
* Page components
* Layout components
* Hooks
* API clients
* State management
* Forms
* Filters
* Search
* Pagination
* Table/List rendering
* Loading states
* Error states

Produce a frontend integration inventory.

Document:

* current data source
* mocked data usage
* temporary implementations
* expected API contracts

---

## STEP 4 — Understand Doctor Listing Flow

Analyze the complete doctor listing experience.

Trace:

User Action
↓
UI Components
↓
Hooks
↓
State Management
↓
API Client
↓
Backend Endpoint
↓
Service Layer
↓
Database Layer
↓
Response Mapping
↓
UI Rendering

Create a complete flow map.

---

## STEP 5 — Contract Validation

Compare frontend expectations with backend implementation.

Identify:

### Request Mismatches

* query parameters
* pagination parameters
* filter parameters
* sort parameters
* search parameters

### Response Mismatches

* field names
* nested structures
* enum values
* date formats
* pagination format
* nullability differences

### Business Logic Mismatches

* filtering rules
* sorting behavior
* status handling
* availability handling

---

## STEP 6 — Integration Impact Analysis

Identify all files requiring updates.

For every file provide:

* file path
* reason for modification
* modification category

Categories:

* API Integration
* Data Mapping
* DTO Alignment
* State Management
* UI Rendering
* Error Handling
* Loading State
* Pagination
* Search
* Filtering
* Authentication
* Validation

---

## STEP 7 — Build Execution Plan

Create a detailed execution plan.

Requirements:

* Extremely granular.
* One task = one logical implementation unit.
* Avoid large tasks.
* Avoid ambiguous tasks.
* Avoid multi-purpose tasks.

Structure:

### Phase 1

Contract Alignment

Task 1.1
Task 1.2
Task 1.3

### Phase 2

Frontend API Integration

Task 2.1
Task 2.2
Task 2.3

### Phase 3

Data Mapping

Task 3.1
Task 3.2

### Phase 4

UI Integration

Task 4.1
Task 4.2

### Phase 5

Validation

Task 5.1
Task 5.2

### Phase 6

Testing

Task 6.1
Task 6.2

Every task must contain:

* objective
* files affected
* dependencies
* expected outcome
* validation criteria

---

## STEP 8 — Risk Assessment

Identify:

* high-risk integration points
* API contract risks
* pagination risks
* filtering risks
* data mapping risks
* performance risks

Provide mitigation steps.

---

## STEP 9 — Generate Integration Execution Document

Create:

docs/integration/feature-2-integration-execution-plan.md

Document must contain:

1. Executive Summary
2. Backend Inventory
3. Frontend Inventory
4. Doctor Listing Flow Analysis
5. Contract Gap Analysis
6. File Modification Matrix
7. Detailed Execution Plan
8. Risk Assessment
9. Validation Checklist
10. Rollback Strategy

---

## STEP 10 — Update Tracking Files

Update:

* execution-status.json
* completion-report.md
* project-memory.md

Record:

* Integration planning completed
* No source code modified
* Execution plan generated
* Ready for implementation phase

---

FINAL OUTPUT

Provide:

* summary of findings
* total files identified
* total integration tasks identified
* path of generated execution plan document

STOP AFTER PLANNING.

DO NOT IMPLEMENT ANY CODE.
DO NOT MODIFY APPLICATION LOGIC.
DO NOT START EXECUTION.
