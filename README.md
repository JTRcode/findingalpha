# Finding Alpha

Research-first equity screener and alpha-validation dashboard.

Finding Alpha is a Python research system for turning discretionary swing-trading ideas into testable, versioned signal hypotheses. It ingests historical market data, calculates interpretable features, saves timestamped signal snapshots, and evaluates whether ranked candidates show predictive value across future return horizons.

The project is intentionally **not** a trading bot. Phase 1 is research-only: no broker execution, no live orders, no options automation, no crypto, no reinforcement learning, and no LLM-based trade decisions.

## Why This Project Exists

The goal is not simply to rank interesting stocks. The goal is to answer a harder question:

```text
Did the signal available at the time predict future returns,
or did it only look good after the fact?
```

The system currently focuses on **Setup B: Trend Pullback Continuation**:

```text
Buy strong pullbacks. Avoid chop. Test whether higher-quality pullbacks lead to better forward returns.
```

Setup B v1 is frozen as a baseline. Future v2 work is being proposed through research documents rather than silently changing the rules.

## What It Demonstrates

This repo is designed to showcase professional software engineering and research-engineering habits:

- modular data-provider interfaces
- reproducible local data pipeline
- timestamped signal snapshots
- interpretable feature engineering
- versioned setup definitions
- forward-return and bucket analysis
- SPY/QQQ-relative diagnostics
- date-declustered, outlier, and yearly-consistency checks
- Streamlit dashboard for research review
- ADRs and design docs
- explicit risk and compliance boundaries
- test coverage for features, scoring, providers, and research utilities

## Architecture

```text
Market data provider
        |
        v
Raw / processed Parquet storage
        |
        v
Feature generation
        |
        v
Signal scoring and Setup B gates
        |
        v
Signal snapshots + ranked outputs
        |
        v
Forward-return research diagnostics
        |
        v
Streamlit dashboard + research reports
```

Main source directories:

```text
src/trading_screener/
  data/          provider interfaces, storage, validation
  features/      technical and intraday feature generation
  signals/       scoring, screeners, Setup B gates
  research/      forward returns, bucket tests, slices, diagnostics
  backtesting/   simple basket research helpers
  dashboard/     Streamlit dashboard
```

## Current Research Workflow

1. Run a research scan over a ticker universe.
2. Save raw bars, processed bars, scored history, signal snapshots, and backtest artifacts.
3. Review Setup B candidates and charts in the dashboard.
4. Evaluate forward returns by bucket and slice.
5. Compare returns against SPY/QQQ.
6. Check date clustering, outlier dependence, and yearly consistency.
7. Record findings before changing signal logic.

## Setup B Research Status

Current baseline:

```text
setup_b_v1_broad_scanner
```

Setup B v1 has:

- broad scanner gate
- strict audit gate
- trend, pullback, volume, structure, and confirmation diagnostics
- continuous quality score
- chart audit view
- bucket diagnostics
- slice and interaction diagnostics
- benchmark-relative diagnostics
- outlier and yearly-consistency diagnostics

Current v2 proposal explores:

- RSI reset
- MACD histogram improvement
- ADX trend strength
- ROC acceleration
- slope confirmation
- high ATR as a context flag, not automatically a positive filter

See:

- [Setup B v1 research report](docs/SETUP_B_V1_RESEARCH_REPORT.md)
- [Setup B v2 proposal](docs/SETUP_B_V2_PROPOSAL.md)
- [Setup B v2 transition plan](docs/SETUP_B_V2_TRANSITION_PLAN.md)

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
```

## Example Daily Research Run

Small universe:

```bash
findingalpha --provider yfinance --universe liquid_large_caps --start 2024-01-01
```

Current S&P 500 universe:

```bash
findingalpha --provider yfinance --universe sp500_current --start 2011-01-01
```

Important caveat: `sp500_current` is not point-in-time. Historical tests using today’s S&P 500 constituents have survivorship bias. This is acceptable for application development and rough signal research, but not for final institutional claims.

## Launch Dashboard

```bash
streamlit run src/trading_screener/dashboard/app.py
```

Dashboard tabs:

- `Overview`: project flow and research-only scope
- `Daily Screener`: latest ranked signal snapshot
- `Setup B Research`: active playbook workflow, candidate chart review, gates, slices, diagnostics
- `Alpha Tests`: generic composite-score tests
- `Intraday Prototypes`: experimental 1-minute research layer

The dashboard reads saved artifacts from `data/`. It does not stream live data and cannot place orders.

## Intraday Research Providers

Alpaca and Massive/Polygon providers are market-data-only integrations.

Alpaca example:

```bash
findingalpha --provider alpaca --tickers SPY QQQ GLD TLT NVDA AAPL --start 2025-01-01 --intraday --intraday-start 2026-05-01 --intraday-timeframe 1Min --feed iex
```

Massive/Polygon example:

```bash
findingalpha --provider massive --tickers SPY QQQ GLD TLT NVDA AAPL --intraday-only --intraday --intraday-start 2026-05-01 --intraday-timeframe 1Min
```

Secrets belong in `.env` and must not be committed. See [.env.example](.env.example).

## Outputs

Generated files are written under `data/` and ignored by git except `.gitkeep` placeholders:

```text
data/raw/          raw provider outputs
data/processed/    normalized bars
data/features/     scored history
data/signals/      timestamped signal snapshots and setup candidates
data/backtests/    forward-return diagnostics and research artifacts
```

Key artifact families:

- `signal_snapshot_*`
- `daily_setup_candidates_*`
- `setup_b_filter_diagnostics_*`
- `setup_b_bucket_diagnostics_*`
- `setup_b_benchmark_relative_monthly_*`
- `setup_b_date_declustered_*`
- `setup_b_outlier_diagnostics_*`
- `setup_b_time_consistency_*`

## Tests

```bash
python3 -m pytest
```

Current test coverage includes:

- provider interfaces
- daily and intraday feature generation
- scoring
- Setup B gates and diagnostics
- forward-return calculation
- dashboard-adjacent formatting helpers
- universe loading

## Documentation Map

Core docs:

- [Design authority](docs/DESIGN.md)
- [Portfolio case study](docs/PORTFOLIO_CASE_STUDY.md)
- [Demo plan](docs/DEMO_PLAN.md)
- [Alpha research methodology](docs/ALPHA_RESEARCH.md)
- [Backtesting notes](docs/BACKTESTING_NOTES.md)
- [Risk and compliance](docs/RISK_AND_COMPLIANCE.md)
- [Research log](docs/RESEARCH_LOG.md)
- [Decision index](docs/DECISIONS.md)

Research docs:

- [Setup B v1 research report](docs/SETUP_B_V1_RESEARCH_REPORT.md)
- [Setup B v2 proposal](docs/SETUP_B_V2_PROPOSAL.md)
- [Setup B v2 transition plan](docs/SETUP_B_V2_TRANSITION_PLAN.md)
- [Survivorship bias](docs/SURVIVORSHIP_BIAS.md)
- [Universes](docs/UNIVERSES.md)

Planning docs:

- [Research plan](docs/RESEARCH_PLAN.md)
- [API comparison](docs/API_COMPARISON.md)
- [Data requirements](docs/DATA_REQUIREMENTS.md)
- [Architecture options](docs/ARCHITECTURE_OPTIONS.md)
- [Project plan](docs/PROJECT_PLAN.md)

## Portfolio Framing

Safe claim:

> This project demonstrates a research-first pipeline for testing interpretable equity-screening signals with reproducible artifacts, benchmark-relative validation, and documented decision controls.

Do not claim:

> This system has found a proven trading edge.

Known limitations:

- current S&P 500 universe is not point-in-time
- yfinance is a practical prototype provider, not institutional-grade data
- no full transaction-cost-aware execution simulation yet
- no sector-neutral or beta-neutral production research layer yet
- no live trading or broker execution by design

## Safety Boundary

This software is for personal research and engineering demonstration only. It is not financial advice and does not submit orders.
