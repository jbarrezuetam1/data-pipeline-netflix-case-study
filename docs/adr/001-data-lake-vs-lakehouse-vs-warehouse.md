\# ADR-001: Data lake vs. lakehouse vs. data warehouse



\## Context

The project needs to store three heterogeneous sources, with the TMDB catalog alone scaling to 30M+ rows once cast, crew, and keywords are included, and growing every week as new titles are added. A simple save-and-overwrite approach does not work: keeping a full weekly backup of the entire dataset to preserve history would waste enormous amounts of storage, since only a small fraction of the catalog actually changes week to week.



\## Options considered

Data warehouse (e.g., PostgreSQL): fast queries and strong consistency, but requires a fixed schema up front and becomes expensive and rigid at this volume. It also does not naturally fit raw PDF/XLSX ingestion.



Data lake (e.g., plain files in MinIO/S3): cheap and flexible enough to hold tens of millions of rows and any file format as-is, but offers no built-in guarantees. If a correction script, such as one fixing a bug in the genre field, fails halfway through rewriting files, the dataset is left in a mixed, inconsistent state, and anyone querying it at that moment gets back wrong numbers without knowing it. This is called a dirty read.



Lakehouse (e.g., MinIO + Apache Iceberg): combines the low-cost, flexible storage of a data lake with ACID guarantees on top, so partial writes are never visible to readers.



\## Decision

Lakehouse (MinIO + Apache Iceberg).



\## Trade-offs

A data warehouse is too costly and rigid for this row volume and for ingesting semi-structured sources like the PDF. A plain data lake is cheap enough for the volume, but the risk of dirty reads during corrections is not acceptable when the same data feeds business decisions. The lakehouse gets the low storage cost of the lake while adding the atomicity and consistency guarantees that make weekly incremental updates and corrections safe. The added cost is the extra complexity of learning and operating Iceberg on top of plain storage.



\## Consequences

Raw and processed data will be appended incrementally, not replaced, as new TMDB records arrive each week, using Iceberg tables to guarantee that a reader never sees a half-finished write. This also shapes how data quality corrections are applied later in the project: fixes must be committed atomically, not applied file by file.

