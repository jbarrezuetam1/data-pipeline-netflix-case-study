# ADR-007: Partitioning Strategy for Silver Tables

## Context

The project plan calls for partitioning as part of the Silver layer
transformation. Partitioning splits a table's physical files into
subfolders by the value of a chosen column (e.g. release year), so
queries that filter on that column can skip reading irrelevant files
("partition pruning").

## Options considered

- **Partition the Silver tables** (e.g. `tmdb_movies` by release year,
  `engagement_report` by release year) to demonstrate the technique and
  match the original project plan.
- **Do not partition**, given the current data volume.

## Decision

Do not partition the Silver tables at this stage.

## Trade-offs

Partitioning meaningfully improves query performance on large tables
with millions or billions of rows, by letting Spark skip whole
folders of files that don't match a filter. At this project's current
scale (60, 15,563, and 19,516 rows across the three Silver tables),
every table already fits comfortably in a handful of files, so
partition pruning would have no measurable benefit — the overhead of
reading "the wrong partition" barely exists when there's effectively
one partition's worth of data to begin with. Partitioning now would
add complexity (deriving a partition column, deciding how to handle
NULL values in that column, e.g. the unknown release date for "Prison
Break: Season 1") without a corresponding performance gain.

## Consequences

Silver tables are written without a partitioning scheme. If a later
stage of the project introduces TMDB's full catalog (per ADR-004's
full-catalog capability) or otherwise grows table volume
significantly, this decision should be revisited.