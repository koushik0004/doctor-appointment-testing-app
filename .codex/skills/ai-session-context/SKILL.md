---
name: ai-session-context
description: Generate compact session-context and current-task guidance from existing AI context files.
---

# AI Session Context

Read:

- docs/ai-content/manifest.yaml
- docs/ai-content/project-map.md
- docs/ai-content/feature-map.md
- docs/ai-content/important-files.md
- docs/ai-content/report-index.md
- docs/ai-content/current-task.md if it exists

Update:

- docs/ai-content/session-context.md

session-context.md must be compact.

Include:
- project summary
- current architecture
- frontend/backend boundaries
- context loading rules
- important files to read first
- commands to run
- report loading rule
- known gaps
- task resume rule

Do not include full reports.

Final output:
- session-context updated
- estimated context size
- files used