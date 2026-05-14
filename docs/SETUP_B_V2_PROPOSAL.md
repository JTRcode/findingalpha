# Setup B v2 Proposal

Date: 2026-05-14
Status: Draft research proposal

## Purpose
This proposal defines the next Setup B research path without changing the frozen v1 rules.

Setup B v1 remains:

```text
setup_b_v1_broad_scanner
```

The goal of v2 research is to test whether momentum-reset and trend-quality diagnostics improve the ability to rank or label Setup B candidates.

This is not a live trading proposal. It does not add broker execution, automated trading, options logic, or LLM-based trading decisions.

## Current Evidence
Setup B v1 has useful longer-horizon ranking information, especially around 20D and 60D, but it is not yet a validated trading strategy.

Current findings:

- broad v1 is useful as a candidate generator
- the score has more value at 20D/60D than at 1D/5D
- SPY-relative evidence is stronger than QQQ-relative evidence
- high ATR is the strongest hardened slice so far
- stricter volume dry-up is not yet a leading v2 candidate
- stricter confirmation alone is not clearly better
- high ATR may represent volatility/rebound exposure, not pure continuation alpha

## Research Hypotheses
The user wants v2 research to explore:

- RSI reset
- MACD histogram improvement
- ADX trend strength
- ROC acceleration
- slope confirmation
- high ATR as a separate context flag, not always a positive

These should be tested as diagnostics before becoming gates.

### Hypothesis 1: RSI Reset
Idea:

Strong stocks that pull back and reset RSI into a constructive zone may have better continuation odds than stocks that remain overextended or break down.

Candidate diagnostic:

```text
rsi_reset_zone == true
```

Supporting fields:

- `rsi_14`
- `rsi_14_change_3d`
- `rsi_was_overbought_10d`
- `rsi_reset_zone`

Questions:

- Does RSI reset improve 5D/10D/20D returns?
- Does it improve median return or only mean return?
- Does it remain useful versus SPY/QQQ?
- Does it help high-ATR names or low/medium-ATR names more?

### Hypothesis 2: MACD Histogram Improvement
Idea:

A pullback may be more actionable when MACD histogram stops deteriorating and begins improving.

Candidate diagnostic:

```text
macd_hist_change_3d > 0
```

Supporting fields:

- `macd_line`
- `macd_signal`
- `macd_hist`
- `macd_hist_change_3d`
- `macd_hist_turning_up`

Questions:

- Does rising MACD histogram improve forward returns?
- Does it matter whether MACD histogram is still negative or already positive?
- Is MACD improvement more useful for timing than for candidate selection?

### Hypothesis 3: ADX Trend Strength
Idea:

Setup B should perform better when the prior trend is real rather than choppy.

Candidate diagnostic:

```text
adx_14 >= 20 or adx_14 >= 25
```

Supporting fields:

- `adx_14`
- plus/minus directional indicator internals if needed later

Questions:

- Does ADX identify cleaner trend environments?
- Does high ADX improve continuation, or does it identify already-exhausted moves?
- Does ADX interact with ATR?

### Hypothesis 4: ROC Acceleration
Idea:

Candidates may be better when short-term momentum is improving relative to the recent 20D pace.

Candidate diagnostic:

```text
accel_5_20 = roc_5d - (roc_20d / 4)
```

Supporting fields:

- `roc_5d`
- `roc_10d`
- `roc_20d`
- `accel_5_20`

Questions:

- Does positive acceleration improve future returns?
- Does strong positive acceleration chase late moves?
- Is flat-to-improving acceleration better than extreme acceleration?

### Hypothesis 5: Slope Confirmation
Idea:

Continuation candidates may be better when moving-average slope or regression slope remains positive during the pullback.

Candidate diagnostics:

```text
sma20_slope_5d > 0
linreg_slope_20d > 0
```

Supporting fields:

- `sma20_slope_5d`
- `sma50_slope_10d`
- `linreg_slope_20d`

Questions:

- Does positive slope improve Setup B quality?
- Is 20 SMA slope enough, or is 20D regression slope cleaner?
- Does slope overlap too much with existing trend-quality score?

### Hypothesis 6: High ATR Context
Idea:

High ATR is currently the strongest hardened slice, but it should not automatically become a universal positive filter. It may identify a different risk style: high-volatility pullback/rebound.

Candidate diagnostic:

```text
atr_slice == high_atr
```

Supporting fields:

- `atr_pct`
- `atr_slice`
- high-ATR interaction slices

Questions:

- Is high ATR still useful after sector-neutral testing?
- Is the effect mostly rebound beta?
- Does high ATR require a different entry/risk process?
- Should high ATR become a v2 context flag, a named variant, or a separate setup label?

## Testing Plan
Do not combine all indicators immediately.

Step 1: single-factor tests

- Setup B + RSI reset
- Setup B + MACD improving
- Setup B + ADX trend strength
- Setup B + ROC acceleration
- Setup B + positive slope
- Setup B + high ATR

Step 2: benchmark-relative tests

For each factor:

- compare absolute forward returns
- compare SPY-relative returns
- compare QQQ-relative returns
- check 5D, 10D, 20D, and 60D horizons

Step 3: robustness tests

For each factor:

- date-declustered returns
- monthly consistency
- yearly consistency
- median return
- win rate
- 5-95% trimmed mean
- top/bottom 1% contribution
- sample size

Step 4: interaction tests

Only after single-factor tests:

- RSI reset + MACD improving
- MACD improving + positive slope
- ADX trend strength + ROC acceleration
- high ATR + RSI reset
- high ATR + MACD improving
- high ATR + pullback depth
- high ATR + slope confirmation

Step 5: chart review

Review examples from:

- best-performing slices
- poor-performing slices
- high-score false positives
- high-ATR winners
- high-ATR losers
- non-high-ATR winners

## Candidate v2 Shapes
No final v2 shape is accepted yet.

### Option A: Momentum Reset Score
Create a new score beside v1:

```text
daily_setup_b_v2_momentum_reset_score
```

Possible inputs:

- RSI reset
- MACD histogram improvement
- ADX trend strength
- ROC acceleration
- positive slope

High ATR would be shown as context, not necessarily as a score boost.

Pros:

- preserves sample size
- avoids hard overfit filters
- lets bucket testing decide whether the score improves ranking

Cons:

- more complex than a simple named variant
- needs clear weight documentation

### Option B: Momentum Reset Variant
Create a named subset:

```text
setup_b_v2_momentum_reset_gate
```

Possible rule shape:

```text
passes Setup B v1 broad gate
and at least N of:
  RSI reset
  MACD histogram improving
  ADX trend strength
  positive ROC acceleration
  positive slope confirmation
```

Pros:

- easy to explain
- clear chart-review workflow

Cons:

- may overfit through threshold selection
- may reduce sample size too quickly

### Option C: High-ATR Watch Variant
Create a separate context label:

```text
setup_b_v2_high_atr_watch
```

Possible rule shape:

```text
passes Setup B v1 broad gate
and atr_slice == high_atr
and not structurally broken
```

Pros:

- directly follows the strongest evidence so far
- keeps high-volatility candidates visible

Cons:

- may be rebound/beta exposure rather than clean continuation alpha
- likely requires different risk assumptions
- should not replace normal Setup B

### Option D: Two-Label v2
Create two separate labels:

```text
setup_b_v2_momentum_reset
setup_b_v2_high_atr_rebound_watch
```

Pros:

- separates clean continuation from volatile rebound
- avoids forcing one rule to describe two behaviors

Cons:

- more dashboard and reporting complexity
- needs careful naming to avoid clutter

## Recommended Initial Direction
The first implementation should not be a hard filter.

Recommended path:

1. Add dedicated v2 diagnostic artifacts for each proposed factor.
2. Add comparison tables for v1 baseline vs each v2 hypothesis.
3. Only after reviewing those artifacts, implement one of:
   - `daily_setup_b_v2_momentum_reset_score`
   - `setup_b_v2_momentum_reset_gate`
   - `setup_b_v2_high_atr_watch`

Current preference:

```text
Start with Option A: Momentum Reset Score
Keep high ATR as a separate context flag and comparison slice
```

Reason:

This explores the user's preferred indicators without prematurely making them mandatory filters. It also preserves the high-ATR finding without assuming high volatility is always desirable.

## Acceptance Criteria
A v2 candidate is worth implementing only if it improves at least one useful research objective without failing the others.

Required:

- clear improvement versus v1 baseline at 10D or 20D
- positive or improved SPY-relative and QQQ-relative returns
- acceptable sample size
- median return does not deteriorate materially
- win rate does not deteriorate materially
- not driven only by top 1% outliers
- positive-year rate is acceptable
- chart examples still match the intended playbook

Preferred:

- improvement visible at both 10D and 20D
- useful at 5D for timing, even if weaker
- improvement survives date-declustering
- simple enough to explain in one paragraph

## Rejection Criteria
Reject or keep diagnostic-only if:

- the indicator only improves mean return through a few outliers
- QQQ-relative results worsen materially
- the sample becomes too small
- the signal works only in one year or market cycle
- chart review shows the rule no longer captures the intended setup
- the combined rule is too complex to explain

## Implementation Notes
If this proposal is accepted for implementation:

- do not edit Setup B v1 columns
- create explicit v2 columns
- keep v2 outputs beside v1 outputs
- update dashboard comparisons
- update tests
- update `docs/DESIGN.md`
- update `docs/ALPHA_RESEARCH.md`
- update or add an ADR if a v2 methodology is accepted

Possible columns:

```text
setup_b_v2_momentum_reset_score
setup_b_v2_momentum_reset_gate
setup_b_v2_high_atr_watch
setup_b_v2_context
setup_b_v2_explanation
```

## Current Decision
Do not implement v2 filters yet.

Next action:

Build diagnostic comparisons for the proposed v2 factors and review them against v1 baseline before choosing a concrete v2 definition.
