from __future__ import annotations

import pandas as pd


HORIZONS = (1, 5, 10, 20, 60)


def add_forward_returns(
    scored_history: pd.DataFrame,
    horizons: tuple[int, ...] = HORIZONS,
    copy: bool = True,
) -> pd.DataFrame:
    forward_columns = [f"fwd_return_{horizon}d" for horizon in horizons]
    if all(column in scored_history.columns for column in forward_columns):
        return scored_history

    df = scored_history.copy() if copy else scored_history
    df.sort_values(["ticker", "date"], inplace=True, ignore_index=True)
    price = df["adj_close"].fillna(df["close"])
    for horizon in horizons:
        future_price = price.groupby(df["ticker"]).shift(-horizon)
        df[f"fwd_return_{horizon}d"] = future_price / price - 1
    return df
