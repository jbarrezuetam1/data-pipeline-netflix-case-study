# ADR-008: Data Quality Tooling — Great Expectations vs. Native dbt Tests

## Context

The project plan calls for data quality validation on the Silver layer, inspired by Netflix's internal Write-Audit-Publish pattern. Two realistic tools are available at this stage: Great Expectations, a standalone Python library for declarative data validation, or dbt's native test framework, which arrives naturally in Week 7 alongside the dimensional modeling work.

## Options considered

- **Great Expectations:** a dedicated validation library with a large set of built-in expectation types, HTML report output, and automatic data profiling. Runs against the Silver Iceberg tables via PySpark, independent of dbt.
- **Native dbt tests:** a simpler set of built-in tests (`not_null`, `unique`, `accepted_values`, `relationships`), declared in YAML next to the dbt models they validate. Would require pulling dbt's setup forward from Week 7.

## Decision

Great Expectations, as specified in the original project plan.

## Trade-offs

Great Expectations is the more capable tool, with a far wider range of expectation types and richer reporting than dbt's built-in tests, which matters for demonstrating a production-style Write-Audit-Publish pattern independent of the modeling layer. Keeping it separate from dbt also lets quality checks run directly against the Silver layer, before any dimensional modeling happens in Week 7, matching WAP's intent of auditing data before it is trusted downstream. The trade-off is maintaining two separate tools with different configurations (Great Expectations now, dbt next week) instead of one unified testing approach, and a steeper learning curve than dbt's simpler built-in tests.

## Consequences

Week 6 will install and configure Great Expectations against the three Silver Iceberg tables (`shareholder_letter_regional_breakdown`, `engagement_report`, `tmdb_movies`), independent of the dbt models built in Week 7. When dbt is introduced next week, its own native tests may be used for model-level checks specific to the gold layer, without replacing the Great Expectations suite already in place for Silver.

This implementation validates data already written to the Silver tables, rather than a pre-publish staging area — a simplified version
of the Write-Audit-Publish pattern appropriate for this project's batch-oriented, single-developer scale, where the risk of a bad write
reaching a shared table mid-correction is much lower than in a multi-team production system.