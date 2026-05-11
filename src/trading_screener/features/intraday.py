from __future__ import annotations

import numpy as np
import pandas as pd


def add_intraday_features(bars: pd.DataFrame) -> pd.DataFrame:
    df = bars.sort_values(["ticker", "timestamp"]).copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    eastern = df["timestamp"].dt.tz_convert("America/New_York")
    df["session_date"] = eastern.dt.date
    df["minute_of_day"] = eastern.dt.hour * 60 + eastern.dt.minute

    grouped = df.groupby(["ticker", "session_date"], group_keys=False)
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    cumulative_pv = (typical_price * df["volume"]).groupby([df["ticker"], df["session_date"]]).cumsum()
    cumulative_volume = df["volume"].groupby([df["ticker"], df["session_date"]]).cumsum()
    calculated_vwap = cumulative_pv / cumulative_volume.replace(0, np.nan)
    df["session_vwap"] = df.get("vwap", calculated_vwap).fillna(calculated_vwap)
    df["ema_20"] = grouped["close"].transform(lambda s: s.ewm(span=20, adjust=False, min_periods=5).mean())
    df["price_vs_vwap"] = df["close"] / df["session_vwap"] - 1
    df["price_vs_ema20"] = df["close"] / df["ema_20"] - 1
    df["return_1m"] = df.groupby("ticker")["close"].pct_change()
    df["rolling_high_30m"] = grouped["high"].transform(lambda s: s.rolling(30, min_periods=5).max())
    df["rolling_low_30m"] = grouped["low"].transform(lambda s: s.rolling(30, min_periods=5).min())
    df["range_30m_pct"] = df["rolling_high_30m"] / df["rolling_low_30m"].replace(0, np.nan) - 1
    df["rolling_volume_20m"] = grouped["volume"].transform(lambda s: s.rolling(20, min_periods=5).mean())
    df["relative_volume_20m"] = df["volume"] / df["rolling_volume_20m"].replace(0, np.nan)
    df["volume_spike"] = df["relative_volume_20m"] >= 3
    df["volume_dryup"] = df["relative_volume_20m"] <= 0.6
    previous_close = df.groupby(["ticker", "session_date"])["close"].shift(1)
    previous_vwap_delta = df.groupby(["ticker", "session_date"])["price_vs_vwap"].shift(1)
    df["vwap_reclaim"] = (previous_vwap_delta <= 0) & (df["price_vs_vwap"] > 0) & (df["close"] > previous_close)
    df["vwap_loss"] = (previous_vwap_delta >= 0) & (df["price_vs_vwap"] < 0) & (df["close"] < previous_close)
    df["near_vwap"] = df["price_vs_vwap"].abs() <= 0.0025
    df["near_ema20"] = df["price_vs_ema20"].abs() <= 0.0025
    return df

