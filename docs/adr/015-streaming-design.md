# ADR-015: Streaming Ingestion (Design Only)

**Status:** Accepted

## Context

The proposal lists a streaming pipeline as a stretch goal, inspired by the
real-time event processing that large streaming platforms run. Every source
in this project is batch-oriented: the Engagement Report (Excel), the
Shareholder Letter (PDF), and the TMDB API. None of them emits events, so a
real streaming workload does not exist in this project.

## Decision

Streaming is documented as a **design only** and is not implemented.

Proposed design, if a real event source existed:

1. **Ingestion:** events (for example, playback events) are published to a
   Kafka topic.
2. **Processing:** Spark Structured Streaming reads the topic and writes to
   the Bronze layer as Iceberg tables, reusing the Medallion layers already
   built.
3. **Downstream:** Silver, Gold, data quality checks, and the dashboard stay
   unchanged. Only the Bronze ingestion step differs from the batch pipeline.

Options considered:

- **Implement a simulated stream** (a script producing fake events into
  Kafka in Docker Compose). Rejected: it adds infrastructure and effort
  without a real source, and it would not teach anything the batch
  pipeline does not already show.
- **Design only (chosen).** It keeps the scope realistic and still shows
  where streaming would fit in the architecture.

## Trade-offs

- The project does not demonstrate hands-on streaming skills.
- The design is untested, so it may hide integration problems (for example,
  schema evolution or exactly-once writes to Iceberg).

## Consequences

- No new services are added to Docker Compose.
- The architecture is ready for streaming at the Bronze layer: the Silver
  and Gold layers would not need to change.
- This ADR is the only deliverable for the stretch goal.