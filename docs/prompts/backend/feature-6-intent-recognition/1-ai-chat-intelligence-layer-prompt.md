Task: Enhance the existing AI Chat backend to support doctor search and appointment assistance using deterministic business logic.

Context:

The project is a Doctor Appointment Application.

Backend Stack:

* FastAPI
* SQLAlchemy
* SQLite

Current State:

* Chat API already exists.
* Chat widget is integrated with frontend.
* Basic message exchange is working.

Objective:

Add an intent-driven chat service that can answer doctor-related queries using existing database data.

Requirements:

1. Create an Intent Detection Layer.

Supported Intents:

* SHOW_DOCTORS_BY_SPECIALIZATION
* SHOW_AVAILABLE_DOCTORS
* SHOW_DOCTOR_DETAILS
* APPOINTMENT_HELP
* UNKNOWN

2. Detect intents using keyword-based matching only.

Do NOT use:

* LLM
* OpenAI
* RAG
* Vector DB

3. Reuse existing Doctor and Appointment services whenever possible.

4. Supported Example Queries:

"Show cardiologists"

"Find dermatologist"

"Who is available tomorrow?"

"What is Dr. Sarah Jenkins fee?"

"How do I book an appointment?"

5. Return structured response format:

{
"intent": "SHOW_DOCTORS_BY_SPECIALIZATION",
"message": "Found 2 cardiologists.",
"data": []
}

6. Keep business logic in a dedicated Chat Service layer.

7. Add clear separation:

API Layer
→ Chat Service
→ Intent Detector
→ Doctor/Appointment Services

8. Add proper error handling.

9. Add unit tests for intent detection and chat service.

10. Do not break existing chat functionality.

Deliverables:

* Intent detection module
* Chat service enhancement
* API integration
* Response schemas
* Unit tests
* Implementation summary
