---
name: ai-report-index
description: Create a compact report-index from docs/reports without injecting full reports into startup context.
---

# AI Report Index

Read docs/ai-content/manifest.yaml first.

Find reports under:

- docs/reports/

Do not copy full report content into AI context files.

Update:

- docs/ai-content/report-index.md

Use this format:

| Report | Area | 5-line Summary | When to Read Full Report |
|---|---|---|---|

Rules:
- Maximum 5 lines summary per report.
- Mention exact report path.
- Clearly say when the full report should be read.
- If no reports exist, write "No reports found yet."

Final output:
- reports indexed
- reports skipped
- warnings if any report is too large or unclear