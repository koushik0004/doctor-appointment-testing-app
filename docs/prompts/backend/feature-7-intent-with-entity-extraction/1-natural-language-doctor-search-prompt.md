Task: Implement AI Chat Phase 3 - Natural Language Doctor Search.

Objective:

Upgrade chat intelligence from simple intent detection to intent + entity extraction.

Current State:

* Intent detection exists.
* Doctor search exists.
* Availability lookup exists.
* Appointment navigation exists.

Requirements:

Supported entities:

* specialization
* gender
* fee range
* date
* time preference
* clinic location

Supported examples:

"Need a female cardiologist"

"Find a dermatologist tomorrow"

"Show doctors under ₹200"

"Need a pediatrician after 5 PM"

"Find available neurologists near Soho clinic"

Implementation:

1. Create entity extraction layer.

2. Use deterministic parsing.

3. Do NOT use:

   * OpenAI
   * LLM
   * RAG

4. Extract entities into structured model.

Example:

{
"specialization": "Cardiology",
"gender": "Female",
"date": "Tomorrow"
}

5. Query existing doctor and appointment services.

6. Return structured search results.

7. Add unit tests.

8. Maintain backward compatibility.

Deliverables:

* Entity extraction module
* Search filters
* API enhancements
* Tests
* Implementation summary
