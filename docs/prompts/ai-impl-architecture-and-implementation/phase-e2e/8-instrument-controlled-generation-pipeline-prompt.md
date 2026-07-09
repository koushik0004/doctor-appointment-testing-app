The current routing is correct.

Do NOT modify ConversationManager routing.

Do NOT modify Execution Policy.

Do NOT modify Prompt Builder.

Do NOT modify Provider Adapter.

Do NOT modify Transport.

------------------------------------------------------------
OBJECTIVE
------------------------------------------------------------

Instrument the Controlled Generation pipeline.

Whenever run_controlled_generation() does NOT return SUCCEEDED,

emit a structured diagnostic log explaining exactly why.

Capture:

- execution mode
- generation_available
- provider readiness
- provider selected
- orchestration started
- prompt builder executed
- provider adapter executed
- transport invoked
- HTTP request sent
- HTTP response received
- validation result
- eligibility result
- composition result
- post processor result
- fallback reason
- exception type
- exception message

If controlled generation returns SKIPPED or FAILED,

log the exact stage where execution stopped.

Never swallow the reason.

Do not change routing.

Do not change business logic.

Do not change fallback behavior.

Only improve diagnostics.

Generate an implementation report explaining every new diagnostic.