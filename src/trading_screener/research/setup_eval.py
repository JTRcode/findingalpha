from __future__ import annotations

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
    df = add_forward_returns(scored_history)
    setup_b = df[df["best_daily_setup"] == "setup_b_trend_pullback"].copy()
    setup_b = setup_b[setup_b["daily_setup_b_trend_pullback_score"] > 0]
    if setup_b.empty:
        return pd.DataFrame()

    setup_b["setup_b_quality_bucket"] = setup_b.groupby("date", group_keys=False)[
        "daily_setup_b_trend_pullback_score"
    ].transform(lambda s: pd.qcut(s.rank(method="first"), q=min(buckets, len(s)), labels=False, duplicates="drop") + 1)

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
