---
name: generate-impl-report
description: Read the last commit range and generate a concise implementation report in markdown format.
---

# Generate Implementation Report

You are documenting a completed implementation.

Goal:
Produce a technical implementation report describing the current implementation.

Instructions:

1. Analyze only the target commits (or the provided commit range).
2. Inspect all changed files.
3. Identify:

   * Files Added
   * Files Modified
   * Files Removed
4. Summarize the implemented architecture.
5. Describe all integration points.
6. List reused business services/APIs.
7. Document important design decisions.
8. Document current limitations.
9. Explain why the implementation is backward compatible.
10. Generate a concise but comprehensive markdown report.

The report must contain:

* Files Added
* Files Modified
* Architecture Summary
* Integration Points
* Business APIs Reused
* Design Decisions
* Known Limitations
* Manual Verification Summary
* Suggested Next Phase (only if the implementation is complete)

Rules:

* Base the report only on the inspected commits.
* Do not invent features.
* Do not redesign the architecture.
* Do not include future work that is not planned.
* Keep the report implementation-focused.
