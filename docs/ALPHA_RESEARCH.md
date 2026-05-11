# Alpha Research

Date: 2026-05-10

## Definition
Alpha means evidence that a signal predicts future returns beyond obvious exposures such as market beta, sector, size, liquidity, or generic momentum. In this project, alpha must be tested before any trading interpretation.

## Screen vs Signal vs Strategy vs Execution
- Screen: ranked list of interesting stocks.
- Signal: measurable hypothesis, such as 20-day momentum or relative volume.
- Strategy: portfolio rule using signals, sizing, rebalancing, costs, and risk constraints.
- Execution system: broker-connected order placement. This is excluded from phase 1.

## Forming a Signal Hypothesis
Each signal should have:
- intuitive reason it might work
- exact formula
- data availability timestamp
- expected horizon
- known failure modes
- planned robustness checks

## Forward Return Testing
For each date and ticker, calculate future returns over 1, 5, 10, 20, and 60 trading days when enough data exists. Rank scores cross-sectionally by date and compare future returns by quintile or decile.

## Daily Playbook Setup Testing
The project also tests rule-based daily setup candidates:

- Setup B: trend pullback continuation.
- Setup A: exhaustion pullback after an extended run.
- Setup C: failed bounce reversal.

These are sequence-aware prototypes based on multi-day features such as 60-day trend, pullback from recent high, relative volume, moving-average structure, extension, bounce attempts, and downside confirmation. They are research labels, not trade instructions.

The scanner uses mandatory gates plus scores. A candidate should pass core structure requirements before it can appear:

- Setup B requires strong trend, controlled pullback, structure hold, volume dry-up, and confirmation.
- Setup A requires extension, stretch, high volume, failed strength, and downside reversal.
- Setup C requires weak structure, bounce attempt, failed reclaim, downside volume, and downside confirmation.

The default candidate threshold is intentionally selective at `0.75`, and the dashboard includes a threshold slider for exploration.

The dashboard includes a Setup B chart inspection workflow. For each selected candidate it displays daily candles and volume before and after the candidate date, so the rule capture can be visually audited against the intended playbook.

Setup B is now split into explicit pass/fail gates:

- Trend gate: strong 60-day trend, above 50/200 SMA, and 20 SMA above 50 SMA.
- Pullback gate: 2-6 down days in 7 sessions, 1.5-7% below the 10-day high, orderly pullback, and no large red breakdown candles.
- Volume dry-up gate: current and recent pullback volume are lower than prior volume.
- Structure gate: price holds the 20/50 SMA area, stays above 50 SMA, and 20-day momentum has not broken.
- Confirmation gate: positive close in the upper daily range and reclaim of prior high or close above 20 SMA.

The dashboard shows these gates as pass/fail for each selected Setup B chart candidate. Each gate also has a continuous 0-1 quality score. Gates determine eligibility; quality scores rank eligible candidates.

Setup B quality scoring:

- Trend quality: stronger 60-day momentum and distance above 50 SMA.
- Pullback quality: pullback depth closest to roughly 4%, pullback duration closest to roughly 4 sessions, and orderly pullback behavior.
- Volume quality: current and recent pullback volume dry up relative to prior volume.
- Structure quality: price holds the 20/50 SMA area.
- Confirmation quality: close strength, prior-high reclaim, and positive daily return.

Setup B bucket diagnostics report:

- count by quality bucket
- mean and median forward return
- win rate
- standard deviation and standard error
- t-stat versus zero
- top bucket minus bottom bucket mean spread
- top bucket minus bottom bucket median spread
- win-rate spread
- rough interpretation label

Interpretation is only a screen. Promising diagnostics still need visual review, out-of-sample testing, benchmark-relative returns, and transaction-cost checks.

## Bucket Analysis
For each score bucket:
- average forward return
- median forward return
- win rate
- count of observations
- top bucket vs bottom bucket spread
- top bucket vs SPY/QQQ forward return

## Simple Basket Test
Create an equal-weight long-only basket of top-ranked names on each rebalance date. Track cumulative returns, drawdown if feasible, turnover, and cost sensitivity. This is a research backtest, not an execution simulation.

## Avoiding Overfitting
- Start with interpretable baseline features.
- Keep parameter counts small.
- Use train/test time splits and walk-forward checks.
- Avoid selecting features only because they worked in one backtest.
- Report weak and negative findings.
- Track performance decay over time.

## Separating Alpha from Exposures
Later phases should compare results against:
- SPY and QQQ
- sector ETF or sector-neutral buckets
- market-cap/liquidity groups
- simple momentum baselines
- beta estimates

## Minimum Evidence for a Promising Signal
A signal is only promising if it:
- shows monotonic or economically sensible bucket behavior
- works across multiple forward horizons or has a clear horizon profile
- survives out-of-sample periods
- is not concentrated in a handful of observations
- remains plausible after transaction-cost sensitivity
- has stable behavior across regimes or clear regime dependence

## Why One Backtest Is Not Enough
One backtest can be a data-mined coincidence. The project must preserve signal snapshots and evaluate future outcomes to learn whether live research-time scores had predictive value.

## Paper Trading Before Supervised Trading
Paper trading validates process, latency, data availability, logging, risk controls, and operator discipline without risking capital. It still does not prove live profitability.

## Automated Trading Exclusion
Automated trading is excluded from the MVP because the project has not yet validated any signal, transaction-cost model, risk controls, broker behavior, or compliance assumptions.
