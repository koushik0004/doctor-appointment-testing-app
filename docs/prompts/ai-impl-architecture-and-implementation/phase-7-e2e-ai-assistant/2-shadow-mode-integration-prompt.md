# Phase 7.2 — Shadow Mode Integration

You are implementing Phase 7.2 of the Doctor Appointment AI Assistant.

## Context

Assume Phases 1–7.1 are complete and frozen.

The project already contains:

- Conversation Manager
- Workflow Engine
- Vector-less RAG
- Prompt Builder
- LLM Generation Orchestrator
- Runtime Activation
- Execution Policy
- Provider Registry
- Provider Adapters
- AIRuntimeFacade (introduced in Phase 7.1)

Do NOT redesign any existing architecture.

Reuse all existing components.

---

## Objective

Implement **Shadow Mode** within the `AIRuntimeFacade`.

The deterministic chatbot **must remain the only user-visible response**.

The LLM should execute internally in parallel for diagnostics and validation only.

Under no circumstances should the LLM response be returned to the frontend.

---

## Functional Requirements

### Runtime Flow

Implement the following execution sequence:

1. Receive the deterministic chatbot response.
2. Return the deterministic response to the user exactly as today.
3. If Shadow Mode is enabled by the existing Runtime Activation / Execution Policy:
   - Invoke the existing Prompt Builder.
   - Execute the existing LLM Generation Orchestrator.
   - Use the configured provider through the existing Provider Registry.
   - Collect runtime diagnostics.
4. Discard the generated LLM response after diagnostics are captured.

### Safety

- Shadow execution must never change business behavior.
- Ignore LLM failures after logging/diagnostics.
- Never interrupt booking, cancellation, confirmation, or knowledge workflows.
- Never modify Workflow Engine logic.
- Never modify Vector-less RAG ownership.
- Never bypass Business APIs.

### Diagnostics

Reuse the project's existing observability models where possible.

Capture information such as:

- Request/correlation ID
- Execution status
- Provider
- Model
- Latency
- Token usage (if available)
- Error information
- Execution duration

Avoid introducing duplicate logging frameworks if existing infrastructure already supports this.

### Feature Control

Use the existing Runtime Activation and Execution Policy introduced in Phase 6.

Do not create a parallel feature-flag system.

### Code Quality

- Keep implementation minimal.
- Maintain provider neutrality.
- Preserve dependency injection.
- Avoid business logic inside the facade.
- Follow existing coding standards and project structure.

### Validation

Confirm:

- Existing chatbot responses remain identical.
- Existing APIs remain unchanged.
- Existing UI remains unchanged.
- Existing tests continue to pass.
- Shadow execution works only when enabled.
- LLM failures never affect production responses.

### Documentation

Update the project's architecture/implementation report with:

- Shadow Mode purpose
- Runtime sequence
- Safety guarantees
- Diagnostics captured
- Rollback strategy
- Modified files
- Validation summary

---

## Deliverables

- Shadow Mode integrated into `AIRuntimeFacade`.
- Existing Prompt Builder connected internally.
- Existing LLM pipeline invoked in parallel.
- Diagnostics captured.
- Deterministic response preserved.
- Updated documentation.
- Summary of modified files.
- Summary of architectural decisions.
- Validation results demonstrating zero user-visible behavior changes.