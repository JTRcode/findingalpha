from __future__ import annotations

import math

import pandas as pd

from trading_screener.research.forward_returns import HORIZONS, add_forward_returns


def evaluate_daily_setups(scored_history: pd.DataFrame, min_score: float = 0.65) -> pd.DataFrame:
    df = add_forward_returns(scored_history)
    rows: list[dict[str, object]] = []
    candidates = df[(df["best_daily_setup_score"] >= min_score) & (df["best_daily_setup"] != "none")]
    for setup_name, group in candidates.groupby("best_daily_setup"):
        for horizon in HORIZONS:
            column = f"fwd_return_{horizon}d"
            valid = group[column].dropna()
            if valid.empty:
                continue
            rows.append(
                {
                    "setup": setup_name,
                    "horizon_days": horizon,
                    "count": int(valid.count()),
                    "mean": float(valid.mean()),
                    "median": float(valid.median()),
                    "win_rate": float((valid > 0).mean()),
                }
            )
    return pd.DataFrame(rows)


def evaluate_setup_b_score_buckets(scored_history: pd.DataFrame, buckets: int = 5) -> pd.DataFrame:
    setup_b = _setup_b_bucket_frame(scored_history, buckets=buckets)
    if setup_b.empty:
        return pd.DataFrame()

    rows: list[dict[str, object]] = []
    for horizon in HORIZONS:
        column = f"fwd_return_{horizon}d"
        valid = setup_b.dropna(subset=[column, "setup_b_quality_bucket"])
        if valid.empty:
            continue
        grouped = valid.groupby("setup_b_quality_bucket")[column]
        summary = grouped.agg(["count", "mean", "median"]).reset_index()
        summary["win_rate"] = grouped.apply(lambda s: (s > 0).mean()).to_numpy()
        summary["horizon_days"] = horizon
        rows.extend(summary.rename(columns={"setup_b_quality_bucket": "bucket"}).to_dict("records"))
    return pd.DataFrame(rows)


def evaluate_setup_b_bucket_diagnostics(scored_history: pd.DataFrame, buckets: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = _setup_b_bucket_frame(scored_history, buckets=buckets)
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    diagnostics: list[dict[str, object]] = []
    spreads: list[dict[str, object]] = []
    for horizon in HORIZONS:
        column = f"fwd_return_{horizon}d"
        valid = df.dropna(subset=[column, "setup_b_quality_bucket"])
        if valid.empty:
            continue
        grouped = valid.groupby("setup_b_quality_bucket")[column]
        for bucket, returns in grouped:
            std = float(returns.std(ddof=1)) if len(returns) > 1 else 0.0
            stderr = std / math.sqrt(len(returns)) if len(returns) > 1 else 0.0
            mean = float(returns.mean())
            diagnostics.append(
                {
                    "horizon_days": horizon,
                    "bucket": int(bucket),
                    "count": int(len(returns)),
                    "mean": mean,
                    "median": float(returns.median()),
                    "win_rate": float((returns > 0).mean()),
                    "std": std,
                    "stderr": stderr,
                    "t_stat_vs_zero": mean / stderr if stderr > 0 else 0.0,
                }
            )

        bucket_ids = sorted(valid["setup_b_quality_bucket"].dropna().unique())
        if len(bucket_ids) < 2:
            continue
        bottom = valid[valid["setup_b_quality_bucket"] == bucket_ids[0]][column].dropna()
        top = valid[valid["setup_b_quality_bucket"] == bucket_ids[-1]][column].dropna()
        spread_mean = float(top.mean() - bottom.mean())
        spread_median = float(top.median() - bottom.median())
        win_rate_spread = float((top > 0).mean() - (bottom > 0).mean())
        spread_stderr = _independent_spread_stderr(top, bottom)
        spreads.append(
            {
                "horizon_days": horizon,
                "bottom_bucket": int(bucket_ids[0]),
                "top_bucket": int(bucket_ids[-1]),
                "bottom_count": int(len(bottom)),
                "top_count": int(len(top)),
                "mean_spread": spread_mean,
                "median_spread": spread_median,
                "win_rate_spread": win_rate_spread,
                "spread_t_stat": spread_mean / spread_stderr if spread_stderr > 0 else 0.0,
                "interpretation": interpret_setup_b_spread(horizon, spread_mean, win_rate_spread, spread_mean / spread_stderr if spread_stderr > 0 else 0.0),
            }
        )
    return pd.DataFrame(diagnostics), pd.DataFrame(spreads)


def evaluate_setup_b_slices(scored_history: pd.DataFrame) -> pd.DataFrame:
    full_history = add_forward_returns(scored_history)
    df = _setup_b_bucket_frame(full_history)
    if df.empty:
        return pd.DataFrame()

    df = _add_setup_b_slice_columns(df, full_history)
    slice_columns = [
        "market_regime",
        "pullback_depth_slice",
        "pullback_duration_slice",
        "volume_dryup_slice",
        "trend_strength_slice",
        "confirmation_quality_slice",
        "atr_slice",
    ]

    rows: list[dict[str, object]] = []
    for slice_column in slice_columns:
        for slice_value, group in df.dropna(subset=[slice_column]).groupby(slice_column):
            for horizon in HORIZONS:
                column = f"fwd_return_{horizon}d"
                valid = group[column].dropna()
                if valid.empty:
                    continue
                rows.append(
                    {
                        "slice": slice_column,
                        "value": str(slice_value),
                        "horizon_days": horizon,
                        "count": int(valid.count()),
                        "mean": float(valid.mean()),
                        "median": float(valid.median()),
                        "win_rate": float((valid > 0).mean()),
                    }
                )
    return pd.DataFrame(rows)


def evaluate_setup_b_interaction_slices(scored_history: pd.DataFrame) -> pd.DataFrame:
    full_history = add_forward_returns(scored_history)
    df = _setup_b_bucket_frame(full_history)
    if df.empty:
        return pd.DataFrame()

    df = _add_setup_b_slice_columns(df, full_history)
    interactions = [
        ("market_regime", "confirmation_quality_slice"),
        ("market_regime", "atr_slice"),
        ("confirmation_quality_slice", "atr_slice"),
        ("confirmation_quality_slice", "pullback_depth_slice"),
        ("pullback_depth_slice", "pullback_duration_slice"),
        ("volume_dryup_slice", "confirmation_quality_slice"),
    ]
    rows: list[dict[str, object]] = []
    for first, second in interactions:
        valid_slice = df.dropna(subset=[first, second]).copy()
        if valid_slice.empty:
            continue
        valid_slice["interaction"] = valid_slice[first].astype(str) + " + " + valid_slice[second].astype(str)
        for interaction_value, group in valid_slice.groupby("interaction"):
            for horizon in HORIZONS:
                column = f"fwd_return_{horizon}d"
                returns = group[column].dropna()
                if returns.empty:
                    continue
                rows.append(
                    {
                        "interaction_pair": f"{first} x {second}",
                        "value": interaction_value,
                        "horizon_days": horizon,
                        "count": int(returns.count()),
                        "mean": float(returns.mean()),
                        "median": float(returns.median()),
                        "win_rate": float((returns > 0).mean()),
                    }
                )
    return pd.DataFrame(rows)


def evaluate_setup_b_variants(scored_history: pd.DataFrame, benchmark_ticker: str = "SPY") -> pd.DataFrame:
    full_history = add_forward_returns(scored_history)
    df = _setup_b_bucket_frame(full_history)
    if df.empty:
        return pd.DataFrame()

    df = add_setup_b_variant_columns(df, full_history, benchmark_ticker=benchmark_ticker)
    rows: list[dict[str, object]] = []
    for variant, group in df.groupby("setup_b_variant"):
        for horizon in HORIZONS:
            column = f"fwd_return_{horizon}d"
            valid = group[column].dropna()
            if valid.empty:
                continue
            row: dict[str, object] = {
                "variant": str(variant),
                "horizon_days": horizon,
                "count": int(valid.count()),
                "mean": float(valid.mean()),
                "median": float(valid.median()),
                "win_rate": float((valid > 0).mean()),
            }

            relative_column = f"rel_fwd_return_{horizon}d_vs_{benchmark_ticker.lower()}"
            relative = group[relative_column].dropna() if relative_column in group else pd.Series(dtype=float)
            if not relative.empty:
                row.update(
                    {
                        "benchmark": benchmark_ticker,
                        "relative_count": int(relative.count()),
                        "relative_mean": float(relative.mean()),
                        "relative_median": float(relative.median()),
                        "relative_win_rate": float((relative > 0).mean()),
                    }
                )
            rows.append(row)
    return pd.DataFrame(rows)


def evaluate_setup_b_market_regime_diagnostics(
    scored_history: pd.DataFrame,
    benchmark_ticker: str = "SPY",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    full_history = add_forward_returns(scored_history)
    df = _setup_b_bucket_frame(full_history)
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = add_setup_b_variant_columns(df, full_history, benchmark_ticker=benchmark_ticker)
    summary = _summarize_market_regime_groups(df, ["market_regime"], benchmark_ticker=benchmark_ticker)
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    monthly = _summarize_market_regime_groups(df, ["month", "market_regime"], benchmark_ticker=benchmark_ticker)
    return summary, monthly


def evaluate_setup_b_benchmark_relative_monthly(
    scored_history: pd.DataFrame,
    benchmark_tickers: tuple[str, ...] = ("SPY", "QQQ"),
) -> pd.DataFrame:
    df = _setup_b_analysis_frame(scored_history, benchmark_tickers=benchmark_tickers)
    if df.empty:
        return pd.DataFrame()
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)

    rows: list[dict[str, object]] = []
    group_specs = [
        ("all_setup_b", None),
        ("score_bucket", "setup_b_quality_bucket"),
        ("atr_slice", "atr_slice"),
        ("trend_strength_slice", "trend_strength_slice"),
        ("variant", "setup_b_variant"),
    ]
    for benchmark in benchmark_tickers:
        benchmark_key = benchmark.lower()
        for horizon in HORIZONS:
            relative_column = f"rel_fwd_return_{horizon}d_vs_{benchmark_key}"
            if relative_column not in df:
                continue
            for group_type, group_column in group_specs:
                if group_column is None:
                    grouped = [(("all",), df)]
                    key_columns = ["group_value"]
                else:
                    grouped = df.dropna(subset=[group_column]).groupby(group_column)
                    key_columns = ["group_value"]
                for group_value, group in grouped:
                    if isinstance(group_value, tuple):
                        group_value = group_value[0]
                    for month, month_group in group.groupby("month"):
                        returns = month_group[relative_column].dropna()
                        absolute = month_group[f"fwd_return_{horizon}d"].dropna()
                        if returns.empty or absolute.empty:
                            continue
                        rows.append(
                            {
                                "benchmark": benchmark,
                                "horizon_days": horizon,
                                "month": month,
                                "group_type": group_type,
                                key_columns[0]: str(group_value),
                                "count": int(returns.count()),
                                "absolute_mean": float(absolute.mean()),
                                "relative_mean": float(returns.mean()),
                                "relative_median": float(returns.median()),
                                "relative_win_rate": float((returns > 0).mean()),
                            }
                        )
    return pd.DataFrame(rows)


def evaluate_setup_b_date_declustering(
    scored_history: pd.DataFrame,
    benchmark_tickers: tuple[str, ...] = ("SPY", "QQQ"),
) -> pd.DataFrame:
    df = _setup_b_analysis_frame(scored_history, benchmark_tickers=benchmark_tickers)
    if df.empty:
        return pd.DataFrame()

    rows: list[dict[str, object]] = []
    group_specs = [
        ("score_bucket", "setup_b_quality_bucket"),
        ("atr_slice", "atr_slice"),
        ("trend_strength_slice", "trend_strength_slice"),
        ("variant", "setup_b_variant"),
    ]
    for benchmark in benchmark_tickers:
        benchmark_key = benchmark.lower()
        for horizon in HORIZONS:
            relative_column = f"rel_fwd_return_{horizon}d_vs_{benchmark_key}"
            if relative_column not in df:
                continue
            for group_type, group_column in group_specs:
                valid = df.dropna(subset=[group_column, relative_column]).copy()
                if valid.empty:
                    continue
                by_date = (
                    valid.groupby(["date", group_column], observed=True)
                    .agg(
                        candidates=("ticker", "count"),
                        absolute_return=(f"fwd_return_{horizon}d", "mean"),
                        relative_return=(relative_column, "mean"),
                        strict_rate=("setup_b_strict_gate", "mean"),
                    )
                    .reset_index()
                )
                for group_value, group in by_date.groupby(group_column, observed=True):
                    relative = group["relative_return"].dropna()
                    absolute = group["absolute_return"].dropna()
                    if relative.empty or absolute.empty:
                        continue
                    rows.append(
                        {
                            "benchmark": benchmark,
                            "horizon_days": horizon,
                            "group_type": group_type,
                            "group_value": str(group_value),
                            "candidate_count": int(group["candidates"].sum()),
                            "date_count": int(relative.count()),
                            "avg_candidates_per_date": float(group["candidates"].mean()),
                            "date_declustered_absolute_mean": float(absolute.mean()),
                            "date_declustered_relative_mean": float(relative.mean()),
                            "date_declustered_relative_median": float(relative.median()),
                            "date_declustered_relative_win_rate": float((relative > 0).mean()),
                            "avg_strict_rate": float(group["strict_rate"].mean()),
                        }
                    )
    return pd.DataFrame(rows)


def evaluate_setup_b_sector_declustering(scored_history: pd.DataFrame) -> pd.DataFrame:
    sector_column = next((column for column in ["sector", "gics_sector", "industry"] if column in scored_history.columns), None)
    if sector_column is None:
        return pd.DataFrame(
            [
                {
                    "status": "sector_metadata_missing",
                    "message": "Sector de-clustering requires a sector, gics_sector, or industry column in scored history.",
                }
            ]
        )
    df = _setup_b_analysis_frame(scored_history)
    if df.empty or sector_column not in df:
        return pd.DataFrame()
    return pd.DataFrame(
        [
            {
                "status": "not_implemented",
                "message": "Sector metadata exists, but sector-neutral Setup B diagnostics have not been implemented for this schema yet.",
            }
        ]
    )


def add_setup_b_variant_columns(
    setup_b_frame: pd.DataFrame,
    benchmark_source: pd.DataFrame | None = None,
    benchmark_ticker: str = "SPY",
) -> pd.DataFrame:
    out = _add_setup_b_slice_columns(setup_b_frame, benchmark_source)
    positive_market = out["market_regime"].astype(str).isin(["spy_positive", "qqq_positive"])

    conservative = (
        positive_market
        & out["atr_slice"].astype(str).isin(["low_atr", "medium_atr"])
        & (out["confirmation_quality_slice"].astype(str) == "strong_confirmation")
        & out["volume_dryup_slice"].astype(str).isin(["moderate_dryup", "strong_dryup"])
    )
    momentum_rebound = (
        positive_market
        & (out["atr_slice"].astype(str) == "high_atr")
        & (out["confirmation_quality_slice"].astype(str) == "strong_confirmation")
        & (out["volume_dryup_slice"].astype(str) == "strong_dryup")
    )
    high_atr_watch = (
        positive_market
        & (out["atr_slice"].astype(str) == "high_atr")
        & out["confirmation_quality_slice"].astype(str).isin(["moderate_confirmation", "strong_confirmation"])
    )

    out["setup_b_variant"] = "other_setup_b"
    out.loc[high_atr_watch, "setup_b_variant"] = "high_atr_watch"
    out.loc[conservative, "setup_b_variant"] = "conservative_continuation"
    out.loc[momentum_rebound, "setup_b_variant"] = "momentum_rebound"
    out["setup_b_variant_reason"] = out["setup_b_variant"].map(SETUP_B_VARIANT_REASONS).fillna("")
    out = _add_benchmark_relative_forward_returns(out, benchmark_source, benchmark_ticker)
    return out


def interpret_setup_b_spread(horizon: int, mean_spread: float, win_rate_spread: float, t_stat: float) -> str:
    abs_t = abs(t_stat)
    if mean_spread <= 0:
        return "weak_or_negative"
    if mean_spread >= 0.01 and win_rate_spread >= 0.05 and abs_t >= 2:
        return "promising"
    if mean_spread >= 0.005 and win_rate_spread >= 0.02 and abs_t >= 1.5:
        return "interesting"
    if mean_spread >= 0.002:
        return "small_edge_watch"
    return "likely_too_small"


def _add_setup_b_slice_columns(df: pd.DataFrame, benchmark_source: pd.DataFrame | None = None) -> pd.DataFrame:
    out = df.copy()
    source = benchmark_source if benchmark_source is not None else out
    benchmark_ticker = "SPY" if (source["ticker"] == "SPY").any() else "QQQ" if (source["ticker"] == "QQQ").any() else None
    if benchmark_ticker is None:
        out["market_regime"] = "benchmark_missing"
    else:
        benchmark = source[source["ticker"] == benchmark_ticker][["date", "price_vs_sma50", "momentum_20d"]].rename(
            columns={"price_vs_sma50": "spy_price_vs_sma50", "momentum_20d": "spy_momentum_20d"}
        )
        benchmark = benchmark.drop_duplicates(subset=["date"], keep="last")
        out = out.merge(benchmark, on="date", how="left")
        out["market_regime"] = "benchmark_missing_for_date"
        positive_market = (out["spy_price_vs_sma50"] > 0) & (out["spy_momentum_20d"] > 0)
        negative_market = (out["spy_price_vs_sma50"] <= 0) | (out["spy_momentum_20d"] <= 0)
        out.loc[positive_market, "market_regime"] = f"{benchmark_ticker.lower()}_positive"
        out.loc[negative_market, "market_regime"] = f"{benchmark_ticker.lower()}_weak_or_chop"

    depth = out["pullback_from_10d_high"].abs()
    out["pullback_depth_slice"] = pd.cut(
        depth,
        bins=[0, 0.025, 0.045, 0.07, 1],
        labels=["shallow_0_2p5", "ideal_2p5_4p5", "deep_4p5_7", "too_deep"],
        include_lowest=True,
    )
    out["pullback_duration_slice"] = pd.cut(
        out["pullback_days_7d"],
        bins=[0, 2, 4, 6, 10],
        labels=["short_1_2", "ideal_3_4", "long_5_6", "too_long"],
        include_lowest=True,
    )
    out["volume_dryup_slice"] = pd.cut(
        out["setup_b_volume_quality"],
        bins=[-0.01, 0.33, 0.66, 1.0],
        labels=["weak_dryup", "moderate_dryup", "strong_dryup"],
    )
    out["trend_strength_slice"] = pd.cut(
        out["setup_b_trend_quality"],
        bins=[-0.01, 0.33, 0.66, 1.0],
        labels=["weak_trend_quality", "moderate_trend_quality", "strong_trend_quality"],
    )
    out["confirmation_quality_slice"] = pd.cut(
        out["setup_b_confirmation_quality"],
        bins=[-0.01, 0.33, 0.66, 1.0],
        labels=["weak_confirmation", "moderate_confirmation", "strong_confirmation"],
    )
    out["atr_slice"] = pd.cut(
        out["atr_pct"],
        bins=[0, 0.025, 0.05, 1],
        labels=["low_atr", "medium_atr", "high_atr"],
        include_lowest=True,
    )
    return out


def add_setup_b_slice_columns_for_dashboard(scored_history: pd.DataFrame) -> pd.DataFrame:
    full_history = add_forward_returns(scored_history)
    return add_setup_b_variant_columns(_setup_b_bucket_frame(full_history), full_history)


def _setup_b_analysis_frame(
    scored_history: pd.DataFrame,
    benchmark_tickers: tuple[str, ...] = ("SPY", "QQQ"),
) -> pd.DataFrame:
    full_history = add_forward_returns(scored_history)
    df = _setup_b_bucket_frame(full_history)
    if df.empty:
        return df
    df = add_setup_b_variant_columns(df, full_history, benchmark_ticker=benchmark_tickers[0])
    for benchmark_ticker in benchmark_tickers[1:]:
        df = _add_benchmark_relative_forward_returns(df, full_history, benchmark_ticker)
    return df


def _setup_b_bucket_frame(scored_history: pd.DataFrame, buckets: int = 5) -> pd.DataFrame:
    df = add_forward_returns(scored_history)
    setup_b = df[(df["best_daily_setup"] == "setup_b_trend_pullback") & (df["daily_setup_b_trend_pullback_score"] > 0)]
    if setup_b.empty:
        return setup_b.copy()
    required_columns = [
        "ticker",
        "date",
        "adj_close",
        "close",
        "best_daily_setup",
        "setup_b_scanner_gate",
        "setup_b_strict_gate",
        "setup_b_trend_gate",
        "setup_b_pullback_gate",
        "setup_b_volume_dryup_gate",
        "setup_b_structure_gate",
        "setup_b_confirmation_gate",
        "daily_setup_b_trend_pullback_score",
        "price_vs_sma50",
        "momentum_20d",
        "pullback_from_10d_high",
        "pullback_days_7d",
        "setup_b_volume_quality",
        "setup_b_trend_quality",
        "setup_b_confirmation_quality",
        "atr_pct",
        *[f"fwd_return_{horizon}d" for horizon in HORIZONS],
    ]
    setup_b = setup_b[[column for column in required_columns if column in setup_b.columns]].copy()
    setup_b["setup_b_quality_bucket"] = setup_b.groupby("date", group_keys=False)[
        "daily_setup_b_trend_pullback_score"
    ].transform(lambda s: pd.qcut(s.rank(method="first"), q=min(buckets, len(s)), labels=False, duplicates="drop") + 1)
    return setup_b


def _independent_spread_stderr(top: pd.Series, bottom: pd.Series) -> float:
    if len(top) < 2 or len(bottom) < 2:
        return 0.0
    return math.sqrt((top.var(ddof=1) / len(top)) + (bottom.var(ddof=1) / len(bottom)))


def _add_benchmark_relative_forward_returns(
    df: pd.DataFrame,
    benchmark_source: pd.DataFrame | None,
    benchmark_ticker: str,
) -> pd.DataFrame:
    out = df.copy()
    if benchmark_source is None or "ticker" not in benchmark_source or benchmark_ticker not in set(benchmark_source["ticker"]):
        return out

    benchmark_columns = ["date"] + [f"fwd_return_{horizon}d" for horizon in HORIZONS]
    available_columns = [column for column in benchmark_columns if column in benchmark_source.columns]
    benchmark = benchmark_source[benchmark_source["ticker"] == benchmark_ticker][available_columns].copy()
    if benchmark.empty:
        return out
    benchmark = benchmark.drop_duplicates(subset=["date"], keep="last")
    benchmark = benchmark.rename(
        columns={
            f"fwd_return_{horizon}d": f"benchmark_{benchmark_ticker.lower()}_fwd_return_{horizon}d"
            for horizon in HORIZONS
            if f"fwd_return_{horizon}d" in benchmark.columns
        }
    )
    out = out.merge(benchmark, on="date", how="left")
    for horizon in HORIZONS:
        candidate_column = f"fwd_return_{horizon}d"
        benchmark_column = f"benchmark_{benchmark_ticker.lower()}_fwd_return_{horizon}d"
        if candidate_column in out and benchmark_column in out:
            out[f"rel_fwd_return_{horizon}d_vs_{benchmark_ticker.lower()}"] = out[candidate_column] - out[benchmark_column]
    return out


def _summarize_market_regime_groups(
    df: pd.DataFrame,
    group_columns: list[str],
    benchmark_ticker: str,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for group_key, group in df.groupby(group_columns):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        base = dict(zip(group_columns, group_key, strict=True))
        for horizon in HORIZONS:
            column = f"fwd_return_{horizon}d"
            valid = group[column].dropna()
            if valid.empty:
                continue
            row: dict[str, object] = {
                **base,
                "horizon_days": horizon,
                "count": int(valid.count()),
                "mean": float(valid.mean()),
                "median": float(valid.median()),
                "win_rate": float((valid > 0).mean()),
            }
            relative_column = f"rel_fwd_return_{horizon}d_vs_{benchmark_ticker.lower()}"
            relative = group[relative_column].dropna() if relative_column in group else pd.Series(dtype=float)
            if not relative.empty:
                row.update(
                    {
                        "benchmark": benchmark_ticker,
                        "relative_count": int(relative.count()),
                        "relative_mean": float(relative.mean()),
                        "relative_median": float(relative.median()),
                        "relative_win_rate": float((relative > 0).mean()),
                    }
                )
            rows.append(row)
    return pd.DataFrame(rows)


SETUP_B_VARIANT_REASONS = {
    "conservative_continuation": "Positive benchmark regime, low/medium ATR, strong confirmation, and at least moderate volume dry-up.",
    "momentum_rebound": "Positive benchmark regime, high ATR, strong confirmation, and strong volume dry-up.",
    "high_atr_watch": "Positive benchmark regime with high ATR and at least moderate confirmation; exploratory, higher volatility.",
    "other_setup_b": "Setup B candidate that does not match the stricter research variants.",
}
