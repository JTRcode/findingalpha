# ADR 0008: Setup B Research Methodology

Date: 2026-05-13
Status: Accepted

## Context
Setup B, trend pullback continuation, is the active research setup. The project started with a stricter all-gates scanner, then broadened the scanner because the strict definition produced too few candidates for useful alpha testing. The broader research workflow now includes strict gate labels, quality scoring, bucket diagnostics, slices, interaction slices, variants, benchmark-relative tests, and chart review.

This is large enough to be an architectural research-methodology decision, not just an implementation detail.

## Options considered
- Keep only the strict all-gates Setup B scanner.
  - Pros: cleaner discretionary interpretation, fewer weak charts.
  - Cons: too few candidates, higher overfit risk, weaker statistical usefulness.
- Use a broad scanner plus strict audit gates and quality score.
  - Pros: larger research sample, keeps strict playbook visibility, enables bucket and slice testing.
  - Cons: more dashboard complexity, risk of admitting noisy candidates.
- Replace Setup B with a machine-learning classifier.
  - Pros: could learn nonlinear interactions later.
  - Cons: premature, harder to interpret, high overfitting risk before baseline evidence is stable.
- Remove Setup A and Setup C from the project and focus only on Setup B.
  - Pros: simpler research focus.
  - Cons: unnecessary right now because A/C are lightweight prototypes and may remain useful later.

## Decision
Use `setup_b_v1_broad_scanner` as the current frozen Setup B research definition.

The Setup B workflow is:
- broad scanner gate creates the candidate research sample
- strict gate records whether the original higher-quality all-gates definition passed
- individual gates record trend, pullback, volume dry-up, structure, and confirmation pass/fail status
- continuous quality score ranks broad candidates
- score buckets test whether higher Setup B scores predict better future returns
- slices and interaction slices are diagnostics, not trade rules
- variants are research labels, not execution signals
- SPY/QQQ-relative and date-declustered tests are required before interpreting positive results
- chart review is used to audit whether rules are capturing the intended setup

Setup B rules must not be silently edited in place. A material rule or weight change should create a new version, such as `setup_b_v2_*`, and should document the differences.

## Rationale
The broad scanner keeps enough observations for forward-return testing while the strict gates preserve the user's intended discretionary playbook. This supports the project goal: test whether an interpretable setup has predictive value before treating it as a trading signal.

This also keeps the system from becoming opaque. The broad gate answers "is this plausible enough to study?" The strict gates answer "does this match the cleaner human setup?" The score answers "how strong is this candidate relative to other candidates?"

## Consequences
Setup B candidates will include some charts that do not look clean. That is intentional for research sample size, but the dashboard must make the gate failures visible. Users should avoid treating broad candidates as trade ideas without chart review and validation.

The dashboard and docs must clearly distinguish:
- generic `composite_score`
- `daily_setup_b_trend_pullback_score`
- strict gate pass/fail status
- slices and variants

Further filtering can improve chart quality but may increase overfitting risk. Narrow filters should be promoted only after bucket, benchmark-relative, date-declustered, and out-of-sample evidence.

## Review triggers
- Setup B score buckets stop showing useful ranking behavior.
- Broad candidates are too noisy for practical review.
- Strict matches are too rare to evaluate.
- A proposed Setup B v2 materially changes gates, weights, or thresholds.
- Sector metadata, beta adjustment, or intraday confirmation becomes available.
- Out-of-sample signal snapshots contradict the historical backtest.
- Machine-learning experiments are proposed.
