from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from trading_screener import __version__
from trading_screener.backtesting.simple_backtester import simple_top_ranked_basket
from trading_screener.data.storage import ensure_data_dirs, write_parquet
from trading_screener.research.alpha_eval import (
    benchmark_comparison,
    evaluate_score_buckets,
    top_bottom_spread,
    transaction_cost_sensitivity,
)
from trading_screener.research.forward_returns import add_forward_returns
from trading_screener.research.setup_eval import (
    evaluate_daily_setups,
    evaluate_setup_b_benchmark_relative_monthly,
    evaluate_setup_b_bucket_diagnostics,
    evaluate_setup_b_date_declustering,
    evaluate_setup_b_filter_diagnostics,
    evaluate_setup_b_indicator_diagnostics,
    evaluate_setup_b_interaction_slices,
    evaluate_setup_b_market_regime_diagnostics,
    evaluate_setup_b_outlier_diagnostics,
    evaluate_setup_b_score_buckets,
    evaluate_setup_b_sector_declustering,
    evaluate_setup_b_slices,
    evaluate_setup_b_time_consistency,
    evaluate_setup_b_variants,
)
from trading_screener.signals.daily_playbook import daily_setup_candidates
from trading_screener.signals.screeners import build_ranked_screen_from_scored


DEMO_TICKERS = [
    "AAPL",
    "AMZN",
    "AVGO",
    "COST",
    "GOOGL",
    "HD",
    "JPM",
    "LLY",
    "META",
    "MSFT",
    "NFLX",
    "NVDA",
    "QQQ",
    "SPY",
    "TSLA",
    "UNH",
    "V",
    "WMT",
    "XOM",
]
DEMO_START = "2023-01-01"
DEMO_STAMP = "20260514T000000Z"


def main() -> None:
    source_path = Path("data/features/scored_history.parquet")
    output_dir = Path("demo_data")
    if not source_path.exists():
        raise SystemExit("Missing data/features/scored_history.parquet. Run the daily pipeline before building demo data.")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    ensure_data_dirs(output_dir)

    scored = pd.read_parquet(source_path)
    scored["date"] = pd.to_datetime(scored["date"]).dt.date
    demo = scored[
        scored["ticker"].isin(DEMO_TICKERS)
        & (pd.to_datetime(scored["date"]) >= pd.Timestamp(DEMO_START))
    ].copy()
    if demo.empty:
        raise SystemExit("Demo slice is empty. Check source data and DEMO_TICKERS.")

    write_parquet(demo, output_dir / "features" / "scored_history.parquet")

    screen = build_ranked_screen_from_scored(
        scored=demo,
        provider="demo",
        universe="demo_public_large_caps",
        config_version="demo-portfolio",
        code_version=__version__,
    )
    screen["universe_description"] = "Sanitized portfolio demo universe of public large-cap stocks and ETFs."
    screen["universe_point_in_time"] = False
    screen["universe_survivorship_bias"] = "demo sample; not point-in-time"
    screen["universe_notes"] = "Built from local research artifacts for read-only dashboard demonstration."
    write_parquet(screen, output_dir / "signals" / f"signal_snapshot_{DEMO_STAMP}.parquet")

    evaluated = add_forward_returns(demo, copy=True)
    setup_candidates = daily_setup_candidates(evaluated)
    write_parquet(setup_candidates, output_dir / "signals" / f"daily_setup_candidates_{DEMO_STAMP}.parquet")

    bucket_summary = evaluate_score_buckets(evaluated)
    write_parquet(bucket_summary, output_dir / "backtests" / f"forward_return_buckets_{DEMO_STAMP}.parquet")
    write_parquet(top_bottom_spread(bucket_summary), output_dir / "backtests" / f"top_bottom_spreads_{DEMO_STAMP}.parquet")
    write_parquet(
        benchmark_comparison(evaluated),
        output_dir / "backtests" / f"benchmark_comparison_{DEMO_STAMP}.parquet",
    )
    basket = simple_top_ranked_basket(evaluated, top_n=5, horizon=5)
    write_parquet(basket, output_dir / "backtests" / f"top_ranked_basket_{DEMO_STAMP}.parquet")
    write_parquet(
        transaction_cost_sensitivity(basket),
        output_dir / "backtests" / f"transaction_cost_sensitivity_{DEMO_STAMP}.parquet",
    )
    write_parquet(
        evaluate_daily_setups(evaluated),
        output_dir / "backtests" / f"daily_setup_forward_returns_{DEMO_STAMP}.parquet",
    )
    write_parquet(
        evaluate_setup_b_score_buckets(evaluated),
        output_dir / "backtests" / f"setup_b_score_buckets_{DEMO_STAMP}.parquet",
    )
    write_parquet(
        evaluate_setup_b_filter_diagnostics(evaluated),
        output_dir / "backtests" / f"setup_b_filter_diagnostics_{DEMO_STAMP}.parquet",
    )
    write_parquet(
        evaluate_setup_b_indicator_diagnostics(evaluated),
        output_dir / "backtests" / f"setup_b_indicator_diagnostics_{DEMO_STAMP}.parquet",
    )
    setup_b_diagnostics, setup_b_spreads = evaluate_setup_b_bucket_diagnostics(evaluated)
    write_parquet(setup_b_diagnostics, output_dir / "backtests" / f"setup_b_bucket_diagnostics_{DEMO_STAMP}.parquet")
    write_parquet(setup_b_spreads, output_dir / "backtests" / f"setup_b_top_bottom_spreads_{DEMO_STAMP}.parquet")
    write_parquet(evaluate_setup_b_slices(evaluated), output_dir / "backtests" / f"setup_b_slices_{DEMO_STAMP}.parquet")
    write_parquet(
        evaluate_setup_b_interaction_slices(evaluated),
        output_dir / "backtests" / f"setup_b_interaction_slices_{DEMO_STAMP}.parquet",
    )
    write_parquet(
        evaluate_setup_b_variants(evaluated),
        output_dir / "backtests" / f"setup_b_variants_{DEMO_STAMP}.parquet",
    )
    regime_summary, regime_monthly = evaluate_setup_b_market_regime_diagnostics(evaluated)
    write_parquet(regime_summary, output_dir / "backtests" / f"setup_b_market_regime_{DEMO_STAMP}.parquet")
    write_parquet(regime_monthly, output_dir / "backtests" / f"setup_b_market_regime_monthly_{DEMO_STAMP}.parquet")
    write_parquet(
        evaluate_setup_b_benchmark_relative_monthly(evaluated),
        output_dir / "backtests" / f"setup_b_benchmark_relative_monthly_{DEMO_STAMP}.parquet",
    )
    write_parquet(
        evaluate_setup_b_date_declustering(evaluated),
        output_dir / "backtests" / f"setup_b_date_declustered_{DEMO_STAMP}.parquet",
    )
    write_parquet(
        evaluate_setup_b_sector_declustering(evaluated),
        output_dir / "backtests" / f"setup_b_sector_declustered_{DEMO_STAMP}.parquet",
    )
    write_parquet(
        evaluate_setup_b_outlier_diagnostics(evaluated),
        output_dir / "backtests" / f"setup_b_outlier_diagnostics_{DEMO_STAMP}.parquet",
    )
    write_parquet(
        evaluate_setup_b_time_consistency(evaluated),
        output_dir / "backtests" / f"setup_b_time_consistency_{DEMO_STAMP}.parquet",
    )

    (output_dir / "README.md").write_text(
        "# Finding Alpha Demo Data\n\n"
        "Small sanitized read-only dataset for the portfolio dashboard demo.\n\n"
        "This data uses public ticker symbols and local research artifacts. It is not point-in-time, "
        "not investment advice, and not evidence of a validated trading strategy.\n",
        encoding="utf-8",
    )
    print(f"Wrote demo dataset to {output_dir} with {len(demo):,} scored rows and {len(setup_candidates):,} setup candidates.")


if __name__ == "__main__":
    main()
