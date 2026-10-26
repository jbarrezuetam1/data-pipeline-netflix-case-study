# ADR-014: BI Tool Choice (Power BI)

## Status
Accepted

## Context
The project needs a dashboard that presents the main consumption and
business indicators from the Gold layer: hours viewed by content type, top
10 titles by hours viewed, hours viewed by genre, and revenue by region and
quarter. The proposal leaves the choice of BI tool open (Netflix's real
equivalent is Tableau).

The goal of this decision is to use a tool that is widely adopted in
industry, so that the dashboard also serves as evidence of a commonly
requested data skill, in line with the portfolio purpose of the project.

## Decision
Use **Power BI Desktop**.

Reasons:
- **Industry adoption.** Power BI is one of the most widely used BI tools in
  data roles, which makes the dashboard relevant beyond this project.
- **Same concepts as Netflix's stack.** The work (measures, dimensions,
  filters, interactive visuals) transfers directly to Tableau, the tool
  named in the proposal's architecture.
- **No extra infrastructure.** It runs natively on the development machine,
  adding no containers to a setup that is already memory-constrained (see
  ADR-011 and the Week 8 troubleshooting).

## Trade-offs
- **Reproducibility.** Power BI Desktop requires Windows and a manual
  install, and the dashboard is a binary `.pbix` file that cannot be
  reviewed line by line in Git. It is the one deliverable that cannot be
  reproduced through Docker Compose.
- **Native connectivity.** Power BI has no native DuckDB connector, so the
  connection to the Gold layer needs an extra step (an ODBC driver or an
  exported file), to be resolved during implementation.
- **Sharing.** Publishing an interactive dashboard online requires a Power
  BI Service account, which is out of scope. The dashboard is delivered as
  the `.pbix` file plus exported images or a PDF.

## Consequences
- The repository will include the `.pbix` file and exported images of the
  dashboard, and the README will state how to open it.
- The limits on reproducibility are stated explicitly in the project
  documentation.