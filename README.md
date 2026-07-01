# Doctor Appointment AI App - Spec Pack

This pack contains markdown specifications for building the first version of the CareNow-style doctor appointment application using spec-driven development.

Focus of this version:

- Next.js frontend
- FastAPI backend
- SQLite database
- Simple appointment booking flow
- Email confirmation
- Future-ready AI chatbot/browser-agent integration

Start reading in this order:

1. `docs/project-context.md`
2. `docs/product-specification.md`
3. `docs/architecture.md`
4. `docs/development-roadmap.md`
5. `.claude/CLAUDE.md`
6. `.claude/project-map.md`
7. `.claude/feature-map.md`

Root dev workflow:

```bash
make setup
make dev
make stop
```

Useful root commands:

```bash
make backend-setup
make frontend-setup
make backend-restart
make frontend-restart
make restart
```


## Codex skill related

```
.codex/skills/update-existing-report
 
Existing Report:
docs/reports/feature-10/ai-impl-architecture-and-implementation/phase-03-report.md

Analyze:
last 4-5 commits
```

- At new session start in codex
```
$ai-context-init
Initialize AI context files only. Do not analyze the app yet.
```

- If need to update project-map file
```
$ai-project-map
Analyze the app and generate project-map, feature-map, and important-files only.
```

- If need to update project index
```
$ai-report-index
Create report-index only. Do not update other files.
```

- Update the context upfter feature implementation
```
$ai-session-context
Generate compact session-context only from existing AI context files.
```

- After all need to update the AGENT.md file for context loading
```
$agents-md-refresh
Update AGENTS.md based on docs/ai-content structure only.
```