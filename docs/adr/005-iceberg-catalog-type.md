# ADR-005: Iceberg Catalog Type for Local Development

## Context

ADR-003 selected Iceberg as the table format for the Bronze layer. Iceberg requires a catalog — something that tracks which metadata file represents the current state of each table, so Spark knows what to read or write. Week 4 needs a catalog running locally on Windows, backed by MinIO, before the TMDB, Engagement Report, and Shareholder Letter connectors can be migrated from plain Parquet files to Iceberg tables.

## Options considered

- **Hadoop catalog:** metadata pointer lives inside the object store (MinIO) itself, next to the data. No extra service needed beyond MinIO.
- **REST catalog (e.g. Nessie, Iceberg's own REST catalog):** a separate service tracks metadata pointers over HTTP. Closer to how production platforms (including Netflix's own) run catalogs, but adds another container to configure and debug.
- **Hive Metastore:** a metastore service backed by a relational database (e.g. Postgres). Most infrastructure and the most unfamiliar concepts for a learner new to programming.

## Decision

Hadoop catalog, for Bronze and (unless revisited later) Silver and Gold as well.

## Trade-offs

The Hadoop catalog introduces the fewest new moving parts while Docker, MinIO, and Iceberg are all being learned in the same week, and needs no service beyond MinIO. This project's goal is portfolio/learning (ADR-004), not production parity, so the added realism of a REST catalog isn't worth the extra setup and debugging surface right now. The trade-off is that the Hadoop catalog doesn't support atomic table renames reliably across object stores (not a concern here, with no concurrent writers), and is less representative of a real multi-team production setup than a REST-based or metastore-based catalog.

## Consequences

`docker-compose.yml` only needs to run MinIO for Week 4 — no separate catalog container. Spark session config will set `spark.sql.catalog.<name>.type` to `hadoop` and point `warehouse` to an S3A path inside the `bronze` MinIO bucket. The underlying Iceberg table format is identical regardless of catalog type, so switching to a REST catalog later would only require reconfiguring the catalog pointer, not rewriting data. If a later week needs to simulate multi-team or multi-engine access, that should be revisited in a new ADR rather than changing this one in place.