from __future__ import annotations

import pandas as pd


REQUIRED_BAR_COLUMNS = {"ticker", "date", "open", "high", "low", "close", "adj_close", "volume"}
REQUIRED_INTRADAY_COLUMNS = {"ticker", "timestamp", "open", "high", "low", "close", "volume"}


def validate_daily_bars(bars: pd.DataFrame) -> None:
    missing = REQUIRED_BAR_COLUMNS.difference(bars.columns)
    if missing:
        raise ValueError(f"Missing required bar columns: {sorted(missing)}")
    if (bars[["open", "high", "low", "close", "adj_close"]] < 0).any().any():
        raise ValueError("OHLC prices must be non-negative")
    if (bars["volume"] < 0).any():
        raise ValueError("Volume must be non-negative")
    if (bars["high"] < bars["low"]).any():
        raise ValueError("High must be greater than or equal to low")
    duplicates = bars.duplicated(subset=["ticker", "date"])
    if duplicates.any():
        raise ValueError("Duplicate ticker/date rows found")


def validate_intraday_bars(bars: pd.DataFrame) -> None:
    missing = REQUIRED_INTRADAY_COLUMNS.difference(bars.columns)
    if missing:
        raise ValueError(f"Missing required intraday columns: {sorted(missing)}")
    if (bars[["open", "high", "low", "close"]] < 0).any().any():
        raise ValueError("Intraday OHLC prices must be non-negative")
    if (bars["volume"] < 0).any():
        raise ValueError("Intraday volume must be non-negative")
    if (bars["high"] < bars["low"]).any():
        raise ValueError("Intraday high must be greater than or equal to low")
    duplicates = bars.duplicated(subset=["ticker", "timestamp"])
    if duplicates.any():
        raise ValueError("Duplicate ticker/timestamp rows found")
