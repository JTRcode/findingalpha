# Backtesting Notes

Date: 2026-05-10

## Minimum Acceptable Standards
- Use adjusted prices for return tests unless testing raw execution prices explicitly.
- Ensure the signal uses only data available at or before the signal timestamp.
- Save signal snapshots before evaluating forward returns.
- Include observation counts for every bucket.
- Compare against SPY/QQQ where relevant.
- Report turnover and cost sensitivity when moving from signal tests to strategy tests.

## Research Backtest vs Execution Simulation
A research backtest tests whether a signal predicts future returns. An execution simulation tests whether an order-placement strategy could realistically capture those returns after fills, spreads, slippage, latency, and broker constraints. Phase 1 only requires research backtests.

## Lookahead Bias Avoidance
- Do not use future bars in feature calculations.
- Shift forward returns so the return window begins after the signal date.
- Lag fundamentals, earnings, news, and filings unless exact release timestamps are available.
- Do not use current constituents for historical universes without acknowledging survivorship bias.

## Split and Dividend Handling
Use adjusted close for returns and indicators when available. If only raw OHLCV exists, flag the data and avoid long historical return conclusions around corporate actions.

## Transaction Costs and Slippage
MVP reports before-cost bucket results and a simple basis-point transaction-cost sensitivity for the top-ranked basket. Later phases should test richer cost assumptions, spread estimates, and turnover impact. Quote/bid-ask data will eventually improve this.

## Forward Return Bucket Testing
For each signal date:
1. Rank tickers by score.
2. Assign quintiles or deciles.
3. Calculate 1, 5, 10, 20, and 60 trading-day forward returns.
4. Aggregate mean, median, win rate, counts, and top-bottom spread.
5. Compare top bucket to benchmark forward return.

## Backtesting Framework Comparison
- pandas/vectorized: simplest, inspectable, ideal for forward-return tests; limited execution realism.
- vectorbt: very fast vectorized portfolio research; can encourage parameter sweeps and overfitting if misused.
- backtrader: mature event-driven framework; better for strategy simulation, heavier for signal validation.
- zipline-reloaded: point-in-time pipeline ideas, but setup/data ingestion complexity is higher.
- bt: portfolio backtesting convenience; less focused on cross-sectional signal diagnostics.
- custom event-driven: maximum control; too expensive before phase 1 signals are validated.

## Recommendation
Use pandas/vectorized forward-return analysis for MVP. Consider vectorbt or an event-driven engine later only after signals justify strategy-level simulation.
