Doctor Appointment AI Assistant

This is NOT a new feature.

We are debugging the existing production runtime.

The architecture is already complete.

Do NOT redesign anything.

Do NOT modify routing.

Do NOT change business logic.

Do NOT change Prompt Builder.

Do NOT change Vector-less RAG.

Do NOT change ConversationManager behavior.

The objective is ONLY to implement complete runtime tracing.

=========================================================
CURRENT PROBLEM
=========================================================

AIRuntimeTraceSession already exists.

Every runtime component already calls

runtime_trace.update_stage(...)

or

runtime_trace.mark_llm_not_invoked(...)

However:

- logs/ai-runtime-trace.log is never created
- tracing is incomplete
- exceptions are swallowed
- execution stop point is unknown

The transport already records

- sdk initialization
- http request
- http response
- latency
- token usage

Do NOT duplicate transport tracing.

Instead complete the missing runtime observability.

=========================================================
OBJECTIVE
=========================================================

Implement a production-quality runtime trace that allows us to identify EXACTLY where execution stops.

Every request must generate exactly ONE trace.

The trace must survive exceptions.

The trace must be written even if generation fails.

=========================================================
REQUIREMENTS
=========================================================

1.

Implement a dedicated runtime trace logger.

It must NOT depend on the application's root logger.

Create

logs/

automatically if missing.

Create

logs/ai-runtime-trace.log

automatically.

Use

RotatingFileHandler

or

TimedRotatingFileHandler

Never rely on logger.info() alone.

2.

AIRuntimeTraceSession.emit()

must

- serialize JSON
- append exactly one JSON object per request
- flush immediately
- never silently fail

If writing fails

write the exception to the application logger.

3.

ConversationManager must emit

ENTER

and

EXIT

for

conversation_manager

4.

Workflow Engine

must record

entered

completed

duration

5.

Vector-less RAG

must record

retrieval started

matched document

score

matched terms

retrieval completed

6.

Execution Policy

must record

activation snapshot

selected provider

generation available

routing decision

fallback reason

7.

Runtime Facade

must record

entered

controlled generation selected

shadow mode

skipped reason

8.

Prompt Builder

must record

entered

prompt built

prompt length

token estimate

9.

LLM Integration

must record

entered

provider selected

provider registry lookup

adapter resolved

generation request created

response received

10.

Provider Adapter

must record

entered

request translated

transport invoked

response translated

11.

Transport

Already implemented.

Only ensure timestamps remain consistent.

12.

Validator

Eligibility

Composer

Post Processor

must each record

entered

completed

status

13.

Every exception must record

component

exception type

message

stack trace

before being re-raised or converted into fallback.

14.

If any component decides NOT to invoke the LLM

record

stop_component

stop_reason

llm_not_invoked=true

15.

ConversationManager must emit()

inside a finally block.

No execution path may exit without emitting the trace.

=========================================================
TRACE FORMAT
=========================================================

Each request must generate one JSON object.

Include

trace_id
timestamp
conversation_id
request_id

user_message

intent

execution_mode

selected_provider

activation_status

every runtime stage

stop_component

stop_reason

llm_not_invoked

final_response_source

final_response_preview

latency_ms

=========================================================
IMPORTANT
=========================================================

Do NOT redesign architecture.

Do NOT add new services.

Do NOT add new dependencies.

Reuse the existing AIRuntimeTraceSession.

Reuse existing runtime_trace.update_stage() calls.

Fill only the missing observability.

=========================================================
OUTPUT
=========================================================

Generate complete production-ready code modifications.

Only modify files required for tracing.

Keep changes minimal.

Maintain backward compatibility.

Do not modify business behavior.
