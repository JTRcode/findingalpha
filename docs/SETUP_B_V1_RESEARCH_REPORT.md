# Setup B v1 Research Report

Date: 2026-05-14
Status: Active baseline, frozen for comparison

## Summary
Setup B is the active daily research setup: trend pullback continuation.

The current definition is frozen as:

```text
setup_b_v1_broad_scanner
```

This means Setup B v1 should not be changed in place. New indicators, thresholds, or scoring changes must be tested as diagnostics first. If evidence supports a revised definition, it should become a new version such as `setup_b_v2_momentum_reset`.

## Trading Idea
Setup B tries to identify stocks or ETFs that are already in an uptrend, pull back in a controlled way, reset momentum, and begin to confirm continuation.

Plain-language hypothesis:

> Strong names that pull back without breaking structure and then begin to confirm should have better forward returns than weaker or lower-quality pullbacks.

## Current Scope
In scope:
- daily bars
- daily Setup B candidates
- forward returns over 1D, 5D, 10D, 20D, and 60D
- chart review
- score buckets
- filter diagnostics
- RSI/MACD/ADX/acceleration/slope diagnostics
- SPY/QQQ-relative diagnostics
- date-declustered diagnostics

Out of scope:
- live trading
- broker execution
- options logic
- automated orders
- intraday rule promotion
- ML-based signal decisions
- changing Setup B v1 rules in place

## Version Freeze
Setup B v1 is frozen as the baseline definition.

Frozen components:
- broad scanner gate
- strict gate
- individual gate definitions
- quality score weights
- default candidate threshold
- v1 naming

Allowed without creating v2:
- adding diagnostics that do not affect v1 eligibility or score
- adding dashboard explanations
- adding reports
- adding research artifacts
- fixing bugs that make implementation differ from the documented v1 definition

Not allowed without creating v2:
- changing broad gate thresholds
- changing strict gate thresholds
- changing quality score weights
- making RSI, MACD, ADX, acceleration, or slope part of eligibility
- changing the meaning of `daily_setup_b_trend_pullback_score`

## Setup B v1 Definition
Setup B v1 has two levels:

- broad scanner gate: creates the research sample
- strict gate: identifies cleaner discretionary-style matches

The score ranks broad candidates. The strict gate does not have to pass for a broad candidate to appear.

### Broad Scanner Gate
A candidate must pass broad trend, pullback, volume, structure, and confirmation checks.

Trend:
- 60D momentum > 4%
- price vs 50 SMA > -2%
- price vs 200 SMA > -5%
- 20 SMA > 50 SMA, or close > 50 SMA

Pullback:
- price is 0.5% to 10% below 10D high
- 1 to 7 down days in last 7 sessions
- no more than 1 large red candle in last 5 sessions

Volume:
- relative volume < 1.25, or pullback volume ratio < 1.10

Structure:
- price vs 20 SMA > -5%, or price vs 50 SMA > -3%
- 20D momentum > -8%
- close > 96% of 50 SMA

Confirmation:
- 1D return > -0.5%
- close position in daily range > 45%
- reclaim prior high, close > 20 SMA, or 1D return > 0

### Strict Gate
The strict gate is the cleaner playbook audit label.

Trend:
- 60D momentum > 10%
- price vs 50 SMA > 2%
- price vs 200 SMA > 0%
- 20 SMA > 50 SMA

Pullback:
- price is 1.5% to 7% below 10D high
- 2 to 6 down days in last 7 sessions
- zero large red candles in last 5 sessions
- orderly pullback proxy passes

Volume:
- relative volume < 0.90
- pullback volume ratio < 0.90

Structure:
- price vs 20 SMA > -2%, or price vs 50 SMA > -1%
- 20D momentum > -2%
- close > 50 SMA

Confirmation:
- 1D return > 0%
- close position in daily range > 65%
- reclaim prior high, or close > 20 SMA

## Current Score
The Setup B score only applies to broad scanner matches.

Weights:
- trend quality: 25%
- pullback quality: 25%
- structure quality: 20%
- volume quality: 15%
- confirmation quality: 15%

Interpretation:
- broad gate answers: is this plausible enough to study?
- strict gate answers: does this match the cleaner discretionary playbook?
- score answers: how strong is this candidate relative to other broad candidates?

## Diagnostic Features
The following are diagnostic only and do not affect Setup B v1 eligibility or score:

- RSI 14
- RSI 14 3D change
- RSI reset zone
- MACD line
- MACD signal
- MACD histogram
- MACD histogram 3D change
- MACD histogram turning up
- ADX 14
- ROC 5D
- ROC 10D
- ROC 20D
- ROC acceleration 5/20
- 20 SMA slope over 5D
- 50 SMA slope over 10D
- 20D linear-regression slope

These diagnostics exist to test possible v2 hypotheses, not to change v1.

## Required Evidence Before v2
Before proposing Setup B v2, collect and review:

- Setup B score buckets
- Setup B bucket diagnostics
- Setup B filter diagnostics
- Setup B indicator diagnostics
- Setup B slices
- Setup B interaction slices
- Setup B variants
- SPY/QQQ-relative monthly diagnostics
- date-declustered diagnostics
- chart review notes

## Filter Diagnostics Findings
Latest reviewed artifact:

```text
data/backtests/setup_b_filter_diagnostics_20260514T071215Z.parquet
```

The broad Setup B funnel shows that the restrictive broad gates are Trend, Pullback, and Confirmation. Volume and Structure are mostly permissive after the earlier gates have already narrowed the sample.

Broad cumulative funnel:

| Step | Gate | Eligible Ticker-Days | Passing Ticker-Days | Pass Rate From Prior Step | Pass Rate Of Total |
|---:|---|---:|---:|---:|---:|
| 1 | Trend | 1,943,089 | 817,668 | 42.08% | 42.08% |
| 2 | Pullback | 817,668 | 467,396 | 57.16% | 24.05% |
| 3 | Volume | 467,396 | 419,500 | 89.75% | 21.59% |
| 4 | Structure | 419,500 | 417,159 | 99.44% | 21.47% |
| 5 | Confirmation | 417,159 | 158,943 | 38.10% | 8.18% |

Interpretation:

- `pass rate from prior step` is conditional. It answers: of the names that already passed all earlier gates, how many pass this gate?
- `pass rate of total` is cumulative. It answers: of all ticker-days in the research dataset, how many are still alive after this gate?
- Volume has a high pass rate from prior step because the broad volume rule is intentionally loose: relative volume < 1.25, or pullback volume ratio < 1.10.
- Structure has a very high pass rate from prior step because Trend and Pullback already select names near trend support; the broad structure checks are therefore mostly redundant at this point.
- The low pass rate of total for Volume and Structure does not mean those gates are independently restrictive. It mostly reflects the filtering already done by Trend and Pullback.
- Confirmation is the largest late-stage broad filter. It cuts the post-structure set from 417,159 to 158,943 ticker-days.

Current implication for v2:

- Do not make Volume or Structure stricter inside v1.
- Treat broad Structure as a safety/audit gate, not a primary source of selectivity.
- If v2 needs fewer, cleaner candidates, start by researching Confirmation quality, Pullback quality, and diagnostic momentum-reset features instead of assuming Volume or Structure are doing the main filtering.
- The strict gate remains much more selective, but it may be too narrow for practical candidate generation without proving forward-return improvement.

### Condition-Level Deep Dive
The filter diagnostics have three useful views:

- `independent_condition`: tests each rule by itself across the dataset.
- `cumulative_funnel`: applies gates in Setup B order: Trend, Pullback, Volume, Structure, Confirmation.
- `final_gate`: reports the final broad or strict candidate count.

The broad scanner is not evenly restrictive. Most filtering comes from a small number of conditions.

Most restrictive broad conditions when tested independently:

| Gate | Condition | Broad Rule | Pass Rate Of Available Rows | Interpretation |
|---|---|---|---:|---|
| Trend | 60D momentum | > 4% | 49.11% | Main trend filter. Most non-uptrending ticker-days fail here. |
| Confirmation | Close position in daily range | > 45% | 56.76% | Requires some buyer support by the close. |
| Pullback | Pullback from 10D high | -10% to -0.5% | 64.44% | Main pullback-shape filter. Excludes extended highs and deeper breaks. |
| Confirmation | 1D return | > -0.5% | 67.62% | Excludes days that are still actively selling off. |
| Trend | Price vs 50 SMA | > -2% | 72.18% | Keeps candidates near intermediate trend support. |

Least restrictive broad conditions:

| Gate | Condition | Broad Rule | Pass Rate Of Available Rows | Interpretation |
|---|---|---|---:|---|
| Pullback | Orderly pullback proxy | not required | 100.00% | Placeholder in broad mode; only meaningful in strict mode. |
| Pullback | Large red candles in last 5 sessions | <= 1 | 99.44% | Almost never filters broad candidates. |
| Pullback | Down days in last 7 sessions | 1 to 7 | 93.68% | Very permissive broad pullback count. |
| Structure | Close vs 50 SMA | close > 96% of 50 SMA | 92.33% | Loose safety check. |
| Structure | Price holds 20/50 SMA area | price vs 20 SMA > -5% OR price vs 50 SMA > -3% | 91.87% | Loose safety check. |

Important redundancy notes:

- Broad Volume has two displayed conditions, but both use the same broad OR expression: `relative volume < 1.25 OR pullback volume ratio < 1.10`. The second Volume row does not add another independent broad filter after the first one has passed.
- Broad Structure is mostly redundant after Trend and Pullback. In a gate-level recomputation, the price-hold and close-vs-50-SMA checks removed no additional rows once Trend, Pullback, and Volume had already passed; only `20D momentum > -8%` removed a small number of rows.
- Broad Pullback's `orderly_pullback_proxy` is intentionally disabled in v1 broad mode. It exists so the strict gate can express a cleaner discretionary version without changing the broad research sample.
- Broad Confirmation is doing more work than it first appears. The final broad pass rate falls from 21.47% after Structure to 8.18% after Confirmation.

Strict gate contrast:

| Gate | Strict Funnel Pass Rate From Prior Step | Strict Funnel Pass Rate Of Total | Interpretation |
|---|---:|---:|---|
| Trend | 21.95% | 21.95% | Much stronger trend requirement. |
| Pullback | 26.02% | 5.71% | Narrower pullback depth does major filtering. |
| Volume | 35.19% | 2.01% | True volume dry-up becomes meaningful only in strict mode. |
| Structure | 93.50% | 1.88% | Still mostly a safety check after prior strict gates. |
| Confirmation | 19.94% | 0.37% | Very selective confirmation requirement. |

This supports a two-level interpretation:

- broad v1 is a research candidate generator
- strict v1 is a clean-playbook label
- future v2 should be promoted only if stricter conditions improve forward-return evidence, not merely because they look more intuitive

Near-term research actions:

1. Review whether broad Volume should be shown as one combined condition in the dashboard to avoid implying two independent broad filters.
2. Test whether strict Volume improves forward returns enough to justify a v2 condition.
3. Test whether Structure is redundant or whether it protects against rare bad charts.
4. Prioritize Confirmation quality and Pullback quality diagnostics before changing v1 thresholds.

## Absolute vs Benchmark-Relative Findings
Latest reviewed artifacts:

```text
data/backtests/setup_b_bucket_diagnostics_20260514T071218Z.parquet
data/backtests/setup_b_top_bottom_spreads_20260514T071218Z.parquet
data/backtests/setup_b_benchmark_relative_monthly_20260514T071235Z.parquet
data/backtests/setup_b_date_declustered_20260514T071239Z.parquet
```

The absolute bucket diagnostics show a positive relationship between Setup B score bucket and longer-horizon forward returns. The relationship is weak at 1D, modest at 5D/10D, and more visible at 20D/60D.

Absolute top-bucket minus bottom-bucket spread:

| Horizon | Mean Spread | Median Spread | Win-Rate Spread | Interpretation |
|---:|---:|---:|---:|---|
| 1D | 0.0067% | -0.0145% | -0.9440% | likely too small |
| 5D | 0.0948% | 0.0357% | -0.3240% | likely too small |
| 10D | 0.1539% | 0.0334% | -0.7919% | likely too small |
| 20D | 0.3999% | 0.1097% | -1.1729% | small edge watch |
| 60D | 1.4924% | 0.4094% | -2.1557% | small edge watch |

The win-rate spread is negative even when the mean spread is positive. That means the higher bucket's advantage is not coming from a higher percentage of winning observations. It is more likely coming from larger winners, smaller losers, or market exposure. This makes benchmark-relative testing important.

Monthly benchmark-relative summary for all Setup B candidates:

| Benchmark | Horizon | Weighted Absolute Mean | Weighted Relative Mean | Monthly Relative Win Rate |
|---|---:|---:|---:|---:|
| SPY | 5D | 0.2521% | 0.0274% | 53.01% |
| SPY | 10D | 0.5245% | 0.0648% | 60.99% |
| SPY | 20D | 1.0886% | 0.1614% | 56.04% |
| SPY | 60D | 3.5412% | 0.5522% | 61.11% |
| QQQ | 5D | 0.2521% | -0.0865% | 48.63% |
| QQQ | 10D | 0.5245% | -0.1373% | 46.70% |
| QQQ | 20D | 1.0886% | -0.2159% | 46.15% |
| QQQ | 60D | 3.5412% | -0.5657% | 43.89% |

Interpretation:

- Setup B candidates look positive in absolute terms.
- Relative to SPY, the aggregate Setup B sample is mildly positive at 5D/10D and more positive at 20D/60D.
- Relative to QQQ, the aggregate Setup B sample is negative across 5D/10D/20D/60D.
- This suggests the current scanner may be capturing broad equity strength and/or large-cap momentum more than a standalone edge over growth/tech beta.
- SPY-relative evidence is more supportive than QQQ-relative evidence.

Score bucket relative comparison:

| Benchmark | Horizon | Bucket 1 Relative Mean | Bucket 5 Relative Mean | Bucket 5 Minus Bucket 1 |
|---|---:|---:|---:|---:|
| SPY | 5D | -0.0145% | 0.0817% | 0.0962% |
| SPY | 10D | 0.0061% | 0.1650% | 0.1589% |
| SPY | 20D | 0.0332% | 0.4425% | 0.4094% |
| SPY | 60D | 0.1079% | 1.6307% | 1.5229% |
| QQQ | 5D | -0.1269% | -0.0321% | 0.0949% |
| QQQ | 10D | -0.1955% | -0.0366% | 0.1589% |
| QQQ | 20D | -0.3435% | 0.0672% | 0.4107% |
| QQQ | 60D | -1.0089% | 0.5189% | 1.5278% |

Date-declustered relative comparison:

| Benchmark | Horizon | Bucket 1 Relative Mean | Bucket 5 Relative Mean | Bucket 5 Minus Bucket 1 | Bucket 5 Relative Win Rate |
|---|---:|---:|---:|---:|---:|
| SPY | 5D | -0.0447% | 0.1189% | 0.1636% | 52.58% |
| SPY | 10D | -0.0146% | 0.1448% | 0.1594% | 51.45% |
| SPY | 20D | -0.0138% | 0.4945% | 0.5082% | 53.80% |
| SPY | 60D | 0.0834% | 1.8316% | 1.7482% | 56.44% |
| QQQ | 5D | -0.1363% | 0.0199% | 0.1563% | 48.99% |
| QQQ | 10D | -0.2046% | -0.0403% | 0.1643% | 48.63% |
| QQQ | 20D | -0.3844% | 0.1400% | 0.5245% | 49.57% |
| QQQ | 60D | -1.0154% | 0.7605% | 1.7759% | 50.62% |

Current conclusion:

- The Setup B score has useful ranking information at longer horizons, especially 20D and 60D.
- The effect is not strong enough at 1D/5D to treat as a tactical entry signal by itself.
- SPY-relative results are meaningfully better than QQQ-relative results.
- QQQ-relative results are only encouraging in the highest bucket at 20D/60D, and even there the win rate is near 50%.
- The evidence is consistent with a possible swing-trade research signal, but not yet a complete trading strategy.
- The next research step should test whether the top bucket's apparent longer-horizon edge is driven by sector/beta/rebound exposure, crowded dates, or a small number of outsized winners.

## Slice and Interaction Findings
Latest reviewed artifacts:

```text
data/backtests/setup_b_slices_20260514T071219Z.parquet
data/backtests/setup_b_interaction_slices_20260514T071221Z.parquet
data/backtests/setup_b_benchmark_relative_monthly_20260514T071235Z.parquet
data/backtests/setup_b_date_declustered_20260514T071239Z.parquet
```

Most promising single slices:

| Slice | Why It Looks Interesting | Main Concern |
|---|---|---|
| `high_atr` | Best absolute slice at 5D/10D/20D/60D and survives SPY/QQQ-relative checks. | Could be high-beta/rebound exposure rather than clean alpha. |
| `strong_trend_quality` | Better than weak trend at 20D/60D and positive versus SPY/QQQ at longer horizons. | Less powerful than high ATR; may overlap with momentum/beta. |
| deeper pullbacks | `deep_4p5_7` and `too_deep` show strong absolute returns at 10D/20D/60D. | Current benchmark-relative monthly artifact does not cover this slice, so confidence is lower. |

High ATR evidence:

| Horizon | High ATR Absolute Mean | High ATR vs SPY | High ATR vs QQQ | Date-Declustered High ATR vs QQQ |
|---:|---:|---:|---:|---:|
| 5D | 0.80% | 0.56% | 0.42% | n/a |
| 10D | 1.77% | 1.21% | 0.90% | n/a |
| 20D | 3.66% | 2.40% | 2.05% | 2.13% |
| 60D | 11.67% | 7.26% | 6.41% | 7.15% |

Strong trend quality evidence:

| Horizon | Strong Trend Absolute Mean | Strong Trend vs SPY | Strong Trend vs QQQ | Date-Declustered Strong Trend vs QQQ |
|---:|---:|---:|---:|---:|
| 20D | 1.84% | 0.67% | 0.19% | 0.32% |
| 60D | 5.94% | 2.50% | 1.52% | 1.47% |

Interaction findings:

- `confirmation_quality_slice x atr_slice` is the strongest interaction family in absolute terms.
- `moderate_confirmation + high_atr` is especially strong: about 4.35% mean at 20D and 13.37% mean at 60D, with sample sizes around 1,500 observations.
- `market_regime x atr_slice` also ranks highly, especially `spy_weak_or_chop + high_atr` and `spy_positive + high_atr`.
- `weak_confirmation + high_atr` and `strong_confirmation + high_atr` both perform well, which suggests ATR may be doing more explanatory work than confirmation quality.
- `weak_confirmation + too_deep` and `too_deep + ideal_3_4` look strong, but these are higher-risk rebound-style slices and need benchmark-relative/de-clustered validation before promotion.

Less promising slices:

- Volume dry-up does not currently show a clean monotonic improvement. Strong dry-up is not consistently better than weak or moderate dry-up at longer horizons.
- Confirmation quality is not cleanly monotonic. Strong confirmation is not consistently better than moderate or weak confirmation.
- Market regime alone is hard to interpret. `spy_weak_or_chop` has higher absolute returns, but that may reflect rebound beta after weak benchmark periods.

Current slice conclusion:

- The clearest v2 research candidate is not “stricter confirmation” or “stricter volume.” It is a high-volatility pullback/rebound subset inside Setup B.
- That does not mean ATR itself is alpha. It means high ATR is currently the strongest segmentation variable and should be tested for beta, sector, and rebound exposure.
- A professional next step would not directly promote `high_atr` into a trading rule. It would run a targeted robustness pass: sector split, date de-clustering, QQQ-relative results, outlier contribution, and transaction-cost sensitivity.

## Pre-v2 Evidence Hardening
Latest generated hardening artifacts:

```text
data/backtests/setup_b_benchmark_relative_monthly_20260514T075532Z.parquet
data/backtests/setup_b_date_declustered_20260514T075544Z.parquet
data/backtests/setup_b_outlier_diagnostics_20260514T075548Z.parquet
data/backtests/setup_b_time_consistency_20260514T075555Z.parquet
```

The hardening pass expanded benchmark-relative and date-declustered coverage to more slices and interaction slices:

- `pullback_depth_slice`
- `pullback_duration_slice`
- `volume_dryup_slice`
- `confirmation_quality_slice`
- `market_regime_x_atr_slice`
- `confirmation_quality_slice_x_atr_slice`
- `confirmation_quality_slice_x_pullback_depth_slice`
- `pullback_depth_slice_x_pullback_duration_slice`
- `volume_dryup_slice_x_confirmation_quality_slice`

The pass also added:

- outlier diagnostics with 5-95% trimmed means, 1st/99th percentiles, and top/bottom 1% contribution
- yearly consistency diagnostics with positive-year rate versus SPY/QQQ

### Hardened Findings
High ATR remains the strongest v2 hypothesis after the added checks.

High ATR versus QQQ:

| Horizon | Absolute Mean | QQQ-Relative Mean | Date-Declustered QQQ-Relative Mean |
|---:|---:|---:|---:|
| 20D | 3.66% | 2.05% | 2.13% |
| 60D | 11.67% | 6.41% | 7.15% |

High ATR time consistency versus QQQ:

| Slice | Horizon | Years | Yearly Relative Mean | Positive-Year Rate |
|---|---:|---:|---:|---:|
| `high_atr` | 60D | 16 | 7.52% | 75.00% |
| `moderate_confirmation + high_atr` | 60D | 16 | 8.41% | 81.25% |
| `weak_confirmation + high_atr` | 60D | 16 | 7.79% | 75.00% |
| `strong_confirmation + high_atr` | 60D | 16 | 5.98% | 62.50% |

Outlier check:

| Slice | Horizon | Mean | Median | Trimmed Mean 5-95% | Top 1% Return Share |
|---|---:|---:|---:|---:|---:|
| `high_atr` | 60D | 11.67% | 8.21% | 9.34% | 15.56% |
| `moderate_confirmation + high_atr` | 60D | 13.37% | 8.66% | 10.76% | 14.65% |

Interpretation:

- High ATR is helped by large winners, but the edge does not disappear after trimming the top and bottom tails.
- The top 1% contribution is meaningful but not so extreme that the entire mean is only one-tail noise.
- `moderate_confirmation + high_atr` currently looks better than `strong_confirmation + high_atr`, which argues against blindly tightening confirmation.
- High ATR has better QQQ-relative yearly consistency than the broad Setup B score bucket alone.

Secondary finding:

- `too_deep` pullbacks now look worth studying. They are positive versus QQQ at 20D and 60D, with 60D QQQ-relative mean around 2.85% and positive-year rate around 68.75%.
- This is likely a higher-risk rebound pattern rather than a clean continuation pattern, so it should be treated as a separate v2 branch or watchlist label, not automatically merged into the core continuation rule.

Negative or weak findings:

- Volume dry-up remains weak as a standalone v2 driver. Strong dry-up is less bad than weak dry-up versus QQQ, but it does not show the same strength as high ATR.
- Confirmation quality remains non-monotonic. Strong confirmation is not clearly better than moderate or weak confirmation.
- Pullback duration is not yet a leading variable by itself.

Current pre-v2 conclusion:

- The best-supported v2 planning path is `Setup B + high ATR`, possibly with a controlled-pullback/rebound framing.
- A second possible path is `Setup B + too_deep pullback`, but this should be treated as a different risk style.
- The next design decision should define whether v2 is intended to be a high-volatility rebound swing screen, a cleaner trend-continuation screen, or two separate labels.

Minimum evidence for a v2 proposal:
- v2 diagnostic condition improves 5D, 10D, or 20D forward returns versus v1 baseline
- improvement appears in mean and preferably median returns
- win rate does not deteriorate meaningfully
- sample size remains practical
- improvement is not concentrated in one month or a few crowded dates
- SPY/QQQ-relative returns improve
- charts still visually match the intended pullback-continuation setup
- proposed rule remains simple enough to explain

## Candidate v2 Hypotheses
Potential v2 ideas to test:

- Setup B + RSI reset: candidates where RSI reset to a constructive zone after prior strength.
- Setup B + MACD improving: candidates where MACD histogram is rising, even if still negative.
- Setup B + ADX trend strength: candidates where ADX shows a real trend environment.
- Setup B + ROC acceleration: candidates where 5D momentum is improving relative to 20D pace.
- Setup B + rising slope: candidates where 20 SMA slope or 20D regression slope remains positive.

None of these are accepted v2 rules yet.

## Promotion Path
If diagnostics support a revised setup:

1. Write `docs/SETUP_B_V2_PROPOSAL.md`.
2. Create ADR 0009 if methodology changes.
3. Implement v2 beside v1, not as a replacement.
4. Compare v1 vs v2 directly.
5. Keep v1 snapshots interpretable.

Comparison requirements:
- v1 candidates vs v2 candidates
- v1-only vs v2-only
- overlap candidates
- top-bucket performance
- benchmark-relative performance
- date-declustered performance
- monthly consistency
- candidate frequency

## Current Decision
Do not change Setup B v1.

Next step is data collection and diagnostics review, not rule editing.
