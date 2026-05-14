from __future__ import annotations

import numpy as np
import pandas as pd


def add_technical_features(bars: pd.DataFrame) -> pd.DataFrame:
    df = bars.sort_values(["ticker", "date"]).copy()
    grouped = df.groupby("ticker", group_keys=False)
    price = df["adj_close"].fillna(df["close"])

    df["return_1d"] = grouped["adj_close"].pct_change(1)
    df["momentum_5d"] = grouped["adj_close"].pct_change(5)
    df["momentum_20d"] = grouped["adj_close"].pct_change(20)
    df["momentum_60d"] = grouped["adj_close"].pct_change(60)
    df["roc_5d"] = df["momentum_5d"]
    df["roc_10d"] = grouped["adj_close"].pct_change(10)
    df["roc_20d"] = df["momentum_20d"]
    df["accel_5_20"] = df["roc_5d"] - (df["roc_20d"] / 4)
    df["sma_20"] = grouped["adj_close"].transform(lambda s: s.rolling(20, min_periods=5).mean())
    df["sma_50"] = grouped["adj_close"].transform(lambda s: s.rolling(50, min_periods=10).mean())
    df["sma_200"] = grouped["adj_close"].transform(lambda s: s.rolling(200, min_periods=50).mean())
    df["sma20_slope_5d"] = df["sma_20"] / grouped["sma_20"].shift(5) - 1
    df["sma50_slope_10d"] = df["sma_50"] / grouped["sma_50"].shift(10) - 1
    df["linreg_slope_20d"] = grouped["adj_close"].transform(
        lambda s: s.rolling(20, min_periods=10).apply(_linear_regression_slope_pct, raw=True)
    )
    df["price_vs_sma20"] = price / df["sma_20"] - 1
    df["price_vs_sma50"] = price / df["sma_50"] - 1
    df["price_vs_sma200"] = price / df["sma_200"] - 1
    df["avg_volume_20d"] = grouped["volume"].transform(lambda s: s.rolling(20, min_periods=5).mean())
    df["relative_volume"] = df["volume"] / df["avg_volume_20d"]
    df["high_52w"] = grouped["adj_close"].transform(lambda s: s.rolling(252, min_periods=20).max())
    df["proximity_52w_high"] = price / df["high_52w"]

    prev_close = grouped["close"].shift(1)
    tr_components = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    )
    df["true_range"] = tr_components.max(axis=1)
    df["atr_14"] = df.groupby("ticker")["true_range"].transform(lambda s: s.rolling(14, min_periods=5).mean())
    df["atr_pct"] = df["atr_14"] / price.replace(0, np.nan)
    prior_high = grouped["high"].shift(1)
    prior_low = grouped["low"].shift(1)
    up_move = df["high"] - prior_high
    down_move = prior_low - df["low"]
    df["plus_dm"] = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    df["minus_dm"] = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    df["plus_di_14"] = 100 * grouped["plus_dm"].transform(lambda s: s.rolling(14, min_periods=5).mean()) / df["atr_14"].replace(0, np.nan)
    df["minus_di_14"] = 100 * grouped["minus_dm"].transform(lambda s: s.rolling(14, min_periods=5).mean()) / df["atr_14"].replace(0, np.nan)
    dx = ((df["plus_di_14"] - df["minus_di_14"]).abs() / (df["plus_di_14"] + df["minus_di_14"]).replace(0, np.nan)) * 100
    df["adx_14"] = dx.groupby(df["ticker"]).transform(lambda s: s.rolling(14, min_periods=5).mean())
    df["gap_pct"] = df["open"] / prev_close - 1
    df["dollar_volume"] = price * df["volume"]
    df["pullback_from_10d_high"] = price / grouped["adj_close"].transform(lambda s: s.rolling(10, min_periods=3).max()) - 1
    df["extension_from_20d_low"] = price / grouped["adj_close"].transform(lambda s: s.rolling(20, min_periods=5).min()) - 1
    df["down_day"] = df["return_1d"] < 0
    df["up_day"] = df["return_1d"] > 0
    df["down_days_5d"] = grouped["down_day"].transform(lambda s: s.rolling(5, min_periods=1).sum())
    df["up_days_5d"] = grouped["up_day"].transform(lambda s: s.rolling(5, min_periods=1).sum())
    df["volume_vs_5d"] = df["volume"] / grouped["volume"].transform(lambda s: s.rolling(5, min_periods=2).mean())
    df["close_position_in_range"] = (df["close"] - df["low"]) / (df["high"] - df["low"]).replace(0, np.nan)
    df["close_position_in_range"] = df["close_position_in_range"].clip(0, 1)
    df["prior_day_high"] = grouped["high"].shift(1)
    df["prior_day_low"] = grouped["low"].shift(1)
    df["reclaims_prior_high"] = df["close"] > df["prior_day_high"]
    df["breaks_prior_low"] = df["close"] < df["prior_day_low"]
    df["pullback_days_7d"] = grouped["down_day"].transform(lambda s: s.rolling(7, min_periods=1).sum())
    df["pullback_volume_avg_5d"] = grouped["volume"].transform(lambda s: s.rolling(5, min_periods=2).mean())
    df["pre_pullback_volume_avg_20d"] = grouped["volume"].transform(lambda s: s.shift(5).rolling(20, min_periods=5).mean())
    df["pullback_volume_ratio"] = df["pullback_volume_avg_5d"] / df["pre_pullback_volume_avg_20d"]
    df["large_red_candle"] = (df["return_1d"] < -(1.25 * df["atr_pct"].fillna(0))) & (df["close_position_in_range"] < 0.35)
    df["large_red_candles_5d"] = grouped["large_red_candle"].transform(lambda s: s.rolling(5, min_periods=1).sum())
    df["higher_low_count_5d"] = grouped["low"].transform(lambda s: (s > s.shift(1)).rolling(5, min_periods=1).sum())
    df["orderly_pullback_proxy"] = (df["large_red_candles_5d"] == 0) & (df["higher_low_count_5d"] >= 1)
    delta = grouped["adj_close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.groupby(df["ticker"]).transform(lambda s: s.rolling(14, min_periods=5).mean())
    avg_loss = loss.groupby(df["ticker"]).transform(lambda s: s.rolling(14, min_periods=5).mean())
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi_14"] = 100 - (100 / (1 + rs))
    df.loc[(avg_loss == 0) & (avg_gain > 0), "rsi_14"] = 100
    df["rsi_14_change_3d"] = grouped["rsi_14"].diff(3)
    df["rsi_was_overbought_10d"] = grouped["rsi_14"].transform(lambda s: s.rolling(10, min_periods=3).max()) >= 70
    df["rsi_reset_zone"] = df["rsi_14"].between(40, 60) & df["rsi_was_overbought_10d"]
    ema_12 = grouped["adj_close"].transform(lambda s: s.ewm(span=12, adjust=False, min_periods=12).mean())
    ema_26 = grouped["adj_close"].transform(lambda s: s.ewm(span=26, adjust=False, min_periods=26).mean())
    df["macd_line"] = ema_12 - ema_26
    df["macd_signal"] = df.groupby("ticker")["macd_line"].transform(lambda s: s.ewm(span=9, adjust=False, min_periods=9).mean())
    df["macd_hist"] = df["macd_line"] - df["macd_signal"]
    df["macd_hist_change_3d"] = grouped["macd_hist"].diff(3)
    df["macd_hist_turning_up"] = df["macd_hist_change_3d"] > 0
    return df


def _linear_regression_slope_pct(values: np.ndarray) -> float:
    valid = values[~np.isnan(values)]
    if len(valid) < 2:
        return np.nan
    mean = float(np.mean(valid))
    if mean == 0:
        return np.nan
    x = np.arange(len(valid), dtype=float)
    slope = np.polyfit(x, valid, 1)[0]
    return float(slope / mean)
