from __future__ import annotations

import math

import pandas as pd

from trading_screener.research.forward_returns import HORIZONS, add_forward_returns


def evaluate_daily_setups(scored_history: pd.DataFrame, min_score: float = 0.65) -> pd.DataFrame:
    df = add_forward_returns(scored_history)
    rows: list[dict[str, object]] = []
    for setup_name, group in df[df["best_daily_setup_score"] >= min_score].groupby("best_daily_setup"):
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


def _setup_b_bucket_frame(scored_history: pd.DataFrame, buckets: int = 5) -> pd.DataFrame:
    df = add_forward_returns(scored_history)
    setup_b = df[df["best_daily_setup"] == "setup_b_trend_pullback"].copy()
    setup_b = setup_b[setup_b["daily_setup_b_trend_pullback_score"] > 0]
    if setup_b.empty:
        return setup_b
    setup_b["setup_b_quality_bucket"] = setup_b.groupby("date", group_keys=False)[
        "daily_setup_b_trend_pullback_score"
    ].transform(lambda s: pd.qcut(s.rank(method="first"), q=min(buckets, len(s)), labels=False, duplicates="drop") + 1)
    return setup_b


def _independent_spread_stderr(top: pd.Series, bottom: pd.Series) -> float:
    if len(top) < 2 or len(bottom) < 2:
        return 0.0
    return math.sqrt((top.var(ddof=1) / len(top)) + (bottom.var(ddof=1) / len(bottom)))
