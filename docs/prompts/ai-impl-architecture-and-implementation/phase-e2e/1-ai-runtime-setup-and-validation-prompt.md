# Objective

Update the project's README.md by adding a comprehensive "AI Assistant Runtime Setup & Validation" section.

IMPORTANT

Do NOT assume any configuration.

Determine everything from the existing implementation.

------------------------------------------------------------
Analyze the entire project
------------------------------------------------------------

Scan the complete codebase including:

- backend
- frontend
- docs
- configuration
- environment loading
- AI runtime
- Prompt Builder
- LLM Integration
- Provider Registry
- Provider Adapter
- Runtime Facade
- Runtime Validation
- Runtime Eligibility
- Runtime Response Composer
- Runtime Response Post Processor
- Conversation Manager
- Workflow Engine
- Vector-less RAG

Also inspect:

- README.md
- AGENTS.md
- project-map
- feature-map
- implementation reports
- architecture documents
- AI context files

------------------------------------------------------------
Determine automatically
------------------------------------------------------------

From the implementation determine:

1. Which LLM providers are actually supported.

2. Which environment variables are required.

3. Which API key(s) must be configured.

4. Which model variable must be configured.

5. Whether runtime activation requires a feature flag.

6. Whether shadow mode exists.

7. Whether deterministic mode can be enabled.

8. Which configuration files load the environment.

9. How Provider Registry initializes.

10. How Runtime Facade activates.

11. How Conversation Manager hands control to the AI Runtime.

12. How Prompt Builder is invoked.

13. How LLM Generation is invoked.

14. How Runtime Validator executes.

15. How Runtime Eligibility executes.

16. How Runtime Response Composer executes.

17. How Runtime Response Post Processor executes.

18. Which log messages indicate successful initialization.

19. Which health endpoint(s) exist.

20. Which API endpoint(s) should be used for manual chatbot testing.

Do NOT guess.

If something is not implemented, explicitly state that.

------------------------------------------------------------
Update README
------------------------------------------------------------

Append a new section after the existing Backend/Frontend setup.

Title:

# AI Assistant Runtime Setup & Validation

The new section must include:

## 1. Overview

Explain how the completed AI Assistant architecture operates.

## 2. Required Environment Variables

Generate a table directly from the implementation.

Include:

- variable name
- required?
- description
- example value (use placeholders only, never real keys)

## 3. LLM Provider Configuration

Explain:

- where to place the API key
- how configuration is loaded
- how to switch providers (if supported)
- how to change the model

## 4. Backend Startup

Provide the exact commands required to start the backend with AI enabled.

## 5. Startup Verification

Explain exactly what successful startup logs should look like.

Explain what failures look like.

## 6. Runtime Verification

Explain how to verify:

- Provider Registry
- Runtime Facade
- Conversation Manager
- Prompt Builder
- LLM Integration

using logs and existing endpoints.

## 7. End-to-End Smoke Test

Provide step-by-step instructions.

Include sample prompts.

Include expected responses.

Include expected backend behaviour.

## 8. Phase 5 Validation

Document how to verify:

- Prompt Builder
- Context Collection
- Workflow Context
- RAG Context
- Final Prompt generation

## 9. Phase 6 Validation

Document how to verify:

- Provider Registry
- Provider Adapter
- LLM Generation
- Provider response
- Canonical response mapping

## 10. Phase 7 Validation

Document how to verify:

- Runtime Validation
- Runtime Eligibility
- Runtime Response Composer
- Runtime Response Post Processor
- Hybrid responses
- Deterministic fallback

## 11. Troubleshooting

Create a troubleshooting table covering:

- Missing API key
- Invalid model
- Invalid provider
- Authentication failure
- Timeout
- Network failure
- Empty response
- Validation failure
- Eligibility rejection
- Runtime fallback

For each issue include:

- symptoms
- probable cause
- resolution

------------------------------------------------------------
Documentation Requirements
------------------------------------------------------------

Do NOT redesign the implementation.

Do NOT modify any source code.

Do NOT change the architecture.

Only update README.md.

Everything must reflect the current implementation exactly.

If implementation differs from previous documentation, the implementation is the source of truth.

Generate documentation suitable for a developer who has never seen the project before and wants to configure a real LLM API key and validate:

- Phase 5
- Phase 6
- Phase 7

from scratch.