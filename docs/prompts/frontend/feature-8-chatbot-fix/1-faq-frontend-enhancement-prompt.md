# Feature: AI Chat Enhancement | Frontend | Appointment FAQ Rendering

## Objective

Update the AI Chat Widget to support the newly added backend intents.

This is only a UI synchronization task.

Do NOT redesign the chat widget.

---

## Requirements

### Appointment Help

Reuse the existing AppointmentHelpMessage component.

Ensure the enhanced booking instructions render correctly.

---

### Cancellation Help

Add rendering support for the new backend intent:

CANCEL_APPOINTMENT_HELP

Use the same visual style as Appointment Help.

Keep the UI consistent.

---

### Consultation Fee Clarification

When backend asks

"Which doctor's consultation fee would you like to know?"

Render it as a normal assistant message.

No special component required.

---

### Response Mapper

Update mapping if required.

Do not change existing doctor cards.

Do not change availability cards.

Do not modify booking navigation.

---

## Files Expected

frontend/lib/ai-widget/services/chat-response-mapper.ts

frontend/lib/ai-widget/components/MessageContentRenderer.tsx

frontend/lib/ai-widget/components/AppointmentHelpMessage.tsx (only if required)

---

## Acceptance Criteria

✔ Existing Doctor Cards unchanged

✔ Existing Availability Cards unchanged

✔ Booking navigation unchanged

✔ Appointment Help renders correctly

✔ Cancellation Help renders correctly

✔ Fee clarification renders as assistant message

✔ No UI redesign