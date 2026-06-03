# Backend Feature Orchestrator

Goal:

Implement backend features using phase-driven execution.

---

## Prompt Discovery

Scan:

docs/prompts/feature-02-doctor-listing-backend-orchestration.md

Discover:

PHASE * as each section

Sort numerically.

---

## Context Loading

Read:

docs/**/*.md

.ai/project-memory.md

.ai/execution-status.json

backend/app/**

backend/AGENTS.md

---

## Agent Routing

Planning Tasks
→ Planner Agent
→ GPT-5.4 Medium

Implementation Tasks
→ Implementation Agent
→ GPT-5.4 Mini

Validation Tasks
→ Validation Agent
→ GPT-5.4 Mini

Memory Updates
→ Memory Agent
→ GPT-5.4 Mini

Final Review
→ Reviewer Agent
→ GPT-5.4 Medium

---

## Phase Execution

For each feature:

Read phases sequentially.

Never skip phase order.

Execute:

Phase 01

↓

Phase 02

↓

Phase 03

↓

Phase 04

↓

Phase 05

↓

Phase 06

↓

Phase 07

↓

Phase 08

↓

Validation Agent

↓

Memory Agent

After all phases complete:

Reviewer Agent

---

## Completion Rules

Do not trust execution-status.json alone.

Verify:

- files exist
- routes registered
- imports valid
- build succeeds
- APIs reachable

If already implemented:

Skip phase.

---

## Outputs

Update:

.ai/project-memory.md

.ai/execution-status.json

.ai/completion-report.md