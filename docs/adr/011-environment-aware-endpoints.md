# ADR-011: Environment-Aware Service Endpoints for Dual Execution Contexts

## Status
Accepted

## Context
The pipeline's Bronze and Silver layer scripts (Weeks 4-7) connect to MinIO
via PySpark's S3A connector, and the Gold layer connects via dbt-duckdb.
These scripts were originally developed and tested running natively on
Windows, where MinIO is reachable at `localhost:9000`.

In Week 8, the same scripts were orchestrated by Apache Airflow running
inside Docker containers. Inside a container, `localhost` refers to the
container itself, not the host machine or the MinIO container, so a
hardcoded `localhost:9000` endpoint does not resolve to MinIO when the
scripts run inside Airflow's containers. MinIO is reachable there only by
its Docker service name (`minio:9000`), once the Airflow containers join
MinIO's Docker network.

During implementation, one of the three `spark_session.py` copies
(`week5-silver-layer`) was missed when applying this change, which was not
caught until the orchestrated DAG run consistently failed on the Silver
tasks with `Connection refused` errors — a failure that looked, at first
glance, like a resource or networking problem, and took significant
troubleshooting time to trace back to the hardcoded endpoint.

## Options Considered

1. **Hardcode the endpoint per environment** — maintain two versions of
   each script (one for native execution, one for Docker). Rejected: doubles
   the maintenance burden and the two versions would drift apart over time.

2. **Always connect via the Docker service name (`minio:9000`)** — rejected
   because it would break native execution entirely, which is still used
   for local development and debugging.

3. **Read the endpoint from an environment variable, with a `localhost`
   default** — the endpoint becomes `os.environ.get("MINIO_ENDPOINT",
   "http://localhost:9000")`. Native execution needs no environment variable
   set (falls back to `localhost`), and Airflow's `docker-compose.yml` sets
   `MINIO_ENDPOINT=http://minio:9000` for the containers. Accepted.

## Decision
Use environment-variable-based endpoint resolution, with a `localhost`
default, in every script that connects to MinIO (`spark_session.py` in
Weeks 4-6, and `profiles.yml` in Week 7 via dbt's `env_var()` function).
The same pattern is used for both the full URL needed by PySpark's S3A
connector (`MINIO_ENDPOINT`) and the host:port-only form needed by
dbt-duckdb's S3 secret (`MINIO_ENDPOINT_HOST`).

## Consequences

**Positive:**
- One codebase runs unmodified in both execution contexts (native
  development and Docker-orchestrated).
- No environment variables need to be set for native execution — the
  default matches the existing local setup.

**Negative:**
- The pattern must be applied consistently across every script that opens
  a connection to MinIO. Missing it in even one file produces a failure
  (`Connection refused`) whose symptoms can easily be mistaken for a
  resource, network, or MinIO availability problem, since the error occurs
  only inside the orchestrated context and the script works perfectly when
  run natively — exactly what happened with `week5-silver-layer/spark_session.py`
  in this project.
- Mitigation going forward: before adding or orchestrating a new script
  that connects to MinIO, explicitly check it uses `os.environ.get(...)`
  for its endpoint rather than a hardcoded value.