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


## AI Assistant Runtime Setup & Validation

### 1. Overview

The current AI assistant stack is implementation-complete for configuration, prompt construction, provider abstraction, runtime routing, validation, eligibility, composition, post-processing, and the first production transport path for Claude.

What that means in practice:

- The backend can load AI configuration from `.env`.
- The prompt pipeline can build canonical prompts from conversation, workflow, and knowledge context.
- The LLM seam can build provider-neutral requests, validate responses, decide eligibility, compose final runtime output, and normalize presentation.
- The default production composition path now builds a real Anthropic-backed Claude transport when Claude is enabled and selected.
- OpenAI, Gemini, OpenRouter, and Ollama still remain transport-inactive until their production transport implementations are added.
- The current visible chat flow remains deterministic and knowledge-backed; hidden shadow execution is still best-effort and falls back safely when generation is unavailable.

### 2. Required Environment Variables

Settings are loaded from `backend/.env` because both backend config loaders read `.env` from the current backend working directory.

#### Core backend settings

| Variable name | Required? | Description | Example value |
|---|---:|---|---|
| `APP_NAME` | No | FastAPI application title used at startup. | `Doctor Appointment Testing App` |
| `API_PREFIX` | No | Prefix applied to all backend routes. | `/api` |
| `DATABASE_URL` | No | SQLAlchemy database URL; defaults to the local SQLite file. | `sqlite:///./doctor_appointment.db` |
| `CORS_ORIGINS` | No | Comma-separated list of frontend origins allowed by CORS. | `http://localhost:4002,http://127.0.0.1:4002` |

#### Global AI runtime settings

| Variable name | Required? | Description | Example value |
|---|---:|---|---|
| `LLM_PROVIDER` | Yes for runtime activation | Selected provider name. Must match one of the supported provider enums. | `claude` |
| `LLM_ENABLED` | Yes for runtime activation | Top-level runtime activation flag. | `true` |
| `LLM_ALLOW_GENERATION` | Yes for runtime activation | Allows generation-capable execution paths. | `true` |
| `LLM_SHADOW_MODE` | No | Enables shadow-mode execution decisions when generation is otherwise available. | `true` |
| `LLM_ALLOW_STREAMING` | No | Allows streaming only if the selected provider also supports it. | `false` |
| `LLM_ALLOW_TOOL_CALLING` | No | Allows tool-calling only if the selected provider also supports it. | `false` |
| `LLM_ALLOW_REASONING` | No | Allows reasoning output only if the selected provider also supports it. | `false` |
| `AI_RUNTIME_TRACE` | No | Enables backend-only structured AI runtime trace logging for each chat request. | `true` |
| `LLM_TIMEOUT_SECONDS` | No | Global timeout fallback for provider config. | `30` |
| `LLM_MAX_RETRIES` | No | Global retry fallback for provider config. | `2` |
| `LLM_RETRY_BACKOFF_SECONDS` | No | Global retry backoff fallback for provider config. | `0.5` |
| `LLM_GENERATION_BUDGET__DEFAULT_PROFILE` | No | Default canonical generation budget profile. | `balanced` |
| `LLM_GENERATION_BUDGET__FAST__MAX_OUTPUT_TOKENS` | No | Global override for the fast budget profile. | `512` |
| `LLM_GENERATION_BUDGET__BALANCED__MAX_OUTPUT_TOKENS` | No | Global override for the balanced budget profile. | `1024` |
| `LLM_GENERATION_BUDGET__WORKFLOW__MAX_OUTPUT_TOKENS` | No | Global override for the workflow budget profile. | `768` |
| `LLM_GENERATION_BUDGET__QUALITY__MAX_OUTPUT_TOKENS` | No | Global override for the quality budget profile. | `2048` |
| `LLM_GENERATION_BUDGET__MAXIMUM__MAX_OUTPUT_TOKENS` | No | Global override for the maximum budget profile. | `4096` |

#### Provider-specific settings

The same nested pattern exists for each supported provider name:

- `OPENAI`
- `CLAUDE`
- `GEMINI`
- `OPENROUTER`
- `OLLAMA`

| Variable name | Required? | Description | Example value |
|---|---:|---|---|
| `LLM_<PROVIDER>__ENABLED` | Yes for that provider | Enables the provider in the configuration model and registry. | `true` |
| `LLM_<PROVIDER>__DEFAULT_MODEL_NAME` | Yes for that provider if enabled | Canonical model name used when a request does not supply one. | `claude-sonnet-4-5` |
| `LLM_<PROVIDER>__API_KEY` | Yes for non-Ollama providers if enabled | Provider API key. | `sk-ant-...` |
| `LLM_OLLAMA__BASE_URL` | Yes for Ollama if enabled | Ollama base URL used as the required authentication/connection setting. | `http://localhost:11434` |
| `LLM_<PROVIDER>__BASE_URL` | No for non-Ollama providers | Optional provider base URL override. | `https://api.openai.com/v1` |
| `LLM_<PROVIDER>__TIMEOUT_SECONDS` | No | Provider-specific timeout override. | `45` |
| `LLM_<PROVIDER>__MAX_RETRIES` | No | Provider-specific retry override. | `3` |
| `LLM_<PROVIDER>__RETRY_BACKOFF_SECONDS` | No | Provider-specific retry backoff override. | `1.0` |
| `LLM_<PROVIDER>__FEATURE_FLAGS__STREAMING` | No | Declares provider streaming support. | `true` |
| `LLM_<PROVIDER>__FEATURE_FLAGS__STRUCTURED_OUTPUT` | No | Declares provider structured-output support. | `true` |
| `LLM_<PROVIDER>__FEATURE_FLAGS__TOOL_CALLS` | No | Declares provider tool-calling support. | `true` |
| `LLM_<PROVIDER>__FEATURE_FLAGS__REASONING` | No | Declares provider reasoning support. | `true` |
| `LLM_<PROVIDER>__FEATURE_FLAGS__CITATIONS` | No | Declares provider citation support. | `true` |
| `LLM_<PROVIDER>__GENERATION_BUDGET__DEFAULT_PROFILE` | No | Provider-specific default budget profile. | `workflow` |
| `LLM_<PROVIDER>__GENERATION_BUDGET__FAST__MAX_OUTPUT_TOKENS` | No | Provider-specific fast budget override. | `512` |
| `LLM_<PROVIDER>__GENERATION_BUDGET__BALANCED__MAX_OUTPUT_TOKENS` | No | Provider-specific balanced budget override. | `1024` |
| `LLM_<PROVIDER>__GENERATION_BUDGET__WORKFLOW__MAX_OUTPUT_TOKENS` | No | Provider-specific workflow budget override. | `768` |
| `LLM_<PROVIDER>__GENERATION_BUDGET__QUALITY__MAX_OUTPUT_TOKENS` | No | Provider-specific quality budget override. | `2048` |
| `LLM_<PROVIDER>__GENERATION_BUDGET__MAXIMUM__MAX_OUTPUT_TOKENS` | No | Provider-specific maximum budget override. | `4096` |

Important provider-auth rules from the implementation:

- OpenAI, Claude, Gemini, and OpenRouter require an API key when enabled.
- Ollama does not require an API key for activation, but it does require `LLM_OLLAMA__BASE_URL`.
- Enabled providers must also declare a default model name.
- A selected provider must be configured and enabled or activation remains inactive.

### 3. LLM Provider Configuration

Supported providers are:

- `openai`
- `claude`
- `gemini`
- `openrouter`
- `ollama`

Where to put the settings:

- Put the runtime settings in `backend/.env`.
- The root `.env.example` documents the available keys.
- The backend loads `backend/.env` through `pydantic-settings` because the startup commands run from the `backend/` directory.

How configuration is loaded:

- `backend/app/core/config.py` loads the core app settings.
- `backend/app/llm/config.py` loads the AI runtime settings.
- Both loaders read `.env` from the current backend working directory and use nested `LLM_...__...` environment mapping.

How to switch providers:

- Set `LLM_PROVIDER` to the provider name you want to select.
- Enable that provider with `LLM_<PROVIDER>__ENABLED=true`.
- Set the provider model with `LLM_<PROVIDER>__DEFAULT_MODEL_NAME`.
- Provide the matching auth value:
  - `LLM_<PROVIDER>__API_KEY` for OpenAI, Claude, Gemini, and OpenRouter
  - `LLM_OLLAMA__BASE_URL` for Ollama

How to change the model:

- Update `LLM_<PROVIDER>__DEFAULT_MODEL_NAME`.
- The adapter will use a request-level model if one is supplied, otherwise it falls back to the provider default model name.

Current runtime limitation:

- The composed runtime now uses `ProductionLLMProviderTransportFactory` by default.
- Today only Claude has a production transport implementation, so OpenAI, Gemini, OpenRouter, and Ollama still require future transport work before a valid API key can produce a live provider call.

Current production transport behavior:

- `backend/app/llm/transport.py` owns Claude HTTP communication through the official Anthropic SDK.
- `ClaudeTransport` normalizes retries, timeout handling, request-id extraction, response-id extraction, usage extraction, structured transport logging, and provider error mapping.
- `backend/app/llm/composition.py` injects Claude transport only when Claude is enabled in configuration.

### 4. Backend Startup

To start the backend with AI configuration enabled in the current repository:

```bash
cp .env.example backend/.env
make backend-setup
make backend-dev
```

To start the full app, including the frontend:

```bash
make setup
make dev
```

What those commands do:

- `make backend-setup` installs the backend virtual environment and dependencies if needed.
- `make backend-dev` starts Uvicorn from `backend/`, which lets the backend load `backend/.env`.
- `make dev` starts backend and frontend together; the frontend AI widget posts to the backend chat API through the Next.js proxy.

### 5. Startup Verification

Successful startup currently looks like normal Uvicorn and FastAPI startup output, not an AI-specific banner.

Expected healthy signals:

- `Application startup complete.`
- `Uvicorn running on http://0.0.0.0:4001`
- `GET /api/health` returns `{"status":"ok"}`

Possible backend warning that is unrelated to AI activation:

- `Rebuilding doctors table due to schema mismatch. Missing columns: ...`

What failures look like:

- If the backend cannot start, Uvicorn exits before the health check passes.
- If the database path is wrong, startup fails before `/api/health` becomes available.
- If AI configuration is invalid and you instantiate the LLM seam in tests or a shell, the config loader or activation service raises a validation/configuration error.
- There is no dedicated AI startup log line in the current code path, so you cannot confirm provider readiness from logs alone.

### 6. Runtime Verification

#### Provider Registry

What the implementation does:

- `LLMRuntimeCompositionRoot.compose()` loads config once.
- It builds adapters only for enabled providers.
- It registers those adapters in `InMemoryLLMProviderRegistry`.
- Duplicate provider names are rejected.

How to verify:

- Use the backend test suite for the composition and integration seams.
- In a Python shell, inspect `LLMRuntimeFacade.snapshot()` or `LLMIntegrationService.get_status()` on a composed runtime object.

#### Runtime Facade

What the implementation does:

- `LLMRuntimeFacade` wraps the composed LLM graph.
- It exposes `snapshot()`, `run_shadow_mode()`, and `run_controlled_generation()`.
- The conversation manager calls `run_shadow_mode()` after the visible chat response is already chosen.

How to verify:

- Send a normal chat request to `POST /api/chat`.
- Confirm the visible response does not change when shadow mode is attempted.
- In tests, inspect the returned facade snapshot and shadow diagnostics.

### 7. AI Runtime Trace Mode

What it does:

- `AI_RUNTIME_TRACE=true` enables a backend-only structured trace for each chat request.
- The trace captures the request path across `ConversationManager`, workflow detection, Vector-less RAG, execution policy, runtime facade, prompt building, LLM integration, adapter selection, provider transport, and final response ownership.
- If the request never reaches the transport layer, the trace explicitly marks `llm_not_invoked=true` and records the exact stop component and reason.
- The trace redacts common patient PII patterns from the logged user message and never logs API keys or authorization headers.

How to enable:

```bash
echo "AI_RUNTIME_TRACE=true" >> backend/.env
make backend-restart
```

How to disable:

```bash
perl -0pi -e 's/AI_RUNTIME_TRACE=true/AI_RUNTIME_TRACE=false/' backend/.env
make backend-restart
```

Sample trace:

```json
{
  "trace_name": "AI Runtime Trace",
  "request_id": "8f6d...",
  "conversation_id": "conv-123",
  "user_message": "My name is [REDACTED_NAME] and my email is [REDACTED_EMAIL]",
  "execution_policy": {
    "selected_provider": "claude",
    "generation_available": true,
    "decision": "SHADOW"
  },
  "provider_transport": {
    "transport_selected": "ClaudeTransport",
    "http_request_started": true,
    "http_response_received": true,
    "status_code": 200
  },
  "final_response": {
    "routed_to": "DETERMINISTIC_ENGINE",
    "response_source": "deterministic_engine"
  }
}
```

How to diagnose routing problems:

- If `runtime_facade.skipped=true`, read `runtime_facade.reason` first; this usually means shadow mode or generation availability was blocked before prompt building.
- If `llm_not_invoked=true`, use `stop_component` and `stop_reason` to find the exact stage where execution stopped.
- If `prompt_builder.executed=true` but `provider_transport.http_request_started=false`, inspect `llm_integration`, `provider_adapter`, and provider registration/transport readiness.
- If `provider_transport.http_request_started=true` and the visible response is still deterministic, that is expected for shadow mode because generated output is discarded after diagnostics.

#### Conversation Manager

What the implementation does:

- It builds conversation context from request history.
- It runs intent detection and entity extraction.
- It uses the knowledge retrieval service only when no workflow is active.
- It finalizes the visible response first, then triggers hidden shadow execution.

How to verify:

- Send a chat request that triggers a doctor search, knowledge reply, or workflow response.
- Confirm the backend returns the expected deterministic or knowledge-backed payload.
- Confirm there is no visible LLM-generated text in the current runtime.

#### Prompt Builder

What the implementation does:

- `PromptBuilderService.build()` collects conversation, workflow, and knowledge context.
- It validates the canonical prompt context.
- It assembles ordered sections and renders the final prompt with truncation support.

How to verify:

- Run the prompt-builder test suite.
- Instantiate `PromptBuilderService` in a shell and call `build()` with sample conversation state and documents.

#### LLM Integration

What the implementation does:

- `LLMGenerationOrchestrator` builds a prompt, converts it into a canonical request, and delegates to `LLMIntegrationService`.
- `LLMIntegrationService` resolves the selected or default provider from the registry.
- The default runtime does not create a live provider transport, so the live app remains disconnected from external LLM APIs.

How to verify:

- Use the integration, composition, activation, and adapter test suites.
- For real provider calls, inject a custom transport factory in a test or local harness; the current runtime does not do this by default.

### 7. End-to-End Smoke Test

Use the backend chat API for the smoke test. The frontend widget ultimately uses the same backend endpoint through the Next.js proxy.

1. Start the backend and confirm `GET /api/health` returns `{"status":"ok"}`.
2. Send a greeting:

```bash
curl -s http://127.0.0.1:4001/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello"}'
```

Expected response:

- `intent` is `UNKNOWN`
- `message` is the deterministic greeting
- `conversation.routed_to` is deterministic, not LLM-owned

3. Send a booking-help prompt:

```bash
curl -s http://127.0.0.1:4001/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"How do I book an appointment?"}'
```

Expected response:

- The answer is knowledge-backed when a matching FAQ document is found.
- The response includes `knowledge_source` metadata when knowledge wins.
- If no knowledge match is selected, the deterministic appointment-help response is returned.

4. Send a doctor search prompt:

```bash
curl -s http://127.0.0.1:4001/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Show cardiologists in Mumbai"}'
```

Expected response:

- `data` contains doctor cards.
- `search_filters` reflects the extracted search terms.
- The response remains deterministic or knowledge-backed; it does not rely on a live LLM call in the current runtime.

5. Send a booking workflow prompt:

```bash
curl -s http://127.0.0.1:4001/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Book an appointment with Dr. ..."}'
```

Expected response:

- The workflow engine owns the response.
- The response may include a workflow draft or a completed booking.
- The hidden shadow LLM path runs only if the runtime policy allows it, but its output is not shown to the user in the current app.

### 8. Phase 5 Validation

Phase 5 is the prompt-builder seam.

What to verify:

- Prompt Builder
- Conversation context collection
- Workflow context collection
- Knowledge context collection
- Final prompt rendering and truncation

How to verify:

```bash
cd backend
. .venv/bin/activate
pytest tests/test_prompt_builder_service.py -q
```

What to look for:

- Conversation history is normalized into canonical turns.
- Workflow state is extracted from caller-supplied context.
- Selected knowledge documents are included or excluded based on prompt hints.
- The final rendered prompt is deterministic and truncates with the expected marker when needed.

### 9. Phase 6 Validation

Phase 6 is the provider-neutral LLM seam.

What to verify:

- Provider Registry
- Provider Adapter
- LLM Generation orchestration
- Provider response translation
- Canonical response mapping

How to verify:

```bash
cd backend
. .venv/bin/activate
pytest \
  tests/test_llm_config.py \
  tests/test_llm_budget.py \
  tests/test_llm_models.py \
  tests/test_llm_integration.py \
  tests/test_llm_orchestrator.py \
  tests/test_llm_composition.py \
  tests/test_llm_activation.py \
  tests/test_llm_provider_adapters.py \
  -q
```

What to look for:

- The selected provider is loaded from `LLM_PROVIDER`.
- Enabled providers appear in the registry.
- The canonical request is translated into provider-private payloads by the adapter.
- The canonical response is mapped back into the internal response model.
- The default app runtime still stays disconnected unless you inject a real transport factory.

### 10. Phase 7 Validation

Phase 7 is the runtime facade path.

What to verify:

- Runtime Validation
- Runtime Eligibility
- Runtime Response Composer
- Runtime Response Post Processor
- Hybrid responses
- Deterministic fallback

How to verify:

```bash
cd backend
. .venv/bin/activate
pytest \
  tests/test_llm_validation.py \
  tests/test_llm_eligibility.py \
  tests/test_llm_composer.py \
  tests/test_llm_post_processor.py \
  tests/test_llm_facade.py \
  tests/test_conversation_manager.py \
  tests/test_chat_api.py \
  -q
```

What to look for:

- Validation rejects empty, whitespace-only, malformed, or invalid canonical output.
- Eligibility only approves low-risk conversational scenarios.
- The composer preserves deterministic business truth in deterministic-only and hybrid paths.
- The post processor normalizes visible presentation text and strips presentation-only metadata.
- The visible app behavior remains deterministic because the live runtime has no default transport.

### 11. Troubleshooting

| Issue | Symptoms | Probable cause | Resolution |
|---|---|---|---|
| Missing API key | Enabled non-Ollama provider stays inactive or config validation fails in tests or shell checks. | `LLM_<PROVIDER>__API_KEY` is blank for a provider that requires one. | Add the provider API key in `backend/.env` and keep the provider enabled. |
| Invalid model | Provider activation stays inactive or the config loader raises a validation error. | `LLM_<PROVIDER>__DEFAULT_MODEL_NAME` is missing or empty. | Set a valid model name for the selected provider. |
| Invalid provider | Startup/config checks fail before a provider is selected. | `LLM_PROVIDER` is not one of `openai`, `claude`, `gemini`, `openrouter`, or `ollama`. | Change `LLM_PROVIDER` to a supported enum value. |
| Authentication failure | A custom harness can reach the transport but the provider rejects the request. | The API key, base URL, or upstream credentials are wrong. | Fix the provider credentials and retry with a known-good model name. |
| Timeout | A custom harness hangs or returns a timeout error. | Provider timeout is too low, network latency is high, or the upstream is slow. | Increase `LLM_TIMEOUT_SECONDS` or the provider-specific timeout override. |
| Network failure | Provider call fails before a response is returned. | The upstream endpoint is unreachable or the base URL is wrong. | Verify the provider base URL and network connectivity. |
| Empty response | Validation fails on `response_message.content`. | The provider returned empty or whitespace-only text. | Check the provider response or fall back to deterministic chat. |
| Validation failure | Controlled generation returns a failed validation result. | The orchestration result is missing canonical fields or structured output is malformed. | Fix the provider mapping or use the deterministic fallback path. |
| Eligibility rejection | Controlled generation is skipped after validation. | The request is not a low-risk conversational scenario or the policy did not approve visibility. | Keep the visible response deterministic for workflow-owned or non-approved requests. |
| Runtime fallback | The app returns deterministic or knowledge-backed chat instead of AI-generated output. | The default runtime has no active transport, or activation/policy rejected generation. | This is expected in the current repo unless you inject a real transport factory in a custom harness. |
| No AI trace logs | No `ai_runtime_trace` log entries appear during chat requests. | `AI_RUNTIME_TRACE` is false or the backend was not restarted after changing `backend/.env`. | Set `AI_RUNTIME_TRACE=true` in `backend/.env` and restart the backend. |
| `LLM NOT INVOKED` in trace | Trace shows `llm_not_invoked=true` with a stop component. | Routing or provider readiness stopped the request before the provider transport. | Use `stop_component`, `stop_reason`, and the stage sections in the trace payload to identify the blocking seam. |

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
