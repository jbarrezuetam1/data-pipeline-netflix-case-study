# ADR-006: Local Bronze Layer Storage — MinIO + Iceberg on Docker

## Context

ADR-003 selected Iceberg as the table format. ADR-005 selected the Hadoop
catalog as the way Iceberg tracks table metadata. Both decisions still
needed a concrete, runnable storage backend for local development: an
S3-compatible object store to hold the actual Iceberg data and metadata
files, reachable from Spark running on Windows.

## Options considered

- **MinIO in Docker:** a self-hosted, S3-compatible object store, run as a
  single container via `docker-compose.yml`. Free, requires no cloud
  account, and lets Spark talk to it exactly as it would talk to real AWS
  S3 (same `s3a://` protocol, same client libraries).
- **Real AWS S3:** the actual cloud service Netflix and most production
  platforms use. Would require an AWS account, incurs storage/API costs
  even at small scale, and ties the project to a specific cloud provider
  for a stage of the project that is meant to be run and re-run locally
  while learning.
- **Local filesystem (no object store):** write Iceberg tables directly to
  a folder on disk, skipping S3-style storage entirely. Simplest to set
  up, but does not exercise the object-store access patterns (`s3a://`
  paths, endpoint/region/credentials configuration) that a real deployment
  would use, which is part of what this project is meant to demonstrate.

## Decision

Run MinIO locally via Docker, exposed on `localhost:9000` (S3 API) and
`localhost:9001` (web console), with a single `bronze` bucket created
manually through that console. Spark connects to it using the Hadoop S3A
connector (`hadoop-aws`), configured with path-style access and an
explicit (arbitrary) region, since MinIO does not use AWS regions but the
AWS SDK still requires one to sign requests.

## Trade-offs

MinIO in Docker keeps the whole Bronze layer free, self-hosted, and fully
reproducible from `docker-compose.yml` — anyone cloning the repo can run
one command and get the same storage layer running locally. It also
forces the project to use the same connection patterns (endpoint,
credentials, path-style access) that a real S3 deployment would need,
which is closer to the production-style pipeline this project is meant to
demonstrate than writing straight to local disk would be. The trade-off is
that data only exists inside a Docker volume on this machine: there is no
built-in redundancy, backup, or multi-machine access, which would matter
for a real production deployment but does not matter for a
portfolio/learning project (ADR-004).

## Consequences

`docker-compose.yml` in the project root must be running (`docker compose
up -d`) before any Bronze layer script executes. All three Week 3/4
connectors (TMDB, Engagement Report, Shareholder Letter) now write Iceberg
tables to `local.bronze.*` instead of plain Parquet files in
`week3-ingestion/output/`. The `spark_session.py` helper in
`week4-bronze-layer/` centralizes the MinIO/Iceberg connection
configuration, so later weeks (Silver, Gold) can reuse it rather than
repeating these settings in every script.