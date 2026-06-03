# Frontend Feature Orchestrator

Goal:

Implement frontend features using prompt-driven execution.

---

## Prompt Discovery

Scan:

docs/prompts/**/*.md

Discover prompt files matching:

feature-{feature-number}-*.md

Sort numerically.

---

## Context Loading

Read:

docs/*.md

Read:

docs/prompts/**/*.md

Read:

src/**

Read:

.ai/project-memory.md

Read:

.ai/execution-status.json

---

## Target UI Design 

Read:

doctors-appointment-multiscreens/*.png
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

## Completion Detection

Do not trust execution-status.json alone.

Verify:

- files exist
- exports exist
- routes wired
- code compiles

If implementation already exists:

SKIP prompt.

---

## Execution Loop

For each prompt:

1. Planner determines status

If complete:
    Skip

If pending:

    Implementation Agent

    ↓

    Validation Agent

    ↓

    Memory Agent

Continue until no pending prompts remain.

---

## Final Stage

Run Reviewer Agent.

Generate:

.ai/completion-report.md

Include:

- completed prompts
- skipped prompts
- modified files
- validation results
- remaining work