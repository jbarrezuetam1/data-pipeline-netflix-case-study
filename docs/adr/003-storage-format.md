\# ADR-003: Storage Format — Parquet vs. Iceberg vs. Delta Lake



\## Context



This week's connectors (TMDB, Engagement Report, Shareholder Letter) all write to Parquet. The question is whether plain Parquet files are enough for the bronze layer, or whether a table format is needed on top, given that sources will be re-ingested periodically and the pipeline will later have multiple stages reading/writing the same data.



\## Options considered



\- \*\*Parquet only:\*\* efficient columnar file format, but no transactions, no safe updates, no schema evolution, no history — just a folder of files.

\- \*\*Delta Lake:\*\* adds transactions, schema evolution, and time travel on top of Parquet. Tied closely to the Databricks ecosystem.

\- \*\*Iceberg:\*\* same core capabilities as Delta, but vendor-neutral and open, with strong Spark/MinIO support.



\## Decision



Apache Iceberg, for bronze and later layers. Parquet remains the underlying file format; Iceberg adds the table layer on top, matching the "MinIO + Iceberg" bronze layer already planned for Week 4.



\## Trade-offs



Plain Parquet doesn't support safe re-ingestion/updates, which this project needs (TMDB and the Engagement Report both change over time). Delta Lake was a valid alternative but was set aside to keep the self-hosted stack independent of Databricks, since the project compares the two separately in Week 10. Iceberg's cost is added setup complexity (a metadata/catalog layer) versus just writing files to a folder.



\## Consequences



This week's connectors still write plain Parquet to local folders — fine for Week 3. Starting Week 4, outputs move into Iceberg tables on MinIO; extraction/parsing logic itself doesn't change.

