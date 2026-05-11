from __future__ import annotations

import argparse
from datetime import date, timedelta
import warnings

from trading_screener import __version__
from trading_screener.config import default_settings
from trading_screener.backtesting.simple_backtester import simple_top_ranked_basket
from trading_screener.data.providers import get_provider
from trading_screener.data.storage import ensure_data_dirs, utc_timestamp_slug, write_parquet, write_timestamped_outputs
from trading_screener.data.validation import validate_daily_bars, validate_intraday_bars
from trading_screener.features.intraday import add_intraday_features
from trading_screener.features.technicals import add_technical_features
from trading_screener.research.alpha_eval import (
    benchmark_comparison,
    evaluate_score_buckets,
    top_bottom_spread,
    transaction_cost_sensitivity,
)
from trading_screener.research.forward_returns import add_forward_returns
from trading_screener.research.intraday_forward_returns import add_intraday_forward_returns
from trading_screener.research.setup_eval import evaluate_daily_setups, evaluate_setup_b_score_buckets
from trading_screener.signals.daily_playbook import add_daily_playbook_scores, daily_setup_candidates
from trading_screener.signals.scoring import add_composite_score
from trading_screener.signals.playbook import add_intraday_setup_scores, intraday_candidates
from trading_screener.signals.screeners import build_ranked_screen
from trading_screener.universe import load_universe, load_universe_metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Finding Alpha daily research screener")
    parser.add_argument("--tickers", nargs="+", help="Ticker universe")
    parser.add_argument("--universe", help="Named universe from config/universes or path to a ticker file")
    parser.add_argument("--provider", default=None, help="Market data provider")
    parser.add_argument("--start", default=str(date.today() - timedelta(days=365 * 2)))
    parser.add_argument("--end", default=None)
    parser.add_argument("--intraday", action="store_true", help="Also fetch intraday bars")
    parser.add_argument("--intraday-start", default=None, help="Intraday start timestamp/date, e.g. 2026-05-01")
    parser.add_argument("--intraday-end", default=None, help="Intraday end timestamp/date")
    parser.add_argument("--intraday-timeframe", default="1Min", help="Alpaca timeframe such as 1Min or 5Min")
    parser.add_argument("--feed", default=None, help="Alpaca market data feed, e.g. iex or sip")
    parser.add_argument("--intraday-only", action="store_true", help="Skip daily screen and fetch intraday research data only")
    parser.add_argument("--check-provider", action="store_true", help="Fetch one recent bar to validate provider credentials")
    args = parser.parse_args()

    settings = default_settings()
    tickers = args.tickers or (load_universe(args.universe) if args.universe else list(settings.universe))
    if args.universe:
        universe_name = args.universe
    elif args.tickers:
        universe_name = "cli_tickers"
    else:
        universe_name = "default"
    universe_metadata = load_universe_metadata(args.universe)
    provider = get_provider(args.provider or settings.provider)
    ensure_data_dirs(settings.data_dir)

    if not universe_metadata.get("point_in_time", False):
        warnings.warn(
            "Universe is not point-in-time. Historical alpha tests may have survivorship bias. "
            f"Universe: {universe_name}. Notes: {universe_metadata.get('notes', 'none')}",
            stacklevel=1,
        )

    if args.check_provider:
        sample = provider.fetch_daily_bars(tickers=[tickers[0]], start=str(date.today() - timedelta(days=10)), end=None)
        print(f"Provider check OK: {provider.name} returned {len(sample)} rows for {tickers[0]}")
        return

    if not args.intraday_only:
        bars = provider.fetch_daily_bars(tickers=tickers, start=args.start, end=args.end)
        validate_daily_bars(bars)
        if bars["ticker"].nunique() < 5:
            warnings.warn(
                "Daily alpha bucket tests are most useful with at least 5 tickers. "
                f"This run has {bars['ticker'].nunique()} ticker(s), so the dashboard may show only one bucket.",
                stacklevel=1,
            )
        write_parquet(bars, settings.data_dir / "raw" / provider.name / "daily_bars.parquet")
        write_parquet(bars, settings.data_dir / "processed" / "daily_bars.parquet")

        features = add_technical_features(bars)
        scored_history = add_daily_playbook_scores(add_composite_score(features))
        write_parquet(scored_history, settings.data_dir / "features" / "scored_history.parquet")

        screen = build_ranked_screen(
            bars=bars,
            provider=provider.name,
            universe=universe_name,
            config_version=settings.config_version,
            code_version=__version__,
        )
        screen["universe_description"] = universe_metadata.get("description", "")
        screen["universe_point_in_time"] = bool(universe_metadata.get("point_in_time", False))
        screen["universe_survivorship_bias"] = universe_metadata.get("survivorship_bias", "unknown")
        screen["universe_notes"] = universe_metadata.get("notes", "")
        parquet_path, csv_path = write_timestamped_outputs(screen, settings.data_dir / "signals", "signal_snapshot")

        evaluated = add_forward_returns(scored_history)
        bucket_summary = evaluate_score_buckets(evaluated)
        write_timestamped_outputs(bucket_summary, settings.data_dir / "backtests", "forward_return_buckets")
        write_timestamped_outputs(top_bottom_spread(bucket_summary), settings.data_dir / "backtests", "top_bottom_spreads")
        write_timestamped_outputs(
            benchmark_comparison(evaluated, benchmark_tickers=settings.benchmark_tickers),
            settings.data_dir / "backtests",
            "benchmark_comparison",
        )
        basket = simple_top_ranked_basket(evaluated, top_n=5, horizon=5)
        write_timestamped_outputs(basket, settings.data_dir / "backtests", "top_ranked_basket")
        write_timestamped_outputs(
            transaction_cost_sensitivity(basket),
            settings.data_dir / "backtests",
            "transaction_cost_sensitivity",
        )
        setup_candidates = daily_setup_candidates(evaluated)
        write_timestamped_outputs(setup_candidates, settings.data_dir / "signals", "daily_setup_candidates")
        write_timestamped_outputs(evaluate_daily_setups(evaluated), settings.data_dir / "backtests", "daily_setup_forward_returns")
        write_timestamped_outputs(
            evaluate_setup_b_score_buckets(evaluated),
            settings.data_dir / "backtests",
            "setup_b_score_buckets",
        )

        print(f"Wrote signal snapshot: {parquet_path}")
        print(f"Wrote ranked CSV: {csv_path}")

    if args.intraday:
        intraday_start = args.intraday_start or str(date.today() - timedelta(days=30))
        run_slug = utc_timestamp_slug()
        intraday = provider.fetch_intraday_bars(
            tickers=tickers,
            start=intraday_start,
            end=args.intraday_end,
            timeframe=args.intraday_timeframe,
            feed=args.feed or settings.alpaca_data_feed,
        )
        validate_intraday_bars(intraday)
        raw_intraday_path = (
            settings.data_dir
            / "raw"
            / provider.name
            / f"intraday_{args.intraday_timeframe}_{run_slug}.parquet"
        )
        write_parquet(intraday, raw_intraday_path)
        intraday_features = add_intraday_features(intraday)
        intraday_scored = add_intraday_setup_scores(intraday_features)
        intraday_evaluated = add_intraday_forward_returns(intraday_scored)
        feature_path = (
            settings.data_dir
            / "features"
            / provider.name
            / f"intraday_scored_{args.intraday_timeframe}_{run_slug}.parquet"
        )
        write_parquet(intraday_evaluated, feature_path)
        candidate_path, candidate_csv = write_timestamped_outputs(
            intraday_candidates(intraday_evaluated),
            settings.data_dir / "signals" / provider.name,
            "intraday_setup_candidates",
        )
        print(f"Wrote raw intraday bars: {raw_intraday_path}")
        print(f"Wrote intraday scored features: {feature_path}")
        print(f"Wrote intraday setup candidates: {candidate_path}")
        print(f"Wrote intraday setup CSV: {candidate_csv}")
