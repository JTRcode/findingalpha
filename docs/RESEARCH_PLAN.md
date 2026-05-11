# Research Plan

Date: 2026-05-10

## Purpose
Design a practical MVP for a personal stock screener and alpha research dashboard before implementing the screener. The project must prioritize evidence that signals predict future returns, not merely produce a ranked list.

## Research Questions
1. What market data is needed for the first MVP?
2. Which data APIs are best for each phase?
3. What broker/API path makes sense later for someone in Canada?
4. What storage approach should be used?
5. What backtesting approach should be used?
6. What dashboard/UI should be used?
7. What should the MVP actually do?
8. What initial signals belong in the first screener?
9. How should the system test whether signals have alpha?
10. What are the major risks and pitfalls?
11. What should not be built yet?

## Method
Use current public vendor documentation, official API docs where available, and conservative engineering assumptions. Treat pricing, limits, and terms as volatile and verify before subscribing or distributing derived data. Prefer official sources for facts about data coverage, rate limits, and broker support.

## Deliverables
- API comparison and recommendation
- Data requirements and snapshot schema
- Architecture options and selected MVP
- Alpha research methodology
- Risk/compliance notes
- Backtesting notes
- ADRs for major decisions
- Implementation plan

## Workflow
Research -> document -> decide -> implement -> test -> update docs.

Do not code the main screener until research docs and ADRs exist. After implementation, update docs if the built system differs from the plan.

## Assumptions
- User is in Vancouver, Canada.
- Phase 1 targets personal research for U.S. equities first.
- TSX/Canadian equities are desirable later but not required for the smallest MVP.
- End-of-day adjusted data is enough for the first alpha tests.
- No live trading or automated execution is allowed in phase 1.

