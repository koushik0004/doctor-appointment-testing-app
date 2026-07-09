The architecture is frozen.

Do NOT redesign any completed phase.

Do NOT change business logic.

Do NOT change routing behaviour.

------------------------------------------------------------
OBJECTIVE
------------------------------------------------------------

Implement a production-safe AI Runtime Trace Mode.

The purpose is to debug the complete execution path of a chat request.

This is for backend diagnostics only.

------------------------------------------------------------
Configuration
------------------------------------------------------------

Add a new environment variable:

AI_RUNTIME_TRACE=false

When false

- no trace logs
- negligible runtime overhead

When true

- emit detailed execution trace

------------------------------------------------------------
Trace every stage
------------------------------------------------------------

For every chat request, log:

=========================================================
AI Runtime Trace
=========================================================

Request Id

Conversation Id

Timestamp

User Message

---------------------------------------------------------
Conversation Manager
---------------------------------------------------------

conversation loaded

history size

conversation state

intent

routing metadata

---------------------------------------------------------
Workflow Engine
---------------------------------------------------------

workflow detected

workflow name

business intent

---------------------------------------------------------
Vector-less RAG
---------------------------------------------------------

executed?

knowledge found?

documents returned?

---------------------------------------------------------
Execution Policy
---------------------------------------------------------

LLM enabled

selected provider

provider healthy

generation allowed

generation available

execution owner

decision

reason

---------------------------------------------------------
Runtime Facade
---------------------------------------------------------

entered?

skipped?

reason

---------------------------------------------------------
Prompt Builder
---------------------------------------------------------

executed?

prompt generated?

prompt length

token estimate

---------------------------------------------------------
LLM Integration
---------------------------------------------------------

provider

model

generation profile

generation budget

---------------------------------------------------------
Provider Adapter
---------------------------------------------------------

adapter selected

request translated

---------------------------------------------------------
Provider Transport
---------------------------------------------------------

transport selected

SDK initialized

HTTP request started

HTTP response received

status code

latency

token usage

---------------------------------------------------------
Runtime Validator
---------------------------------------------------------

pass/fail

reason

---------------------------------------------------------
Eligibility
---------------------------------------------------------

pass/fail

reason

---------------------------------------------------------
Composer
---------------------------------------------------------

deterministic

LLM

hybrid

reason

---------------------------------------------------------
Post Processor
---------------------------------------------------------

executed?

---------------------------------------------------------
Final Response
---------------------------------------------------------

routed_to

response owner

response source

=========================================================

------------------------------------------------------------
Requirements
------------------------------------------------------------

Use structured logging.

Never log API keys.

Never log authorization headers.

Never log patient PII.

Only enable when AI_RUNTIME_TRACE=true.

When disabled there should be almost zero performance impact.

------------------------------------------------------------
Additional Requirement
------------------------------------------------------------

If execution never reaches the transport layer,

explicitly log

"LLM NOT INVOKED"

and include the exact component and reason where execution stopped.

------------------------------------------------------------
Documentation
------------------------------------------------------------

Update README with:

AI Runtime Trace Mode

Explain:

- how to enable
- how to disable
- sample trace
- how to diagnose routing problems