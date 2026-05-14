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

The scanner now uses a two-level structure:

- Broad scanner gate: looser eligibility that captures plausible Setup B research candidates.
- Strict gates: higher-quality audit labels that show whether the original stricter playbook conditions passed.
- Quality score: continuous ranking score used to compare candidates after broad eligibility.

A broad candidate should still have trend, pullback, volume, structure, and confirmation evidence, but it does not need every strict gate to pass before it can appear:

- Setup B requires strong trend, controlled pullback, structure hold, volume dry-up, and confirmation.
- Setup A requires extension, stretch, high volume, failed strength, and downside reversal.
- Setup C requires weak structure, bounce attempt, failed reclaim, downside volume, and downside confirmation.

The default candidate threshold is `0.60`, and the dashboard includes a threshold slider for exploration. Higher thresholds can be used for stricter chart review, but alpha tests should avoid stacking too many filters until sample sizes are large enough.

The dashboard includes a Setup B chart inspection workflow. For each selected candidate it displays daily candles and volume before and after the candidate date, so the rule capture can be visually audited against the intended playbook.

Setup B is now split into explicit pass/fail gates:

- Trend gate: strong 60-day trend, above 50/200 SMA, and 20 SMA above 50 SMA.
- Pullback gate: 2-6 down days in 7 sessions, 1.5-7% below the 10-day high, orderly pullback, and no large red breakdown candles.
- Volume dry-up gate: current and recent pullback volume are lower than prior volume.
- Structure gate: price holds the 20/50 SMA area, stays above 50 SMA, and 20-day momentum has not broken.
- Confirmation gate: positive close in the upper daily range and reclaim of prior high or close above 20 SMA.

The dashboard shows the broad scanner gate, strict match flag, and strict gate pass/fail status for each selected Setup B chart candidate. Each strict gate also has a continuous 0-1 quality score. Broad eligibility determines whether a candidate can be researched; quality scores and strict gates rank and explain candidates.

Setup B quality scoring:

- Trend quality: stronger 60-day momentum and distance above 50 SMA.
- Pullback quality: pullback depth closest to roughly 4%, pullback duration closest to roughly 4 sessions, and orderly pullback behavior.
- Volume quality: current and recent pullback volume dry up relative to prior volume.
- Structure quality: price holds the 20/50 SMA area.
- Confirmation quality: close strength, prior-high reclaim, and positive daily return.

The current Setup B implementation is versioned as `setup_b_v1_broad_scanner`. If the rules or weights change, the new version should be documented so old signal snapshots are not mixed with new definitions.

The generic `composite_score` is separate from the playbook setup scores. It is a broad technical ranking score for the latest screener table, while `daily_setup_b_trend_pullback_score` is the rule-based Setup B research score. They should not be interpreted as the same signal.

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

Setup B slice diagnostics split candidates by:

- market regime
- pullback depth
- pullback duration
- volume dry-up strength
- trend quality
- confirmation quality
- ATR/volatility

The goal is to determine whether poor aggregate results hide a conditional edge, such as Setup B only working when SPY is in a positive regime or when the pullback depth is in a narrow range.

Market regime uses SPY when present, otherwise QQQ. Daily runs fetch benchmark context symbols alongside the selected universe so market regime can be calculated even when the universe is `sp500_current`, which does not include SPY or QQQ. Candidates remain restricted to the selected universe.

Interaction slices test combinations of conditions, including:

- market regime x confirmation quality
- market regime x ATR
- confirmation quality x ATR
- confirmation quality x pullback depth
- pullback depth x pullback duration
- volume dry-up x confirmation quality

These should be used carefully because each added condition reduces sample size and increases data-mining risk.

Setup B variants combine the most interesting slice findings into stricter research labels:

- `conservative_continuation`: positive benchmark regime, low/medium ATR, strong confirmation, and at least moderate volume dry-up.
- `momentum_rebound`: positive benchmark regime, high ATR, strong confirmation, and strong volume dry-up.
- `high_atr_watch`: positive benchmark regime, high ATR, and at least moderate confirmation.
- `other_setup_b`: broad Setup B candidates that do not match the stricter variants.

Variants are not trade rules. They are diagnostic groups for testing whether Setup B works better under narrower conditions. Variant diagnostics include absolute forward returns and SPY-relative forward returns when SPY data is available.

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
