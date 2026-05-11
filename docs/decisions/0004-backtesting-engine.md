# ADR 0004: Backtesting Engine

Date: 2026-05-10
Status: Accepted

## Context
The first alpha research need is to test whether scores predict future returns, not to simulate detailed order execution.

## Options considered
- pandas/vectorized forward-return analysis: Simple, inspectable, ideal for score buckets and forward horizons. Limited execution realism.
- vectorbt: Fast vectorized portfolio tests and parameter sweeps. Powerful but can encourage overfitting.
- backtrader: Mature event-driven backtesting. More complex than needed for cross-sectional score validation.
- zipline-reloaded: Useful pipeline concepts, but setup and data ingestion are heavier.
- bt: Convenient portfolio backtesting, less focused on signal diagnostics.
- custom event-driven engine: Flexible but too much work before signal validation.

## Decision
Use pandas/vectorized forward-return analysis for MVP, with a simple long-only top-ranked basket research test. Consider vectorbt or an event-driven framework later.

## Rationale
The MVP should answer whether signals predict 1, 5, 10, 20, and 60 day returns. A transparent pandas implementation is easiest to test and audit.

## Consequences
MVP results are research backtests, not execution simulations. Transaction costs and slippage are approximate until quote/order simulation is added.

## Review triggers
- A signal passes baseline validation.
- Need detailed rebalancing, fills, slippage, or order types.
- Need large parameter sweeps.
- Need intraday/event-driven strategies.

