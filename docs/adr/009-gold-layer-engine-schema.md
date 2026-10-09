# ADR-009: Gold Layer Engine and Schema Shape

## Context

Following the Silver layer (Week 5) and data quality validation (Week 6,
ADR-008), the project needs a Gold layer: a dimensional model built with
dbt, as planned in the project proposal. Two decisions were needed before
building any models: which engine dbt should run against, and whether
the dimensional model should follow a star or snowflake schema.

## Options considered

### Engine
- **DuckDB:** no additional server or container; reads Iceberg tables
  directly from MinIO via DuckDB's native Iceberg extension, using the
  same Hadoop catalog (path-based) already in place (ADR-005). Runs
  embedded in the same Python process as dbt.
- **PostgreSQL:** requires an additional Docker container and a separate
  ETL step to load Silver data from Iceberg into Postgres before dbt can
  model it, duplicating data outside the lakehouse.
- **Spark (via Thrift Server):** queries the lakehouse directly, closer
  to how Trino/Spark would be used in a real production stack (as in
  Netflix's own architecture), but requires running and maintaining an
  additional long-running Spark Thrift Server process, and dbt's "session"
  connection method (which skips the Thrift Server) is explicitly marked
  experimental and unsupported.

### Schema shape
- **Star schema:** a central fact table connected directly to dimension
  tables, with no intermediate normalization. Simple, fast to query, some
  redundancy within dimensions.
- **Snowflake schema:** dimensions further normalized into sub-dimensions,
  reducing redundancy at the cost of more joins per query.

## Decision

DuckDB as the dbt engine, with a star schema for the dimensional model.

## Trade-offs

DuckDB avoids both the extra infrastructure of Postgres (another
container, another thing that can be "not running" when picking the
project back up) and the operational overhead of a Spark Thrift Server,
while still reading Iceberg tables directly from MinIO with no data
duplication — unlike Postgres, which would require copying Silver data
into a separate system. The trade-off is that DuckDB is less
"enterprise-typical" than querying through Spark/Trino the way Netflix's
real stack would, though its Iceberg support is now officially generally
available and widely adopted in the industry.

For schema shape, the project's data volumes (tens of thousands of rows,
not millions) do not benefit meaningfully from snowflake's storage
savings, while a star schema keeps the model easy to query and easy to
explain in a portfolio context — directly in line with the decision
already made not to partition the Silver tables at this scale (ADR-007).

## Consequences

Gold layer dbt models will be built using the `dbt-duckdb` adapter,
reading Iceberg tables from `local.silver.*` directly via DuckDB's
Iceberg extension. The resulting model will have one or more fact tables
connected directly to dimension tables, with no intermediate
normalization layers.