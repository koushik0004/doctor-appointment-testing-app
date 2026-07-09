You are acting as a Principal Enterprise Solution Architect.

Your task is to reverse-engineer the AI Assistant implementation and generate a complete API Design Document.

IMPORTANT

This document is ONLY for the AI Assistant.

DO NOT document APIs belonging to the base application.

DO NOT document Appointment APIs.

DO NOT document Doctor APIs.

DO NOT document Patient APIs.

DO NOT document business application APIs unless they are invoked by the AI Runtime.

Treat the implementation as the single source of truth.

Never invent endpoints.

Never redesign the implementation.

----------------------------------------------------------
OBJECTIVE
----------------------------------------------------------

Analyze the complete repository.

Read:

- Source code
- Controllers
- Routes
- API layer
- Conversation Manager
- Workflow Engine
- Vector-less RAG
- Prompt Builder
- Controlled Generation
- Runtime Facade
- Runtime Validator
- Eligibility
- Composer
- Post Processor
- Provider Registry
- Provider Adapter
- Provider Transport
- Runtime Trace
- Configuration
- Existing documentation
- README
- AGENTS
- Runtime reports
- Architecture documents
- Test cases

Reverse engineer every API and every internal runtime contract used by the AI Assistant.

----------------------------------------------------------
OUTPUT
----------------------------------------------------------

Generate

docs/reports/architecture/AI-Assistant-API-Design.md

----------------------------------------------------------
DOCUMENT STRUCTURE
----------------------------------------------------------

1.
Purpose

2.
Scope

3.
Architecture Context

Explain where the AI APIs sit inside the runtime.

Example

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

Prompt Builder

↓

LLM Runtime

↓

Composer

↓

Response

----------------------------------------------------------

4.
External REST APIs

For every AI endpoint include

- Endpoint
- HTTP Method
- Purpose
- Authentication
- Request Headers
- Query Parameters
- Request Body
- Response Body
- Status Codes
- Error Responses
- Validation Rules
- Example Request
- Example Response

----------------------------------------------------------

5.
Conversation APIs

Document

- Conversation initialization
- Continue conversation
- Session handling
- History handling
- Context update

----------------------------------------------------------

6.
Runtime Processing APIs

Document the internal processing contracts.

Examples

Conversation Manager

↓

Execution Policy

↓

Workflow Engine

↓

Knowledge Engine

↓

Prompt Builder

↓

LLM Runtime

↓

Composer

↓

Post Processor

For each stage describe

- Input Contract
- Output Contract
- Validation
- Failure Conditions

----------------------------------------------------------

7.
Workflow APIs

Reverse engineer every workflow interaction.

Document

- Workflow selection
- Workflow execution
- Workflow completion
- Workflow interruption
- Workflow continuation

Explain how workflows call business APIs.

Do NOT document the business APIs themselves.

----------------------------------------------------------

8.
Knowledge APIs

Document

Knowledge lookup

Knowledge search

Knowledge retrieval

Knowledge ranking

Knowledge formatting

Knowledge response generation

Explain routing logic.

----------------------------------------------------------

9.
Prompt Builder APIs

Document

Conversation Context

Workflow Context

Knowledge Context

Runtime Context

Prompt Assembly

Prompt Output

----------------------------------------------------------

10.
Controlled Generation APIs

Document

Eligibility evaluation

Execution policy

Generation decision

Routing decision

Fallback

----------------------------------------------------------

11.
LLM Runtime APIs

Document

Provider Registry

Provider Adapter

Provider Transport

Provider Request

Provider Response

Provider Errors

Retry

Timeout

----------------------------------------------------------

12.
Runtime Validation APIs

Document

Validation

Safety

Eligibility

Response Verification

----------------------------------------------------------

13.
Composer APIs

Document

Response composition

Formatting

Citation attachment

Metadata enrichment

----------------------------------------------------------

14.
Post Processor APIs

Document

Cleanup

Formatting

Normalization

Final output generation

----------------------------------------------------------

15.
Runtime Trace APIs

Document

Trace generation

Logging

Metrics

Diagnostics

----------------------------------------------------------

16.
Routing Decision Matrix

Create a table showing exactly how requests are routed.

Example

Greeting

↓

Conversation Manager

↓

Response

Appointment Booking

↓

Workflow

↓

Business API

FAQ

↓

Knowledge

↓

Prompt Builder

↓

Response

Complex Question

↓

Prompt Builder

↓

LLM

↓

Composer

↓

Response

Unknown

↓

Fallback

----------------------------------------------------------

17.
Internal Runtime Contracts

Document every internal DTO/model exchanged between runtime components.

Examples

ChatRequest

ConversationContext

WorkflowContext

KnowledgeResult

PromptContext

PromptRequest

ProviderRequest

ProviderResponse

ValidationResult

ComposerRequest

ComposerResponse

RuntimeTrace

Only document models that actually exist.

----------------------------------------------------------

18.
Error Handling

Reverse engineer

Validation errors

Provider failures

Knowledge failures

Workflow failures

Timeouts

Retries

Fallback responses

----------------------------------------------------------

19.
Sequence Mapping

For every API map it to the runtime stages.

API

↓

Conversation Manager

↓

Workflow

↓

Knowledge

↓

Prompt

↓

LLM

↓

Validation

↓

Composer

↓

Post Processor

----------------------------------------------------------

20.
Production Considerations

Document

Performance

Scalability

Caching

Idempotency

Concurrency

Timeouts

Security

Observability

Tracing

Configuration

Versioning

----------------------------------------------------------

QUALITY REQUIREMENTS
----------------------------------------------------------

Everything must be derived from implementation.

Never invent endpoints.

Never redesign APIs.

Never describe future work.

Use actual names from the codebase.

If implementation differs from documentation,

implementation wins.

Every API should include examples.

Every routing decision should be explained.

Every runtime interaction should be documented.

Use Mermaid diagrams wherever interaction diagrams improve clarity.

The final document should be suitable for enterprise API review and architecture review.