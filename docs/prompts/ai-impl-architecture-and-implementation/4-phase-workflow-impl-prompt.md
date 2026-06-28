Goal:
Implement the Workflow Engine for the existing Doctor Appointment AI Assistant.

Background:
The project already contains:
- Reusable AI Chat Widget
- Deterministic Chat Engine
- Intent Detection
- Entity Extraction
- Conversation Manager
- Doctor Search
- Availability Search
- FAQ Engine

Do NOT redesign or replace any existing modules.

The Workflow Engine must become the single business execution layer used by the Conversation Manager.

Responsibilities:
- Execute business workflows.
- Coordinate existing backend services.
- Validate required workflow inputs.
- Track workflow progress.
- Return structured workflow results.
- Never contain AI reasoning logic.
- Never call any LLM.

Initial Workflows to Support:
1. Book Appointment
2. Cancel Appointment
3. Appointment Confirmation
4. Workflow Validation

Workflow Behavior:
- Receive normalized conversation context from the Conversation Manager.
- Determine whether enough information is available.
- If information is missing, return the missing fields instead of executing the workflow.
- When all required information exists, invoke the existing backend services.
- Reuse all current business APIs.
- Do not duplicate booking or cancellation logic.

Required Changes:
- Introduce a WorkflowEngine service.
- Introduce a simple workflow state model.
- Integrate the Conversation Manager with the Workflow Engine.
- Keep existing doctor search, availability search, FAQ, booking help, and cancellation help fully functional.
- Preserve backward compatibility.
- Do not modify existing API endpoints.
- Do not introduce database migrations unless absolutely required.
- Keep the implementation simple and prototype-friendly.

Testing:
- Add tests covering:
  - Successful appointment booking workflow.
  - Missing information detection.
  - Successful cancellation workflow.
  - Regression tests to ensure existing deterministic chat behavior remains unchanged.

Documentation:
Generate:
- docs/reports/feature-10/ai-impl-architecture-and-implementation/phase-03-report.md

The report must include:
- Files added.
- Files modified.
- Workflow architecture summary.
- Integration points.
- Business APIs reused.
- Design decisions.
- Known limitations.
- Suggested next phase.

Out of Scope:
- No LLM integration.
- No Prompt Builder.
- No Vector-less RAG.
- No conversation persistence.
- No database redesign.
- No frontend redesign.