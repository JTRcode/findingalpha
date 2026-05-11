# ADR 0003: Dashboard Framework

Date: 2026-05-10
Status: Accepted

## Context
The project needs a local dashboard to inspect ranked screens, features, signal snapshots, and alpha evaluation summaries.

## Options considered
- Streamlit: Fastest Python-native data app, minimal frontend work, good for local research.
- Dash: More structured and flexible, but more boilerplate.
- FastAPI + React/Next.js: Scalable production app path, too heavy before research workflow is proven.
- Jupyter notebooks: Excellent exploration, weaker as a repeatable dashboard.
- CLI-only: Simple, but less useful for scanning and filtering results.

## Decision
Use Streamlit for the MVP dashboard.

## Rationale
Streamlit is the simplest route to a usable local research UI and works naturally with pandas/Parquet outputs.

## Consequences
The dashboard is not a production multi-user app. More complex state, permissions, and deployment may require a future framework change.

## Review triggers
- Need multi-user deployment.
- Need complex interactions or role-based access.
- Need API-backed frontend separation.
- Dashboard performance becomes a bottleneck.

