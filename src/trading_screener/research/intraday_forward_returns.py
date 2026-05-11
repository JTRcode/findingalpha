from __future__ import annotations

import pandas as pd


INTRADAY_HORIZONS_MINUTES = (30, 60, 120, 390)


def add_intraday_forward_returns(
    scored_intraday: pd.DataFrame,
    horizons: tuple[int, ...] = INTRADAY_HORIZONS_MINUTES,
) -> pd.DataFrame:
    df = scored_intraday.sort_values(["ticker", "timestamp"]).copy()
    price = df["close"]
    for horizon in horizons:
        future_price = price.groupby(df["ticker"]).shift(-horizon)
        df[f"fwd_return_{horizon}m"] = future_price / price - 1
    return df

