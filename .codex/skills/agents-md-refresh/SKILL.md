---
name: agents-md-refresh
description: Update root AGENTS.md to load docs/ai-content context safely and avoid unnecessary token usage.
---

# AGENTS.md Refresh

Read:

- existing AGENTS.md
- docs/ai-content/manifest.yaml
- docs/ai-content/session-context.md
- docs/ai-content/important-files.md
- docs/ai-content/report-index.md

Update root AGENTS.md.

Rules:
- Preserve useful existing project rules.
- Add startup context rule.
- Add report loading restriction.
- Add token optimization rule.
- Add task resume rule.
- Do not include full report content.
- Keep AGENTS.md concise.

Required AGENTS.md rule:

Before work, read:
1. docs/ai-content/manifest.yaml
2. docs/ai-content/session-context.md
3. docs/ai-content/current-task.md
4. docs/ai-content/important-files.md
5. docs/ai-content/report-index.md

Do not read full reports unless required by the current task.

Final output:
- AGENTS.md updated
- sections changed
- any missing context files