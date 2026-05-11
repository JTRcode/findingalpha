from __future__ import annotations

import pandas as pd

from trading_screener.research.forward_returns import HORIZONS, add_forward_returns


def assign_score_buckets(df: pd.DataFrame, buckets: int = 5) -> pd.DataFrame:
    out = df.copy()

    def bucket_group(group: pd.DataFrame) -> pd.Series:
        ranked = group["composite_score"].rank(method="first")
        labels = pd.qcut(ranked, q=min(buckets, len(group)), labels=False, duplicates="drop")
        return labels.astype("float") + 1

    out["score_bucket"] = out.groupby("date", group_keys=False).apply(bucket_group)
    return out


def evaluate_score_buckets(scored_history: pd.DataFrame, buckets: int = 5) -> pd.DataFrame:
    df = assign_score_buckets(add_forward_returns(scored_history), buckets=buckets)
    rows: list[dict[str, float | int]] = []
    for horizon in HORIZONS:
        column = f"fwd_return_{horizon}d"
        valid = df.dropna(subset=[column, "score_bucket"])
        if valid.empty:
            continue
        grouped = valid.groupby("score_bucket")[column]
        summary = grouped.agg(["count", "mean", "median"]).reset_index()
        summary["win_rate"] = grouped.apply(lambda s: (s > 0).mean()).to_numpy()
        summary["horizon_days"] = horizon
        rows.extend(summary.to_dict("records"))
    return pd.DataFrame(rows)


def top_bottom_spread(bucket_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for horizon, group in bucket_summary.groupby("horizon_days"):
        top = group.loc[group["score_bucket"].idxmax()]
        bottom = group.loc[group["score_bucket"].idxmin()]
        rows.append(
            {
                "horizon_days": horizon,
                "top_bucket": top["score_bucket"],
                "bottom_bucket": bottom["score_bucket"],
                "mean_spread": top["mean"] - bottom["mean"],
                "median_spread": top["median"] - bottom["median"],
            }
        )
    return pd.DataFrame(rows)


def benchmark_comparison(
    scored_history: pd.DataFrame,
    benchmark_tickers: tuple[str, ...] = ("SPY", "QQQ"),
    top_bucket: float | None = None,
    buckets: int = 5,
) -> pd.DataFrame:
    df = assign_score_buckets(add_forward_returns(scored_history), buckets=buckets)
    if top_bucket is None and not df["score_bucket"].dropna().empty:
        top_bucket = float(df["score_bucket"].max())

    rows: list[dict[str, float | int | str]] = []
    for horizon in HORIZONS:
        column = f"fwd_return_{horizon}d"
        top = df[
            (df["score_bucket"] == top_bucket)
            & (~df["ticker"].isin(benchmark_tickers))
            & df[column].notna()
        ][["date", column]]
        if top.empty:
            continue
        top_by_date = top.groupby("date")[column].mean().rename("top_bucket_return")
        for benchmark in benchmark_tickers:
            bench = df[(df["ticker"] == benchmark) & df[column].notna()][["date", column]]
            if bench.empty:
                continue
            merged = top_by_date.to_frame().join(bench.set_index("date").rename(columns={column: "benchmark_return"}))
            merged = merged.dropna()
            if merged.empty:
                continue
            spread = merged["top_bucket_return"] - merged["benchmark_return"]
            rows.append(
                {
                    "benchmark": benchmark,
                    "horizon_days": horizon,
                    "count": int(len(merged)),
                    "top_bucket_mean": float(merged["top_bucket_return"].mean()),
                    "benchmark_mean": float(merged["benchmark_return"].mean()),
                    "mean_spread": float(spread.mean()),
                    "win_rate_vs_benchmark": float((spread > 0).mean()),
                }
            )
    return pd.DataFrame(rows)


def transaction_cost_sensitivity(
    basket_returns: pd.DataFrame,
    cost_bps: tuple[int, ...] = (0, 5, 10, 25, 50),
) -> pd.DataFrame:
    if basket_returns.empty:
        return pd.DataFrame(columns=["cost_bps", "mean_return", "cumulative_return"])

    rows: list[dict[str, float | int]] = []
    for cost in cost_bps:
        cost_decimal = cost / 10_000
        adjusted = basket_returns["basket_return"] - cost_decimal
        rows.append(
            {
                "cost_bps": cost,
                "mean_return": float(adjusted.mean()),
                "cumulative_return": float((1 + adjusted).prod() - 1),
            }
        )
    return pd.DataFrame(rows)
