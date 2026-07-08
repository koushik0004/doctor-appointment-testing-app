The implementation report and runtime execution trace are the source of truth.

Do NOT redesign the architecture.

Do NOT bypass existing layers.

Do NOT remove deterministic routing.

Do NOT remove Vector-less RAG.

Do NOT bypass the Runtime Facade.

Do NOT directly invoke the Provider Adapter.

Do NOT directly invoke ClaudeTransport.

------------------------------------------------------------
OBJECTIVE
------------------------------------------------------------

The production Claude Transport is implemented.

The remaining issue is that the runtime never reaches:

Phase 5
Prompt Builder

Phase 6
LLM Integration

Phase 7
Controlled Runtime Integration

because the current execution path exits during shadow execution.

Implement the minimum production-safe changes required so that eligible requests can execute the Controlled Runtime pipeline.

------------------------------------------------------------
CURRENT BEHAVIOUR
------------------------------------------------------------

Current path:

Conversation Manager

↓

Workflow Engine

↓

Vector-less RAG

↓

LLMRuntimeFacade.run_shadow_mode()

↓

Execution Policy

↓

should_execute_shadow = false

↓

Return

Therefore Prompt Builder, Orchestrator, Integration Service, Provider Adapter, Claude Transport, Validator, Eligibility, Composer and Post Processor are never executed.

------------------------------------------------------------
REQUIRED IMPLEMENTATION
------------------------------------------------------------

Investigate the existing Runtime Facade and Execution Policy.

Determine how the runtime should transition from Shadow Mode to Controlled Generation.

Do NOT invent a new execution model.

Reuse the existing architecture.

Implement only the missing integration.

------------------------------------------------------------
Execution Policy
------------------------------------------------------------

Review AIExecutionPolicyEvaluator.

Determine:

- when controlled generation should execute
- when deterministic ownership should remain
- when workflow ownership should remain
- when Vector-less RAG ownership should remain
- when hybrid composition should execute

The decision must remain deterministic and production-safe.

------------------------------------------------------------
Runtime Facade
------------------------------------------------------------

Use the existing run_controlled_generation() implementation.

Do NOT duplicate its logic.

Determine where ConversationManager should invoke controlled generation instead of shadow execution.

------------------------------------------------------------
Routing Rules
------------------------------------------------------------

Preserve:

Workflow ownership.

Business API ownership.

Vector-less RAG ownership.

Only invoke Controlled Generation when appropriate.

Example:

General AI questions

"What is quantization?"

"What is diabetes?"

"What causes migraine?"

"What is machine learning?"

should become LLM-eligible.

Booking workflow

Cancel workflow

Confirmation workflow

Doctor search

Availability lookup

must remain deterministic.

------------------------------------------------------------
Hybrid Responses
------------------------------------------------------------

If Vector-less RAG returns relevant context,

reuse the existing Runtime Composer.

Allow:

Workflow

+

RAG

+

LLM

to compose the final response.

Do not bypass Composer.

------------------------------------------------------------
Validation
------------------------------------------------------------

Responses generated through Controlled Generation must continue through:

Runtime Validator

↓

Runtime Eligibility

↓

Runtime Response Composer

↓

Runtime Response Post Processor

Do not skip any layer.

------------------------------------------------------------
Diagnostics
------------------------------------------------------------

Extend AI Runtime Trace so it clearly reports:

Execution Owner

Shadow Mode

Controlled Generation

Prompt Builder Executed

Orchestrator Executed

Provider Invoked

Transport Invoked

Validator Executed

Eligibility Executed

Composer Executed

Post Processor Executed

Reason for routing decision

------------------------------------------------------------
Testing
------------------------------------------------------------

After implementation, these scenarios should behave as follows:

1.

"What is quantization?"

Expected:

Execution reaches Prompt Builder.

Claude Transport invoked.

LLM response returned.

2.

"My wife has migraine for 3 weeks."

Expected:

Workflow = none.

Vector-less RAG consulted.

Controlled Generation executed.

Runtime Composer combines RAG context with Claude guidance.

3.

"Book an appointment with Dr Elena Rodriguez tomorrow at 4 PM."

Expected:

Workflow owns the request.

No LLM business decision.

Business APIs remain source of truth.

------------------------------------------------------------
Deliverables
------------------------------------------------------------

Update only the required integration code.

Preserve all completed architecture.

Generate an implementation report including:

- files modified
- routing changes
- execution flow before/after
- why controlled generation was previously unreachable
- how it is now activated
- manual validation steps