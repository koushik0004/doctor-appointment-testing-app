---
name: app-context-builder
description: Read the full application and generate project map, catalog files, and a compact context pack for future Codex sessions.
---

# App Context Builder

When this skill is used, analyze the repository from root and generate/update these files:

- docs/ai-content/project-map.md
- docs/ai-content/file-catalog.md
- docs/ai-content/session-context.md
- docs/ai-content/feature-map.md
- docs/ai-content/important-files.md

## Rules

- Do not modify application source code.
- Read package/config files first.
- Understand frontend, backend, DB, API, routing, state management, tests, build scripts.
- Ignore generated folders: node_modules, dist, build, coverage, .next, .angular, target, .git.
- Keep output concise and useful for feeding into a new Codex session.

## Step 1: Identify stack

Inspect important root files:

- package.json
- angular.json / next.config / vite.config
- tsconfig files
- eslint/prettier configs
- docker files
- backend config files
- README files
- env examples

## Step 2: Generate docs/project-map.md

Include:

- app purpose
- tech stack
- folder structure
- major modules
- routing overview
- API/service layer overview
- state management overview
- styling approach
- test/build commands

## Step 3: Generate docs/file-catalog.md

Create a catalog table:

| File/Folder | Purpose | Importance | When to feed in context |
|---|---|---|---|

Importance values:

- Critical
- High
- Medium
- Low

## Step 4: Generate docs/important-files.md

List only the files Codex should read first in new sessions.

Group by:

- App entry/setup
- Routes/pages
- Core services/API
- Store/state
- Shared components
- Types/models
- Config
- Tests

## Step 5: Generate docs/feature-map.md

Map features like:

| Feature | UI files | Service/API files | Store/model files | Notes |
|---|---|---|---|---|

## Step 6: Generate docs/session-context.md

This is the most important file.

Keep it short enough to paste into a fresh Codex chat.

Include:

- Project summary
- Architecture summary
- Current conventions
- Critical files to read
- Commands to run
- Known risks/gaps
- Suggested next files to inspect depending on task type

## Final response

After creating/updating files, summarize:

- files created
- most important context file
- suggested next Codex command