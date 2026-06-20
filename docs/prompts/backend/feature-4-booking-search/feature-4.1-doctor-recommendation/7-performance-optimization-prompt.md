TASK: Optimize Recommended Doctors Queries

Review implementation.

Add required indexes for:

- doctor specialty
- doctor active status
- doctor rating

Requirements:

- backward compatible
- no schema breaking changes

Create:

docs/analysis/feature-4.1/feature-4-recommended-doctors-performance.md

Include:

- indexes added
- query improvements
- expected performance impact