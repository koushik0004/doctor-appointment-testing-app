# AI Context Management Workflow

## Purpose

This project uses an AI Context Management workflow to help Codex understand the application efficiently while keeping token usage low.

Instead of making Codex read the entire repository every time a new session starts, a small set of generated context files is maintained. These files summarize the application architecture, current work, reports, and important implementation details.

This approach provides:

* Faster startup for new Codex sessions
* Lower token consumption
* Easier continuation of unfinished work
* Better consistency across multiple development sessions
* Less repeated repository analysis

---

# AI Context Directory

All AI-generated files are stored under:

```text
docs/
└── ai-content/
```

Typical contents:

```text
docs/ai-content/

manifest.yaml
project-map.md
feature-map.md
important-files.md
report-index.md
session-context.md
current-task.md
decision-log.md
```

These files are generated and maintained by the AI skills described below.

---

# Initial Project Setup (One-Time)

When starting a new project or introducing the AI Context workflow into an existing project, execute the following skills **in order**.

---

## Step 1 — ai-context-init

### Prompt
```
$ ai-context-init
Initialize AI context files only. Do not analyze the app yet.
```

### Purpose

Initializes the AI workspace.

### What it does

* Creates `docs/ai-content/`
* Creates all required markdown files if they do not already exist
* Creates `manifest.yaml`
* Preserves any existing files

### Expected Output

```
docs/ai-content/

manifest.yaml
project-map.md
feature-map.md
important-files.md
report-index.md
session-context.md
current-task.md
decision-log.md
```

### Benefits

* Creates the standard AI folder structure
* Ensures all later skills have a consistent destination
* One-time initialization

### Run Frequency

✅ One time only

Run again only if the AI context directory has been deleted.

---

## Step 2 — ai-project-map

### Prompt
```
$ ai-project-map
Analyze the app and generate project-map, feature-map, and important-files only.
```

### Purpose

Analyzes the repository structure.

### Reads

* Frontend
* Backend
* Config files
* Routing
* APIs
* State management
* Database
* Shared modules

### Generates

* project-map.md
* feature-map.md
* important-files.md

### Benefits

* Gives Codex a complete understanding of the project architecture
* Eliminates repeated repository scanning
* Creates feature-to-file mapping

### Run Frequency

✅ Initial setup

✅ Major architecture changes

✅ Large feature additions

❌ Not required after every bug fix

---

## Step 3 — ai-report-index

### Prompt
```
$ ai-report-index
Create report-index only. Do not update other files.
```

### Purpose

Indexes project reports.

### Reads

```
docs/reports/
```

### Generates

```
report-index.md
```

### Important Rule

The full reports are **NOT** copied into AI context.

Only concise summaries are generated.

Each report includes:

* purpose
* summary
* when to read it

### Benefits

* Keeps startup context extremely small
* Full reports are loaded only when necessary
* Significant token savings

### Run Frequency

Run only when:

* new reports are added
* reports are updated
* reports are removed

---

## Step 4 — ai-session-context

### Prompts

```
$ ai-session-context
Generate compact session-context only from existing AI context files.
```

### Purpose

Generates the startup context used in every Codex session.

### Reads

* project-map
* feature-map
* important-files
* report-index
* current-task

### Generates

```
session-context.md
```

### Benefits

Provides Codex with:

* project summary
* architecture summary
* startup guidance
* context loading rules
* report loading rules
* task continuation rules

### Run Frequency

Run after:

* completing a feature
* redesigning a feature
* significant repository changes

Not required for every small bug fix.

---

## Step 5 — agents-md-refresh

### Prompt

```
$ agents-md-refresh
Update AGENTS.md based on docs/ai-content structure only.
```

### Purpose

Synchronizes AGENTS.md with the current AI context workflow.

### Updates

```
AGENTS.md
```

### Benefits

Ensures every new Codex session automatically loads the correct AI context.

### Run Frequency

Run only when:

* AI workflow changes
* AI context structure changes
* new AI context files are introduced

Normally this is a rare operation.

---

# Daily Development Workflow

For normal development, follow this sequence.

```
Open Session

↓

Read AGENTS.md

↓

Read AI Context

↓

Implement Feature

↓

Update current-task

↓

Update session-context (if required)

↓

End Session
```

---

# New Codex Session Prompt

Use this prompt whenever starting a brand-new Codex session.

```
Read AGENTS.md and follow the startup instructions.

Load only the AI context files required for startup.

Do not scan the full repository.

Do not load full reports unless they are required for the current task.

Continue from docs/ai-content/current-task.md.
```

---

# When Should Each Skill Be Run?

| Skill              | Initial Setup | New Feature |  Bug Fix | Major Refactor | New Reports | AI Workflow Changes |
| ------------------ | :-----------: | :---------: | :------: | :------------: | :---------: | :-----------------: |
| ai-context-init    |       ✅       |      ❌      |     ❌    |        ❌       |      ❌      |          ❌          |
| ai-project-map     |       ✅       |  Sometimes  |  Rarely  |        ✅       |      ❌      |          ❌          |
| ai-report-index    |       ❌       |      ❌      |     ❌    |        ❌       |      ✅      |          ❌          |
| ai-session-context |       ❌       |      ✅      | Optional |        ✅       |   Optional  |          ❌          |
| agents-md-refresh  |       ✅       |    Rarely   |     ❌    |    Sometimes   |      ❌      |          ✅          |

---

# Recommended End-of-Day Workflow

At the end of a development session:

1. Finish coding.
2. Update `current-task.md`.
3. Update `session-context.md` if architecture or implementation changed.
4. Update `report-index.md` if reports were created.
5. Commit both source code and AI context files.

This keeps every future Codex session synchronized with the latest project state.

---

# Expected Benefits

Compared to reading the entire repository for every session:

| Without AI Context                      | With AI Context                 |
| --------------------------------------- | ------------------------------- |
| Repository scanned repeatedly           | Repository scanned once         |
| High token usage                        | Low token usage                 |
| Slow startup                            | Fast startup                    |
| Hard to resume work                     | Resume within seconds           |
| Reports repeatedly loaded               | Reports loaded only when needed |
| Architecture rediscovered every session | Architecture already summarized |

---

# Best Practices

* Keep `session-context.md` concise.
* Do not place large reports inside AI context.
* Use `report-index.md` as the entry point for reports.
* Update AI context only after meaningful project changes.
* Preserve manually written notes inside `current-task.md` whenever possible.
* Treat AI context files as project assets and commit them to version control.

Following this workflow will allow the project to scale while keeping Codex sessions efficient, consistent, and easy to resume.

### Finally Session Start System kind of prompt

```
Read AGENTS.md and follow the docs/ai-content startup rules. Then continue my task.
```
