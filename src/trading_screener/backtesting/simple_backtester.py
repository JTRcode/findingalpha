from __future__ import annotations

import pandas as pd

from trading_screener.research.forward_returns import add_forward_returns


def simple_top_ranked_basket(scored_history: pd.DataFrame, top_n: int = 5, horizon: int = 5) -> pd.DataFrame:
    if f"fwd_return_{horizon}d" not in scored_history.columns:
        scored_history = add_forward_returns(scored_history, horizons=(horizon,))
    df = scored_history.sort_values(["date", "composite_score"], ascending=[True, False]).copy()
    picks = df.groupby("date").head(top_n)
    returns = picks.groupby("date")[f"fwd_return_{horizon}d"].mean().dropna()
    out = returns.rename("basket_return").reset_index()
    out["equity_curve"] = (1 + out["basket_return"]).cumprod()
    out["drawdown"] = out["equity_curve"] / out["equity_curve"].cummax() - 1
    holdings = picks.groupby("date")["ticker"].apply(set)
    previous = holdings.shift(1)
    turnover = []
    for date_value, current in holdings.items():
        prior = previous.loc[date_value]
        if not isinstance(prior, set) or not prior:
            turnover.append({"date": date_value, "turnover_estimate": 1.0})
            continue
        changed = len(current.symmetric_difference(prior))
        turnover.append({"date": date_value, "turnover_estimate": changed / max(len(current), len(prior), 1)})
    turnover_df = pd.DataFrame(turnover)
    out = out.merge(turnover_df, on="date", how="left")
    return out
