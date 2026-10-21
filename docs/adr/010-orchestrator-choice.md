# ADR-010: Orchestrator Choice

## Context

The pipeline consists of five sequential stages with clear dependencies
(Bronze ingestion → Silver cleaning → Data Quality validation → Gold
dimensional model) that today are run manually, in order, from the
terminal. This requires remembering the correct order, offers no automatic
retry on failure, and provides no single place to see whether a run
succeeded or failed.

## Options considered

- **Apache Airflow**: industry-standard orchestrator with a monitoring UI,
  robust scheduling, and wide adoption in Data Engineering roles. Requires
  its own metadata database and several running services (scheduler,
  webserver), adding operational overhead.
- **Dagster / Prefect**: lighter-weight, more modern developer experience,
  but less common in traditional Data Engineering job postings, which
  matters for a project meant to practice industry-standard tooling.
- **Sequential bash script**: no new dependencies, but no UI, no automatic
  retries, no real scheduling, and does not demonstrate competency with
  orchestration tooling.

## Decision

Apache Airflow, running in Docker (alongside MinIO), with a single DAG
representing the four pipeline stages.

## Trade-offs

Airflow adds operational complexity (more Docker services, more memory
usage) that would not be justified for a pipeline this simple if the only
goal were "make it work." This cost is accepted because the project's goal
is to demonstrate competency with an industry-standard orchestration tool,
not to solve the problem in the simplest possible way.

## Consequences

Airflow must be installed via Docker Compose, the same way MinIO was. The
DAG orchestrates calls to the existing Python/Spark/dbt scripts (via
`BashOperator`) without rewriting their internal logic — Airflow only
coordinates execution order, retries, and scheduling; it does not replace
the pipeline's business logic.