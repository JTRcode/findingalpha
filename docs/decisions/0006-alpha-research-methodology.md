# ADR 0006: Alpha Research Methodology

Date: 2026-05-10
Status: Accepted

## Context
The project must test whether screener signals have predictive value before treating any score as a trading signal.

## Options considered
- Forward-return bucket analysis: Directly tests whether higher scores lead to better future returns.
- Event studies: Useful for earnings/news/filings later, but not required for daily technical baseline.
- Factor regression/neutralization: Valuable later for separating alpha from beta/sector/size/momentum exposures.
- Full strategy backtest: Useful later, but can obscure whether the underlying signal works.
- Complex ML: Premature and high overfitting risk.

## Decision
Use forward return analysis by score bucket, a simple long-only top-ranked basket research backtest, comparison against SPY/QQQ, no live trading, and no complex ML until baseline signals are validated.

## Rationale
This method is simple, interpretable, and aligned with the core question: does the score predict future returns over 1, 5, 10, 20, and 60 trading days?

## Consequences
Initial tests will not fully isolate all exposures or simulate execution. Later research must add sector/size/liquidity controls, transaction costs, slippage, and out-of-sample tracking.

## Review triggers
- Baseline score shows promising bucket monotonicity.
- Fundamentals, sectors, or event features are added.
- Paper trading is considered.
- Results are concentrated, regime-specific, or unstable.

