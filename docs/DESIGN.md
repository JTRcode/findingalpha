# Project Design

Date: 2026-05-13
Status: Active design authority

## Purpose
This document is the short design authority for the project. Use it before adding features, changing screener logic, or expanding the dashboard.

The project is a personal alpha research system for testing whether interpretable stock-screening signals have predictive value for future returns. It is not a live trading system.

## Current Phase
Phase 1: research, screening, chart review, and alpha validation.

Allowed:
- historical market data ingestion
- provider interfaces
- feature calculation
- interpretable screener scores
- signal snapshots
- forward-return evaluation
- benchmark-relative diagnostics
- Streamlit dashboard views
- local research reports

Not allowed:
- live order submission
- broker execution
- automated trading
- options trading logic
- crypto trading
- reinforcement learning
- LLM-based trade decisions
- high-frequency tick prediction
- social media sentiment scraping

## Design Principles
- Research first: every signal must be a testable hypothesis, not a trading claim.
- Small core, many outputs: keep calculation logic centralized and let outputs reuse it.
- Version rules: if a signal definition changes, give it a new version instead of silently changing history.
- Prefer interpretable features before ML.
- Keep provider-specific code inside provider modules.
- Keep dashboard code as presentation logic; it should not define research rules.
- Keep signal snapshots so future outcomes can be compared to what was known at the time.
- Avoid adding indicators, slices, tabs, or providers unless they answer a current research question.

## System Layers

```text
Market data providers
        |
        v
Data storage and validation
        |
        v
Feature generation
        |
        v
Signal and setup scoring
        |
        v
Research evaluation
        |
        v
Dashboard and reports
```

### Data Layer
Owned by:
- `src/trading_screener/data/`
- `src/trading_screener/data/providers/`
- `src/trading_screener/events/`

Responsibilities:
- fetch raw historical data
- isolate vendor-specific behavior
- validate required fields
- save raw and processed data separately
- never expose API secrets

This layer must not contain screener logic or trading decisions.

### Feature Layer
Owned by:
- `src/trading_screener/features/`

Responsibilities:
- calculate reusable market features such as returns, moving averages, ATR, volume ratios, pullback measures, and intraday features
- avoid setup-specific business decisions where possible

This layer should produce facts, not decide whether something is tradable.

### Signal Layer
Owned by:
- `src/trading_screener/signals/`

Responsibilities:
- convert features into scores, setup labels, gates, explanations, and risk flags
- keep setup definitions explicit and versioned
- avoid hidden dashboard-only logic

Current important signal definitions:
- `composite_score`: generic technical ranking score.
- `setup_b_v1_broad_scanner`: current Setup B trend-pullback research definition.
- `daily_setup_b_trend_pullback_score`: Setup B-specific research score.

The generic composite score and Setup B score are separate signals. Do not treat them as the same ranking.

### Research Layer
Owned by:
- `src/trading_screener/research/`
- `src/trading_screener/backtesting/`
- `data/backtests/`

Responsibilities:
- calculate forward returns
- evaluate score buckets
- compare against SPY/QQQ when available
- test slices and interactions
- report sample size, win rate, mean, median, and stability
- avoid treating one good backtest as proof

Research diagnostics are evidence-gathering tools. They are not execution rules.

### Dashboard Layer
Owned by:
- `src/trading_screener/dashboard/`

Responsibilities:
- display latest screens, setup candidates, charts, forward-return diagnostics, and reports
- make existing calculations easier to inspect
- avoid defining new signal rules inside UI code

If the dashboard needs a new metric, add it to the appropriate data, feature, signal, or research layer first.

## Current Product Shape
The project should remain a focused research dashboard, not a full trading platform.

Primary workflow:
1. Run `findingalpha` for a universe.
2. Save raw data, processed data, scored history, signal snapshots, setup candidates, and backtest artifacts.
3. Open the Streamlit dashboard.
4. Review latest ranked stocks and Setup B candidates.
5. Inspect forward returns, buckets, slices, benchmark-relative tests, and charts.
6. Record findings before changing the signal.

## Setup B Design
Setup B is the active research setup.

Mental model:
Buy strong pullbacks, avoid chop, and verify whether higher-quality pullback candidates have better future returns.

Current version:
- `setup_b_v1_broad_scanner`

Status:
- frozen baseline for research comparison
- documented in `docs/SETUP_B_V1_RESEARCH_REPORT.md`
- v2 transition process documented in `docs/SETUP_B_V2_TRANSITION_PLAN.md`

Structure:
- broad scanner gate: creates a research sample
- strict gate: original higher-quality all-gates match
- individual gates: trend, pullback, volume dry-up, structure, confirmation
- continuous quality score: ranks eligible broad candidates
- slices and variants: diagnostics only
- audit tables: show raw feature values beside broad and strict thresholds for chart-by-chart debugging
- filter diagnostics: show independent condition pass rates and cumulative gate funnels across the universe
- indicator diagnostics: RSI, MACD, ADX, ROC acceleration, moving-average slope, and regression slope are feature diagnostics only

Do not keep changing Setup B thresholds in place. If a revised definition is needed, create `setup_b_v2_*`, document what changed, and keep old snapshots interpretable. Before implementing v2, follow `docs/SETUP_B_V2_TRANSITION_PLAN.md`.

## Prototype Setups
Setup A and Setup C are prototype labels only. They may remain in generated artifacts for future research, but the dashboard should not present them as equal to the active Setup B workflow.

Dashboard rule:
- Setup B is the default daily research view.
- Setup A/C rows should be hidden by default or grouped under prototype wording.
- Prototype setup scores should not clutter the main Setup B candidate table.
- Intraday setup work is also prototype status until intraday data coverage and rule definitions are stable.

## Change Control
Before adding or changing a feature, answer:
- What research question does this answer?
- Which layer owns it?
- Does this duplicate an existing metric or diagnostic?
- Does it change a frozen signal definition?
- Does it need a new signal version?
- Does it need an ADR?
- What test should prove it works?
- What doc should be updated?

Use an ADR for major changes to:
- data providers
- storage
- signal methodology
- backtesting/research methodology
- dashboard framework
- broker or execution path

Use `docs/RESEARCH_LOG.md` for research findings and smaller implementation decisions.

## Anti-Slop Rules
- No new dashboard tab without a clear user workflow.
- No new indicator unless it supports an active hypothesis.
- No new slice unless it has enough sample size to be useful.
- No ML until baseline signals have stable, documented evidence.
- No provider addition unless it improves data quality, coverage, cost, or reliability for a current need.
- No duplicate calculations in multiple layers.
- No silent edits to historical signal definitions.
- No execution code in phase 1.

## Documentation Rules
When implementation changes the design:
- update this file if system structure, layer ownership, signal definitions, or scope changes
- update `docs/RESEARCH_LOG.md` when a research finding or cleanup decision is made
- update ADRs for major architecture decisions
- update `docs/ALPHA_RESEARCH.md` when methodology changes
- update `README.md` when user-facing commands or workflows change

## Current Open Design Questions
- Should the dashboard hide generic `composite_score` on Setup B-specific pages?
- Should heavy diagnostics become opt-in for large universes?
- Should sector metadata be added for sector-neutral tests?
- Should intraday research stay separate from daily Setup B until data coverage is stable?
