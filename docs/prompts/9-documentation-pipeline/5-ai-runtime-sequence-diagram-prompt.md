You are acting as a Principal Enterprise Solution Architect.

Your task is to reverse-engineer the AI Assistant implementation and generate a complete set of runtime sequence diagrams.

DO NOT modify any code.

DO NOT redesign the architecture.

DO NOT assume missing functionality.

The implementation is the single source of truth.

----------------------------------------------------
OBJECTIVE
----------------------------------------------------

Analyze the COMPLETE repository including:

- Source code
- Runtime
- Services
- AI modules
- Configuration
- Prompt Builder
- Conversation Manager
- Workflow Engine
- Runtime Validator
- Eligibility
- Composer
- Post Processor
- Provider Adapter
- Provider Transport
- Runtime Trace
- Existing reports
- Existing architecture documents
- README
- AGENTS
- Testing documents

Then reconstruct the ACTUAL runtime execution flow.

----------------------------------------------------
OUTPUT
----------------------------------------------------

Generate

docs/reports/architecture/AI-Runtime-Sequence-Diagrams.md

Use Mermaid sequence diagrams only.

Every scenario must have:

- Title
- Description
- Trigger
- Preconditions
- Mermaid Diagram
- Step-by-step explanation
- Important production considerations

----------------------------------------------------
IMPORTANT
----------------------------------------------------

Every participant shown in the sequence diagram MUST correspond to an actual implementation component.

Never invent layers.

Never simplify the runtime.

Preserve actual execution order.

If multiple execution paths exist, generate separate diagrams.

----------------------------------------------------
GENERATE DIAGRAMS FOR ALL MAJOR SCENARIOS
----------------------------------------------------

1.
Initial Chat Initialization

User
→ Chat Widget
→ Backend API
→ Conversation Manager
→ Greeting Response

--------------------------------------------

2.
Normal User Conversation

User Question

↓

Conversation Manager

↓

Execution Policy

↓

Response

--------------------------------------------

3.
Workflow Detection

User

↓

Conversation Manager

↓

Workflow Engine

↓

Workflow Selection

↓

Business API

↓

Response

--------------------------------------------

4.
Knowledge Retrieval (Vector-less RAG)

User

↓

Conversation Manager

↓

Workflow Engine

↓

Knowledge Search

↓

Prompt Builder

↓

Response

--------------------------------------------

5.
Controlled Generation

User

↓

Execution Policy

↓

Eligibility

↓

Controlled Generation

↓

Prompt Builder

↓

LLM Runtime

↓

Composer

↓

Post Processor

↓

Response

--------------------------------------------

6.
Prompt Builder Flow

Conversation Context

Workflow Context

Knowledge Context

Runtime Context

↓

Prompt Assembly

↓

Final Prompt

--------------------------------------------

7.
LLM Runtime

Prompt

↓

Provider Registry

↓

Provider Adapter

↓

Transport

↓

Claude/OpenAI

↓

Response

↓

Validation

--------------------------------------------

8.
Runtime Validation

LLM Response

↓

Runtime Validator

↓

Safety Checks

↓

Eligibility

↓

Composer

--------------------------------------------

9.
Post Processing

Validated Response

↓

Composer

↓

Formatting

↓

Response Cleanup

↓

Runtime Trace

↓

Final Response

--------------------------------------------

10.
Runtime Trace Logging

Every important runtime event

↓

Runtime Trace

↓

Log Storage

--------------------------------------------

11.
Business Workflow Example

User asks to perform business action

↓

Conversation

↓

Workflow Engine

↓

Business API

↓

Business Response

↓

AI Response

--------------------------------------------

12.
Fallback Flow

Unknown Intent

↓

Knowledge

↓

LLM

↓

Fallback

↓

User

--------------------------------------------

13.
Provider Failure

LLM Failure

↓

Retry

↓

Fallback

↓

Response

--------------------------------------------

14.
Complete End-to-End Runtime

User

↓

Chat Widget

↓

REST API

↓

Conversation Manager

↓

Workflow Engine

↓

Knowledge

↓

Execution Policy

↓

Eligibility

↓

Prompt Builder

↓

Runtime

↓

Provider

↓

LLM

↓

Validator

↓

Composer

↓

Post Processor

↓

Runtime Trace

↓

Final Response

----------------------------------------------------
QUALITY REQUIREMENTS
----------------------------------------------------

Each Mermaid diagram should be independently renderable.

Avoid giant unreadable diagrams.

One scenario = one sequence diagram.

Use actual implementation names.

Maintain consistent participant naming.

Explain why each component exists.

Highlight where decisions are made.

Highlight where business APIs are called.

Highlight where LLM is invoked.

Highlight where tracing occurs.

Highlight where validation occurs.

----------------------------------------------------
VERIFICATION
----------------------------------------------------

Before writing each diagram verify that the flow matches the current implementation.

If code contradicts existing documentation,

follow the code.

Do not invent missing interactions.

Treat the repository as production software.