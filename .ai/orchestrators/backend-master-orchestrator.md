# Backend Master Orchestrator

INPUT

feature_file=<path>

Example

docs/prompts/backend/feature-03-appointment-booking.md

---

Goal

Implement backend feature using phase-driven execution.

---

Load Context

Read:

.ai/memory/project-memory.md

.ai/memory/execution-status.json

docs/**/*.md

backend/**

backend/AGENTS.md

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

After all phases:

Reviewer Agent

---

Completion Rules

Verify:

- APIs exist
- imports valid
- routes registered
- tests pass
- build succeeds

Do not trust memory files alone.

---

Outputs

Update:

.ai/memory/project-memory.md

.ai/memory/execution-status.json

.ai/memory/completion-report.md