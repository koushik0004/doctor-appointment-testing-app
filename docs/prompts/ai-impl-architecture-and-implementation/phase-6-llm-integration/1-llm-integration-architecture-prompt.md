Phase 6.1 — LLM Integration Architecture

Objective:
Introduce a new provider-neutral LLM Integration layer as an architectural boundary only.

Requirements:
- Do NOT integrate any LLM SDK.
- Do NOT add provider-specific code.
- Do NOT modify Conversation Manager, Workflow Engine, Vector-less RAG, or Prompt Builder.
- Keep the layer inactive and disconnected from the production runtime.
- Define clear module boundaries, responsibilities, package structure, and documentation.
- Ensure zero behavior changes, zero API changes, zero database changes, and full backward compatibility.
- Prototype-first and implementation-ready for future phases.