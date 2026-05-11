from __future__ import annotations

import pandas as pd

from trading_screener.features.technicals import add_technical_features


def sample_bars(days: int = 70) -> pd.DataFrame:
    rows = []
    dates = pd.date_range("2024-01-01", periods=days, freq="B")
    for ticker, offset in [("AAA", 0), ("BBB", 10)]:
        for i, day in enumerate(dates):
            close = 100 + offset + i
            rows.append(
                {
                    "ticker": ticker,
                    "date": day.date(),
                    "open": close - 0.5,
                    "high": close + 1,
                    "low": close - 1,
                    "close": close,
                    "adj_close": close,
                    "volume": 1_000_000 + i * 1000,
                }
            )
    return pd.DataFrame(rows)


def test_add_technical_features_calculates_expected_columns() -> None:
    features = add_technical_features(sample_bars())
    last = features[features["ticker"] == "AAA"].iloc[-1]

    assert "momentum_20d" in features.columns
    assert "relative_volume" in features.columns
    assert "atr_pct" in features.columns
    assert last["momentum_20d"] > 0
    assert last["proximity_52w_high"] == 1

