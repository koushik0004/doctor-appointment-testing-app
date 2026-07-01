# Phase 04 Manual Test Checklist

Date: 2026-07-01

## Purpose

This checklist covers manual validation for the Vector-less RAG prototype in the existing AI chat widget. It focuses on:

- Positive scenarios
- Negative scenarios
- Edge cases
- Regression coverage
- Workflow interaction
- Existing chatbot functionality

## Preconditions

- Run the app in the normal local development setup.
- Confirm the frontend, backend, and seeded database are available.
- Open the app in a browser with devtools available for network and console inspection.
- Use the existing global AI widget mounted in the app shell.
- Verify the chat widget can send messages and receive responses before starting deeper checks.

## Positive Scenarios

- [ ] Send a basic greeting and confirm the assistant responds normally.
- [ ] Ask a knowledge question that should map to an active knowledge document and confirm the reply is knowledge-backed.
- [ ] Confirm the assistant reply includes the minimal source footer on text responses.
- [ ] Confirm the source footer shows the retrieved document title.
- [ ] Confirm the source footer shows the source path.
- [ ] Confirm the source footer shows matched terms when the backend supplies them.
- [ ] Ask a second knowledge question in the same session and confirm the footer updates to the new source.
- [ ] Ask a question that matches a Markdown knowledge source and verify the reply still renders as plain assistant text.
- [ ] Ask a question that matches a JSON knowledge source and verify the reply still renders as plain assistant text.
- [ ] Confirm the widget remains responsive after multiple knowledge-backed exchanges.

## Negative Scenarios

- [ ] Ask a question that should not match any knowledge document and confirm the assistant falls back to the existing generic deterministic response.
- [ ] Ask an intentionally unrelated question and confirm no knowledge footer appears.
- [ ] Use a typo-heavy message and confirm it does not incorrectly resolve to an unrelated knowledge source.
- [ ] Ask a question that looks similar to a supported topic but should still fall back when no document is a good match.
- [ ] Trigger a response without `knowledge_source` metadata and confirm the UI does not render an empty or broken footer.
- [ ] Confirm the widget does not show a knowledge footer on structured workflow cards.

## Edge Cases

- [ ] Send the same knowledge question with different casing and confirm the same source is selected.
- [ ] Send a knowledge question with extra punctuation and confirm the same source is selected.
- [ ] Use plural or simple inflection variants and confirm deterministic retrieval still works as expected.
- [ ] Ask a multi-sentence message with one knowledge-relevant clause and confirm the top matching document is still selected.
- [ ] Ask a message with several candidate terms and confirm the highest-ranked document is selected.
- [ ] Ask a very short query such as a keyword fragment and confirm the system either selects the expected document or falls back cleanly.
- [ ] Ask a very long query and confirm the widget remains stable and the response still renders.
- [ ] Send repeated messages quickly and confirm responses stay ordered and readable.
- [ ] Confirm the footer remains visually readable when the source path is long.
- [ ] Confirm the footer does not overflow or overlap the assistant text on small screens.

## Workflow Interaction

- [ ] Start an active booking workflow from chat and confirm knowledge retrieval does not replace the workflow response.
- [ ] Continue a booking workflow with follow-up fields and confirm workflow state still wins over knowledge fallback.
- [ ] Ask a knowledge question after completing a workflow response and confirm the next non-workflow reply can still surface a knowledge source.
- [ ] Ask a cancellation or appointment lookup question and confirm the existing workflow/card behavior is preserved.
- [ ] Confirm that workflow cards still navigate or hand off exactly as before the Vector-less RAG changes.
- [ ] Confirm that a knowledge-backed reply does not overwrite workflow metadata in the widget state.

## Existing Chatbot Functionality

- [ ] Confirm the assistant still answers greetings and general help prompts.
- [ ] Confirm doctor list responses still render as structured doctor cards.
- [ ] Confirm doctor availability responses still render as structured availability cards.
- [ ] Confirm doctor profile responses still work for exact and partial `Dr. <first-name>` mentions.
- [ ] Confirm appointment-help style responses still render the existing help card.
- [ ] Confirm booking completion still redirects into the standard confirmation flow.
- [ ] Confirm appointment-related navigation still uses the existing booking store and not a new chat-only screen.
- [ ] Confirm the widget does not introduce console errors when rendering knowledge-backed replies.
- [ ] Confirm the widget still works after a page refresh.

## Regression Checks

- [ ] Verify the chat widget still mounts on all pages where it previously appeared.
- [ ] Verify existing API requests still succeed through the frontend proxy.
- [ ] Verify the assistant still handles non-knowledge deterministic fallback responses.
- [ ] Verify the assistant still preserves existing workflow metadata in response handling.
- [ ] Verify structured response rendering remains unchanged for doctor, availability, and help cards.
- [ ] Verify the existing appointment booking redirect continues to land on the confirmation page.
- [ ] Verify knowledge source rendering does not affect message ordering or scroll behavior.
- [ ] Verify the UI remains backward compatible when the backend omits optional knowledge metadata.

## Recommended Manual Test Pass

Use this sequence for a compact end-to-end pass:

1. Open the app and verify the AI widget loads.
2. Send a greeting and confirm the assistant replies normally.
3. Ask one question that should resolve to knowledge and confirm the source footer appears.
4. Ask one unrelated question and confirm the generic fallback still works.
5. Start a booking workflow and confirm the workflow path still wins.
6. Complete or cancel the workflow and confirm the widget returns to normal chat behavior.
7. Recheck doctor cards, availability cards, and booking confirmation behavior for regressions.

