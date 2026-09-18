\# ADR-004: Ingestion Scope — Full TMDB Catalog vs. Targeted Subset



\## Context



TMDB's full ID export contains 1,244,185 movie IDs, confirmed by this week's connector work, matching the "1.3M+ movies" figure cited in the project proposal. The Netflix Engagement Report, by contrast, lists 15,563 titles actually available on the platform. This raises the question of how much of TMDB's catalog the pipeline should actually ingest and process in later weeks.



\## Options considered



\- \*\*Full catalog (1.2M+ movies):\*\* ingest and process TMDB's entire catalog end-to-end.

\- \*\*Targeted subset:\*\* ingest a smaller, bounded set of titles, sized to be practical for local/self-hosted processing while still exercising the pipeline at meaningful scale.



\## Decision



Targeted subset, sized in the same order of magnitude as the Engagement Report (\~15–20K titles), rather than the full TMDB catalog.



\## Trade-offs



This project's goal is to demonstrate and learn a production-style data engineering pipeline for a portfolio, not to operate TMDB's catalog at full production scale. The ingestion, transformation, and modeling logic is identical regardless of volume — processing 1.2M rows instead of 20K would mainly add compute time and infrastructure cost on a self-hosted setup, without adding architectural complexity or additional skills demonstrated. Additionally, any analysis joining TMDB data against Netflix's own catalog is bounded by the Engagement Report's 15,563 titles — ingesting TMDB's full catalog would not produce more usable insight, since the vast majority of it has no Netflix engagement data to join against.



\## Consequences



Later weeks (Bronze/Silver ingestion, Spark processing, dbt modeling) will run against a bounded TMDB subset rather than the full ID list. The full-catalog capability remains demonstrated at the connector level (this week's `download\_movie\_ids.py` already proves the pipeline can fetch and handle all 1.2M+ IDs) even though downstream processing operates on a smaller working set.

