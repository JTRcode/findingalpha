from __future__ import annotations

import pandas as pd

from tests.test_features import sample_bars
from trading_screener.features.technicals import add_technical_features
from trading_screener.research.alpha_eval import (
    benchmark_comparison,
    evaluate_score_buckets,
    top_bottom_spread,
    transaction_cost_sensitivity,
)
from trading_screener.research.forward_returns import add_forward_returns
from trading_screener.signals.scoring import add_composite_score
from trading_screener.backtesting.simple_backtester import simple_top_ranked_basket


def test_add_forward_returns_uses_future_prices() -> None:
    df = add_forward_returns(sample_bars(days=10), horizons=(1, 5))
    first = df[df["ticker"] == "AAA"].iloc[0]

    assert round(first["fwd_return_1d"], 6) == round(101 / 100 - 1, 6)
    assert round(first["fwd_return_5d"], 6) == round(105 / 100 - 1, 6)


def test_evaluate_score_buckets_outputs_summary() -> None:
    scored = add_composite_score(add_technical_features(sample_bars(days=90)))
    summary = evaluate_score_buckets(scored, buckets=2)
    spreads = top_bottom_spread(summary)

    assert not summary.empty
    assert {"score_bucket", "mean", "median", "win_rate", "horizon_days"}.issubset(summary.columns)
    assert not spreads.empty


def test_benchmark_comparison_outputs_spread_when_benchmark_present() -> None:
    bars = sample_bars(days=90).replace({"BBB": "SPY"})
    scored = add_composite_score(add_technical_features(bars))
    comparison = benchmark_comparison(scored, benchmark_tickers=("SPY",), buckets=2)

    assert not comparison.empty
    assert {"benchmark", "mean_spread", "win_rate_vs_benchmark"}.issubset(comparison.columns)


def test_simple_basket_and_cost_sensitivity() -> None:
    scored = add_composite_score(add_technical_features(sample_bars(days=90)))
    basket = simple_top_ranked_basket(scored, top_n=1, horizon=5)
    costs = transaction_cost_sensitivity(basket)

    assert not basket.empty
    assert {"basket_return", "equity_curve", "drawdown", "turnover_estimate"}.issubset(basket.columns)
    assert not costs.empty
