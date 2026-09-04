\# ADR-002: ETL vs. ELT



\## Context



Following ADR-001, raw data lands first in the bronze layer of the lakehouse, as-is, before any cleaning or business logic is applied. This raises the question of where transformation logic should actually run: before data is loaded into the lake (ETL), or after, on top of the already-landed raw data (ELT). One nuance to resolve up front: the PDF source (Netflix's shareholder letter) cannot be loaded as a table without some initial structural parsing, extracting tables from the PDF into rows and columns. This needs to be distinguished from business-logic transformation, which is a separate decision.



\## Options considered



ETL: transform data (cleaning, business rules) before it ever reaches its destination, discarding the raw form. Common when storage is expensive or limited, when sensitive data must be masked before it is ever persisted, or in traditional on-prem warehouse setups.



ELT: load raw data first, transform afterwards, in place, keeping the original untouched. Favored when storage is cheap, when the same raw data may need to be reprocessed differently over time, and when powerful compute engines such as Spark and dbt are available to do the transformation work after landing.



\## Decision



ELT, with one clarification: PDF and XLSX structural parsing, turning an unstructured file into rows and columns, such as extracting a table from the shareholder letter with pdfplumber, counts as part of Extract, not Transform, since it makes no business decisions about the data. Actual business-logic transformation, such as cleaning, calculations, joins, and aggregates, only happens after landing, in the silver and gold layers.



\## Trade-offs



None of the three sources contain sensitive data that must be masked before storage, so ETL's main justification for this project does not apply. The dataset's volume of 30 million or more rows and the availability of Spark and dbt as compute engines make ELT more practical, since transformation logic can run at scale after landing rather than in a constrained pre-load step. The main benefit is flexibility: because raw data is preserved intact, anyone, including future teammates or other projects, can build a different pipeline on top of the same raw data without needing to re-extract it from the original sources. The trade-off is that raw storage volume is higher than it would be under ETL, since unprocessed data is kept indefinitely rather than discarded after transformation.



\## Consequences



Ingestion connectors are only responsible for extraction and structural parsing, such as API calls, XLSX reads, and PDF table extraction. No business logic is allowed at this stage. All cleaning, validation, and modeling logic lives in the processing (silver) and modeling (gold) layers, built with PySpark and dbt, running against data that has already landed in the lakehouse.

