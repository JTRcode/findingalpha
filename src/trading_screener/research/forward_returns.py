from __future__ import annotations

import pandas as pd


HORIZONS = (1, 5, 10, 20, 60)


def add_forward_returns(scored_history: pd.DataFrame, horizons: tuple[int, ...] = HORIZONS) -> pd.DataFrame:
    df = scored_history.sort_values(["ticker", "date"]).copy()
    price = df["adj_close"].fillna(df["close"])
    for horizon in horizons:
        future_price = price.groupby(df["ticker"]).shift(-horizon)
        df[f"fwd_return_{horizon}d"] = future_price / price - 1
    return df

