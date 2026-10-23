# ADR-013: Self-Hosted Open-Source Stack vs. Managed Platform (Databricks)

## Status
Accepted

## Context
The pipeline (Weeks 1-9) was built on a self-hosted, open-source stack:
MinIO, Apache Iceberg, Apache Spark, Airflow, dbt and Great Expectations,
all run locally through Docker. The project proposal asks for one
representative slice of the pipeline to be replicated on a managed
platform (Databricks Free Edition), to inform, not replace, the main
implementation.

The slice chosen was the Engagement Report, from Bronze to Gold. Raw data
was uploaded to a Unity Catalog volume, and the Bronze, Silver and Gold
layers were rebuilt as Delta tables (`workspace.bronze`, `workspace.silver`
and `workspace.gold`) using the same business logic as the self-hosted
version. Row counts were consistent across layers (15,563 rows).

## Options Considered

1. **Self-hosted open-source stack as the base**, with Databricks documented
   as an alternative.
2. **Databricks as the base** going forward.

## Observations from the replicated slice

| Criterion | Self-hosted stack | Databricks Free Edition |
|---|---|---|
| Setup | Docker Compose, MinIO, S3A and catalog configuration in `spark_session.py` | Sign-up and a notebook; `spark` is ready to use |
| Resources | Limited by a 16 GB laptop; Spark JVMs and Airflow competed for RAM | Serverless compute, with daily quotas |
| Table format | Apache Iceberg | Delta Lake |
| Catalog | Hadoop catalog over MinIO | Unity Catalog |
| Raw files | MinIO bucket | Volume, uploaded manually through the UI |
| Dependencies | `requirements.txt` | `%pip install` plus a Python restart |
| Business logic | SQL / PySpark | Nearly identical; only table names and `USING iceberg` changed |

Spark version also differed (4.0.1 locally, 4.2.0 on Databricks), with no
effect on the logic.

The main finding is subjective but consistent: building the medallion
layers on Databricks had fewer barriers. Everything lives in one
ecosystem, there is no infrastructure to operate, and iteration is faster.

## Limits of this comparison
- **Not like-for-like.** On Databricks, existing, already-tested Silver and
  Gold logic was translated. On the self-hosted stack, the logic and the
  infrastructure were both built and debugged from scratch (including the
  resource and networking issues in ADR-011). Part of the smoother
  experience on Databricks reflects that difference.
- **Only one slice was replicated.** TMDB, data quality (Great Expectations),
  orchestration, and dbt were not rebuilt on Databricks, so the comparison
  says nothing about them.
- **Free Edition constraints.** Serverless compute only, daily quotas, no
  custom storage location (MinIO cannot be connected), limited outbound
  internet, non-commercial use, and no support or SLA.
- **Not measured:** cost at scale and vendor lock-in.

## Decision
Keep the **self-hosted open-source stack as the base implementation**, and
document Databricks as a credible alternative. This follows the project
scope (the managed-platform comparison informs and does not replace) and
keeps the repository reproducible by anyone with Docker, without requiring
a Databricks account or being tied to a non-commercial Free Edition.

For a team that prioritizes development speed and does not want to operate
infrastructure, Databricks is the recommended option based on this
experiment.

## Consequences

**Positive:**
- The repository remains fully reproducible with Docker Compose.
- Full control over every component, which is also what makes the project
  useful as evidence of data engineering skills.
- The comparison is documented honestly, including its limits.

**Negative:**
- The self-hosted stack carries operational cost: setup time, resource
  tuning, and troubleshooting that a managed platform would remove.
- The conclusions about a full migration remain untested.