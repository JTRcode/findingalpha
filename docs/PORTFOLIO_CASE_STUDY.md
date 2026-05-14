# Portfolio Case Study: Finding Alpha

Date: 2026-05-14
Status: Portfolio-facing summary

## One-Sentence Summary
Finding Alpha is a research-first equity screener and alpha-validation dashboard that turns discretionary swing-trading setups into versioned, testable signal hypotheses.

## Problem
Many screeners produce ranked stock lists, but a ranked list does not prove predictive value.

The project asks:

```text
Given only information available at signal time, did higher-ranked candidates have better future returns?
```

The system is built to support research discipline:

- save signal snapshots at run time
- evaluate forward returns later
- compare against benchmarks
- document assumptions and decisions
- avoid live trading until research evidence is stronger

## Role And Scope
This is a personal software engineering and research-engineering project.

Built components:

- Python package and CLI
- provider interface for market data
- yfinance daily provider
- Alpaca and Massive/Polygon market-data-only providers
- Parquet storage
- feature engineering layer
- Setup B signal logic
- forward-return research diagnostics
- Streamlit dashboard
- tests
- architecture docs, ADRs, research reports

Explicitly excluded:

- live order submission
- broker execution
- automated trading
- options strategy automation
- crypto trading
- reinforcement learning
- LLM-based trading decisions

## Architecture

```text
Providers -> Storage -> Features -> Signals -> Research Diagnostics -> Dashboard
```

Layer responsibilities:

- `data`: fetch, normalize, validate, and store provider data
- `features`: compute reusable market facts
- `signals`: define versioned setup gates, scores, and explanations
- `research`: evaluate forward returns, buckets, slices, benchmarks, outliers, and consistency
- `dashboard`: inspect saved artifacts without defining research rules

Design principle:

```text
Research rules live in signal/research layers, not in the dashboard.
```

## Research Methodology
The project focuses on **Setup B: Trend Pullback Continuation**.

Setup B v1:

- broad scanner creates a research sample
- strict gate labels cleaner discretionary matches
- score ranks broad candidates
- diagnostics explain gates and feature values
- v1 is frozen before proposing v2

Research tests include:

- forward returns at 1D, 5D, 10D, 20D, and 60D
- score buckets and top-vs-bottom spreads
- SPY/QQQ-relative returns
- date-declustered diagnostics
- outlier diagnostics
- yearly consistency
- slice and interaction analysis
- chart review

## Current Findings
Current evidence is exploratory, not a trading claim.

Findings so far:

- Setup B v1 has more useful ranking behavior at 20D/60D than at 1D/5D.
- SPY-relative results are stronger than QQQ-relative results.
- high ATR is the strongest hardened slice so far.
- stricter confirmation alone is not clearly better.
- stronger volume dry-up is not currently the leading v2 driver.
- v2 should test momentum-reset features before changing gates.

Current v2 proposal explores:

- RSI reset
- MACD histogram improvement
- ADX trend strength
- ROC acceleration
- slope confirmation
- high ATR as context

## Engineering Highlights
Professional practices demonstrated:

- versioned signal methodology
- ADRs for major decisions
- no secrets in repo
- generated research artifacts ignored by git
- timestamped outputs for reproducibility
- tests for calculation logic
- explicit safety/compliance docs
- design document to prevent uncontrolled scope growth
- research log documenting findings and changes

## Dashboard
The Streamlit dashboard is a local research viewer.

It supports:

- latest signal snapshot review
- Setup B candidate table
- candlestick and volume chart around candidate dates
- pass/fail gate audit
- condition-level debug table
- forward-return buckets
- benchmark-relative diagnostics
- slice and interaction review
- outlier and time-consistency diagnostics

It does not:

- stream live market data
- place orders
- connect to broker execution APIs
- make trading decisions

## Demo Strategy
A demo is useful, but it should be read-only and sanitized.

Recommended employer-facing demo:

- short screen recording or GIF
- screenshots on portfolio page
- optional hosted Streamlit app using small bundled sample artifacts
- no API keys
- no private `.env`
- no full local `data/` folder
- clear disclaimer that it is research-only

Avoid exposing:

- personal API keys
- full local research data
- live broker accounts
- anything that implies automated trading

## Limitations
Important limitations are documented rather than hidden:

- current `sp500_current` universe has survivorship bias for historical tests
- yfinance is practical for prototyping but not institutional-grade
- sector-neutral and beta-neutral diagnostics are not complete
- transaction-cost modeling is still basic
- no point-in-time fundamentals or delisted-symbol database yet
- historical evidence is exploratory and not proof of future edge

## Portfolio Positioning
Good portfolio summary:

> Built a research-first equity screening platform that converts discretionary trading setups into versioned, testable signal hypotheses using timestamped snapshots, forward-return analysis, benchmark-relative diagnostics, and a Streamlit research dashboard.

Good interview emphasis:

- how the project avoids lookahead bias
- why signal snapshots matter
- why v1 was frozen before v2
- how benchmark-relative tests change interpretation
- why live trading is intentionally excluded
- how documentation and ADRs keep the project maintainable

Avoid saying:

> I built a profitable trading bot.

Say instead:

> I built the research infrastructure needed to test whether a setup deserves further investigation.

## Next Improvements
Highest-value next steps:

1. Add a small sanitized sample dataset for public demo mode.
2. Add screenshots or a short video walkthrough.
3. Add sector metadata and sector-neutral diagnostics.
4. Add beta/rebound exposure checks for high-ATR candidates.
5. Build v2 diagnostic comparison artifacts for RSI/MACD/ADX/ROC/slope features.
6. Improve README screenshots and architecture diagrams after demo data is stable.
