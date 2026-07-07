The investigation report is the source of truth.

Do NOT redesign any completed architecture.

Do NOT modify Prompt Builder.

Do NOT modify Conversation Manager.

Do NOT modify Workflow Engine.

Do NOT modify Runtime Validation.

Do NOT modify Runtime Eligibility.

Do NOT modify Runtime Composer.

Do NOT modify Runtime Post Processor.

------------------------------------------------------------
OBJECTIVE
------------------------------------------------------------

Implement the missing Production Transport Layer.

The current provider-neutral architecture is complete except for the network transport.

Implement the transport infrastructure and make Claude the first production provider.

------------------------------------------------------------
IMPLEMENT
------------------------------------------------------------

Implement:

1.

ClaudeTransport

Responsibilities:

- own all HTTP communication with Anthropic
- authentication
- retries
- timeout
- error mapping
- structured logging
- usage extraction
- request id extraction

------------------------------------------------------------

2.

ProductionLLMProviderTransportFactory

Replace the inactive transport factory.

Create transports based on

LLM_PROVIDER

LLM_<PROVIDER>__ENABLED

configuration.

Inject only enabled providers.

------------------------------------------------------------

3.

Composition Root

Update the composition root so production runtime composes:

Configuration

↓

Transport Factory

↓

Claude Transport

↓

Claude Adapter

↓

Registry

↓

Integration Service

↓

Orchestrator

without changing existing architecture.

------------------------------------------------------------

4.

Claude SDK

Use the official Anthropic SDK.

Do not manually build HTTP unless the SDK cannot support an existing feature.

------------------------------------------------------------

5.

Translate existing canonical request into Anthropic request.

Support:

- model
- system prompt
- messages
- max_tokens
- thinking
- generation budget
- structured output (if supported)
- tool calling (if supported)
- metadata

Reuse existing adapter translation.

------------------------------------------------------------

6.

Translate Anthropic response back into canonical models.

Support:

- content
- finish reason
- usage
- model
- response id
- citations (if available)
- thinking summary (if available)
- tool calls
- metadata

------------------------------------------------------------

7.

Logging

Add structured logs.

Never log API keys.

Log:

provider

model

request id

response id

latency

input tokens

output tokens

finish reason

status code

------------------------------------------------------------

8.

Diagnostics

Return transport diagnostics for runtime activation.

------------------------------------------------------------

9.

Error Mapping

Normalize:

401

403

404

408

429

500

503

timeouts

network failures

SDK exceptions

into existing runtime error models.

------------------------------------------------------------

10.

Tests

Add real transport unit tests using mocked SDK responses.

Do NOT require a real API key.

------------------------------------------------------------

11.

Integration Test

Create one optional integration test.

Run only when

CLAUDE_API_KEY

(or equivalent)

is configured.

Skip automatically in CI.

------------------------------------------------------------

12.

Documentation

Update:

README

implementation report

runtime report

manual validation steps

Only where required.

------------------------------------------------------------

IMPORTANT

Do NOT implement OpenAI, Gemini, OpenRouter or Ollama yet.

The objective is to prove one provider works end-to-end.

Architecture must remain provider-neutral.