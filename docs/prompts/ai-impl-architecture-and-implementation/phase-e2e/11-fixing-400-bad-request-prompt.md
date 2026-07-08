We have identified the production root cause.

Do NOT redesign the architecture.

Do NOT modify business logic.

Do NOT modify Prompt Builder.

Do NOT modify ConversationManager.

Do NOT modify Runtime Facade.

Do NOT modify execution policy.

This is a provider request serialization bug.

=====================================================

Observed runtime trace

Anthropic returns

400 Bad Request

metadata.routed_to:
Extra inputs are not permitted

The runtime trace confirms

ConversationManager ✓

Runtime Facade ✓

Prompt Builder ✓

LLM Integration ✓

Provider Adapter ✓

Claude Transport ✓

The request fails immediately before inference.

=====================================================

Root Cause

Internal runtime metadata is being forwarded directly into the Anthropic Messages API request.

Application metadata contains fields such as

routed_to

execution_owner

execution_mode

conversation diagnostics

runtime tracing metadata

These are internal fields.

They must never be sent to Anthropic.

=====================================================

Required implementation

Inspect the complete request-building pipeline.

Starting from

LLMGenerationRequest

↓

Provider Request

↓

ClaudeTransport

↓

client.messages.create(...)

Determine exactly where runtime metadata is copied into the Anthropic request.

Remove only unsupported fields.

Do NOT remove runtime metadata from the application.

Runtime metadata must still be preserved inside

AIRuntimeTraceSession

and

ai-runtime-trace.log

Only sanitize the provider request.

=====================================================

Implement provider-specific serialization.

Anthropic payload must contain only officially supported fields.

Do not forward arbitrary metadata dictionaries.

Whitelist provider-supported request properties instead of forwarding generic dictionaries.

If provider-specific metadata is unsupported,

exclude it from the outgoing payload.

=====================================================

After implementation verify

User

Hello

Expected

client.messages.create()

returns HTTP 200

Claude generates response

runtime trace records

provider_transport.completed=true

http_request_sent=true

http_response_received=true

response_received=true

transport_invoked=true

No

LLMTransportError

No

metadata.routed_to

No

400 Bad Request

=====================================================

Output

Generate production-ready code modifications only.

Keep changes minimal.

Maintain backward compatibility.

Do not redesign the provider architecture.

Fix only the request serialization layer.