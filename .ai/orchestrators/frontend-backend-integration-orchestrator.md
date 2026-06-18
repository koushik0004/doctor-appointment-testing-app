# Frontend Backend Integration Orchestrator

INPUT

feature_file=<path>

Example

docs/prompts/frontend/feature-03-frontend-backend-integration.md

---

Goal

Integrate existing frontend feature with existing backend APIs.

---

Load Context

Read:

docs/**/*.md

.ai/project-memory.md

.ai/execution-status.json

.ai/config/frontend-backend-integration-model-routing.md

frontend/src/**

backend/**

---

Phase Discovery

Read feature_file.

Discover:

# Phase 1
# Phase 2
# Phase 3

...

Sort numerically.

---

Execution Rules

Never execute future phases.

Never skip validation.

Never modify backend contracts.

Never break existing features.

Only integrate existing frontend with existing backend.

---

Execution Loop

For each phase:

Planner Agent

↓

Implementation Agent

↓

Validation Agent

↓

Memory Agent

---

Validation Requirements

Verify:

- TypeScript compile
- ESLint passes
- Existing routes work
- Existing doctor listing works
- Existing filters work
- Existing navigation works

---

Completion Rules

Do not trust memory files alone.

Verify:

- APIs connected
- Loading states implemented
- Error states implemented
- Success states implemented
- Navigation works

---

Final Stage

Reviewer Agent

Generate:

feature-03-integration-review-report.md

---

Outputs

Update:

.ai/project-memory.md

.ai/execution-status.json

.ai/completion-report.md