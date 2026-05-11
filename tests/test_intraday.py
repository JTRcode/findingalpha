from __future__ import annotations

import pandas as pd

from trading_screener.features.intraday import add_intraday_features
from trading_screener.research.intraday_forward_returns import add_intraday_forward_returns
from trading_screener.signals.playbook import add_intraday_setup_scores, intraday_candidates


def sample_intraday_bars(minutes: int = 80) -> pd.DataFrame:
    rows = []
    timestamps = pd.date_range("2026-05-01 13:30:00Z", periods=minutes, freq="min")
    for i, timestamp in enumerate(timestamps):
        close = 100 + i * 0.03
        rows.append(
            {
                "ticker": "SPY",
                "timestamp": timestamp,
                "open": close - 0.02,
                "high": close + 0.05,
                "low": close - 0.05,
                "close": close,
                "volume": 100_000 if i != 40 else 500_000,
                "trade_count": 100 + i,
                "vwap": close - 0.01,
                "provider": "test",
                "timeframe": "1Min",
                "feed": "iex",
            }
        )
    return pd.DataFrame(rows)


def test_intraday_features_and_setup_scores() -> None:
    features = add_intraday_features(sample_intraday_bars())
    scored = add_intraday_setup_scores(features)
    candidates = intraday_candidates(scored, min_score=0.1)

    assert "session_vwap" in scored.columns
    assert "relative_volume_20m" in scored.columns
    assert "best_intraday_setup" in scored.columns
    assert not candidates.empty


def test_intraday_forward_returns() -> None:
    scored = add_intraday_setup_scores(add_intraday_features(sample_intraday_bars()))
    evaluated = add_intraday_forward_returns(scored, horizons=(30, 60))
    first = evaluated.iloc[0]

    assert "fwd_return_30m" in evaluated.columns
    assert first["fwd_return_30m"] > 0

