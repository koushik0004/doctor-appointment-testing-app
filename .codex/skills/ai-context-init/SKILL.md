---
name: ai-context-init
description: Initialize docs/ai-content folder, manifest, and empty AI context files.
---

# AI Context Init

Create this folder if missing:

- docs/ai-content/

Create these files if missing:

- docs/ai-content/manifest.yaml
- docs/ai-content/current-task.md
- docs/ai-content/project-map.md
- docs/ai-content/feature-map.md
- docs/ai-content/important-files.md
- docs/ai-content/report-index.md
- docs/ai-content/session-context.md
- docs/ai-content/decision-log.md

Do not overwrite existing content.

Initialize manifest.yaml with:

context_directory: docs/ai-content
startup_files:
  - session-context.md
  - current-task.md
  - important-files.md
  - feature-map.md
  - report-index.md
optional_files:
  - project-map.md
  - decision-log.md
full_reports_directory: docs/reports
rule: Read summaries first. Read full reports only when task requires them.

Final output:
- files created
- files already existed