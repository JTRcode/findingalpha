# Setup B v2 Transition Plan

Date: 2026-05-14
Status: Proposed process

## Purpose
This document defines what must happen before Setup B v2 is designed, coded, or promoted.

The goal is to prevent accidental overfitting and avoid silently changing `setup_b_v1_broad_scanner`.

## Current Baseline
Frozen baseline:

```text
setup_b_v1_broad_scanner
```

Current diagnostic-only candidates:
- RSI reset
- MACD histogram improvement
- ADX trend strength
- ROC acceleration
- moving-average slope
- linear-regression slope
- high ATR / volatility regime
- pullback depth regime

These features are allowed to be studied, but they are not Setup B v1 filters.

## Pre-v2 Checklist
Before designing Setup B v2:

- Run Setup B v1 over the target daily universe.
- Confirm the generated artifacts include `setup_b_indicator_diagnostics`.
- Review Setup B filter diagnostics to understand which v1 gates are already restrictive.
- Review candidate charts across multiple dates, sectors, and volatility regimes.
- Identify which diagnostic features improve outcomes and which do not.
- Confirm enough candidates remain after any proposed diagnostic filter.
- Compare absolute and SPY/QQQ-relative forward returns.
- Check date-declustered diagnostics so one crowded date does not dominate.
- Check monthly stability.
- Check outlier dependence with trimmed means and top/bottom 1% contribution.
- Check yearly consistency versus SPY/QQQ.
- Record findings in `docs/RESEARCH_LOG.md`.

## Required Artifacts
Use these files before proposing v2:

```text
data/backtests/setup_b_score_buckets_*.parquet
data/backtests/setup_b_bucket_diagnostics_*.parquet
data/backtests/setup_b_top_bottom_spreads_*.parquet
data/backtests/setup_b_filter_diagnostics_*.parquet
data/backtests/setup_b_indicator_diagnostics_*.parquet
data/backtests/setup_b_slices_*.parquet
data/backtests/setup_b_interaction_slices_*.parquet
data/backtests/setup_b_benchmark_relative_monthly_*.parquet
data/backtests/setup_b_date_declustered_*.parquet
data/backtests/setup_b_outlier_diagnostics_*.parquet
data/backtests/setup_b_time_consistency_*.parquet
data/signals/daily_setup_candidates_*.parquet
data/features/scored_history.parquet
```

## Research Questions
Primary:
- Do Setup B candidates with RSI reset outperform candidates without RSI reset?
- Do candidates with rising MACD histogram outperform candidates with falling MACD histogram?
- Do candidates with stronger ADX outperform weak-trend candidates?
- Does positive ROC acceleration help, or does it chase late moves?
- Do rising SMA or regression slopes improve trend quality?

Secondary:
- Are improvements visible at 5D, 10D, and 20D?
- Are improvements still present after SPY/QQQ-relative comparison?
- Are improvements stable month to month?
- Are improvements broad across many dates and tickers?
- Do improved groups still look like the intended chart setup?
- Are improvements robust after trimming extreme winners and losers?
- Are improvements present in most years, or only in one market cycle?
- Is high ATR acting as useful setup context or just beta/rebound exposure?
- Is a deep pullback variant still Setup B continuation, or a separate rebound label?

## Possible v2 Shapes
Prefer score enhancement before hard filters.

Option A: v2 enhanced score
- keep broad Setup B eligibility
- add diagnostic indicators to a new score
- compare v1 score buckets against v2 score buckets

Option B: v2 variant
- keep v1 as main scanner
- create a named subset such as `setup_b_v2_momentum_reset`
- use RSI/MACD/ADX as additional subset rules

Option C: v2 hard gate
- add one or more indicators to candidate eligibility
- only acceptable if sample size remains healthy and evidence is strong

Previous recommended first attempt:

```text
Option A: v2 enhanced score
```

Reason:
It preserves sample size and reduces the risk of overfitting from hard thresholds.

Updated pre-v2 evidence as of 2026-05-14:

- High ATR is the leading v2 research hypothesis after benchmark-relative, date-declustered, outlier, and yearly-consistency checks.
- `moderate_confirmation + high_atr` looks stronger than `strong_confirmation + high_atr`, so stronger confirmation should not be promoted blindly.
- `too_deep` pullbacks may deserve a separate rebound-style branch, but this may not be the same as clean trend-continuation Setup B.

Updated recommended planning direction:

```text
Decide v2 shape before coding:
1. high-volatility Setup B continuation/rebound variant
2. conservative clean-continuation variant
3. separate labels for continuation and rebound
```

The evidence currently favors option 1 or option 3 over a generic stricter version of v1.

## Acceptance Criteria For v2 Proposal
A v2 proposal should only be written if the candidate changes show:

- better 5D/10D/20D forward returns than v1 baseline
- better or similar median return
- better or similar win rate
- positive SPY/QQQ-relative behavior
- date-declustered improvement
- acceptable sample size
- no obvious single-month dependency
- chart quality that still matches the user's playbook

## Rejection Criteria
Do not promote v2 if:

- improvement only appears in one horizon
- improvement is only mean return but not median or win rate
- sample size becomes too small
- results depend on one month or event cluster
- results vanish relative to SPY/QQQ
- chart review shows candidates no longer match the intended setup
- rules become too complex to explain

## Implementation Rules
If v2 is approved:

- implement v2 beside v1
- do not rename or overwrite v1 columns
- create explicit v2 columns
- update dashboard to compare v1 vs v2
- add tests
- update `docs/DESIGN.md`
- update `docs/ALPHA_RESEARCH.md`
- create or update an ADR
- record findings in `docs/RESEARCH_LOG.md`

Possible v2 columns:

```text
setup_b_v2_momentum_reset_gate
daily_setup_b_v2_momentum_reset_score
setup_b_v2_version
setup_b_v2_explanation
```

## Current Decision
No v2 implementation yet.

Next action:
Use `docs/SETUP_B_V2_PROPOSAL.md` as the working proposal. Build diagnostic comparisons for RSI reset, MACD histogram improvement, ADX trend strength, ROC acceleration, slope confirmation, and high ATR context before choosing a concrete v2 definition.
