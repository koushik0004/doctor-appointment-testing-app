# Feature: AI Chat Enhancement | Backend | Appointment FAQ Support

## Objective

Enhance the existing deterministic AI Chat backend by improving appointment-related intents.

This is an incremental enhancement to the existing Intent Detection + Entity Extraction architecture.

Do NOT introduce:
- RAG
- Vector DB
- LLM
- Workflow engine
- Conversation memory
- Appointment booking automation

---

## Requirements

### 1. Improve Appointment Help

Expand the existing `APPOINTMENT_HELP` intent.

Recognize queries such as:

- How to book appointment?
- How do I book an appointment?
- Appointment process
- Booking process
- Book appointment help
- How can I consult a doctor?

Return a structured appointment help response explaining:

1. Choose a doctor
2. Select available date
3. Choose time slot
4. Enter patient details
5. Confirm appointment

---

### 2. Add Cancellation Help Intent

Introduce a new intent:

`CANCEL_APPOINTMENT_HELP`

Recognize phrases like:

- How to cancel appointment?
- Cancel appointment
- Cancel booking
- Appointment cancellation
- How do I cancel my booking?

Return a structured help response.

Current application doesn't support AI cancellation, therefore guide the user to the existing cancellation flow (or support page if available).

Do NOT implement cancellation logic.

---

### 3. Consultation Fee Clarification

Current behaviour:

Works only when doctor name exists.

Improve behaviour.

If doctor name exists

Return existing doctor detail response.

If doctor name is missing

Examples

- Consultation fee
- Doctor fee
- How much consultation fee?
- Consultation charges
- Doctor charges

Return

"Which doctor's consultation fee would you like to know?"

Never guess the doctor.

---

### 4. Improve Intent Detection

Expand keyword matching.

Booking

- appointment
- book
- booking
- consultation
- consult
- reserve
- schedule

Cancellation

- cancel
- cancellation
- cancel booking
- cancel consultation

Fee

- fee
- consultation fee
- consultation charges
- doctor charges
- cost
- price

---

## Files Expected

Modify only when required.

backend/app/services/chat_intent_detector.py

backend/app/services/chat_service.py

backend/app/schemas/chat.py

backend/tests/test_chat_api.py

backend/tests/test_chat_intent_detector.py

---

## Acceptance Criteria

✔ Existing doctor search unchanged

✔ Existing availability search unchanged

✔ Existing entity extraction unchanged

✔ Appointment Help works

✔ Cancellation Help works

✔ Fee clarification works

✔ Existing APIs remain backward compatible

✔ All tests pass