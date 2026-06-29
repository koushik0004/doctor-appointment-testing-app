# Update Existing Implementation Report

Do NOT generate a new report.

Update the existing implementation report using only the target commits supplied.

Tasks:

1. Read the current implementation report.
2. Analyze only the specified commit range.
3. Identify:

   * Bug fixes
   * Stabilization work
   * Refactoring
   * Behavior changes
   * Integration improvements
4. Update only the affected sections.
5. Preserve all existing valid documentation.
6. Add a new section:

## Stabilization Summary

For each fix include:

* Issue
* Root Cause
* Implementation
* Files Changed
* Backward Compatibility

Also update:

* Files Modified
* Architecture Summary (only if behavior changed)
* Integration Points
* Design Decisions
* Known Limitations
* Manual Verification Summary

Do NOT:

* Rewrite the entire document.
* Remove valid historical information.
* Change unrelated sections.
* Document unimplemented features.

The updated report must accurately describe the implementation after the supplied commits while preserving implementation history.
