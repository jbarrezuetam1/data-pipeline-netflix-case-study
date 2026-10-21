# ADR-012: CI/CD Testing and Deployment Strategy

## Status
Accepted

## Context
The pipeline (Weeks 1-8) has, so far, only been verified manually: running
scripts natively, inspecting output tables, and triggering Airflow DAG runs
by hand. Week 8's troubleshooting (ADR-011) showed the cost of that approach
directly — a hardcoded endpoint in one script went undetected until a full
orchestrated run failed, hours into debugging what looked like a resource
problem.

This week introduces Continuous Integration via GitHub Actions: an
automated workflow that checks code quality and correctness on every push,
without needing to manually spin up Docker, Spark, or Airflow. Three
decisions had to be made about its scope, since a project at this stage
does not have (and does not need) a production-grade test suite.

## Decision

**1. Test depth: lightweight unit tests.**
The CI runs small, fast unit tests against individual functions (e.g., a
single data-cleaning or parsing function), not full integration tests that
would require spinning up MinIO, Spark, or Airflow inside the GitHub
Actions runner. This matches the project's entry-level scope: it catches
clear logic errors and regressions quickly, without the cost and
complexity of standing up the full infrastructure stack inside CI.

**2. Gating: lint and tests block, image build does not.**
The workflow runs three jobs: lint, tests, and a Docker image build. Lint
and tests must pass for the workflow to report success — a failure in
either is a clear, actionable signal that something in the code is wrong.
The image build job always runs regardless of the other jobs' outcome,
since its purpose is just to confirm the Dockerfile still produces a valid
image, not to gate code quality.

**3. CD scope: build and publish the image to GitHub Container Registry
(ghcr.io).**
The project runs locally via Docker Compose, with no live server to deploy
to, so "continuous deployment" in the traditional sense does not apply.
Instead, CD here means publishing the built image to GitHub Container
Registry (ghcr.io) on pushes to `main`. This is a modest but real instance
of the publish step a production CD pipeline would perform, kept
proportional to what the project actually needs.

## Trade-offs

**What this gives up, compared to a production setup:**
- No integration tests against real MinIO/Spark/Airflow — a bug that only
  manifests when components interact (like the Week 8 endpoint issue)
  could still slip past CI. Unit tests reduce this risk but do not
  eliminate it.
- No actual deployment target — the published image to ghcr.io is a
  demonstration of the publish step, not evidence of a live, continuously
  deployed service.

**What this gives, proportional to project scope:**
- Fast feedback (seconds, not the manual multi-step verification used
  through Week 8) on a meaningful subset of bugs.
- A real, working example of a lint → test → build → publish pipeline,
  which is the shape of CI/CD regardless of project scale.

## Consequences
- Every script with testable logic should have at least one corresponding
  unit test, added incrementally as the project adds code deliverables.
- The GitHub Actions workflow becomes the first thing to check when a push
  breaks something, before falling back to the kind of manual, step-by-step
  debugging used for the Airflow orchestration layer.