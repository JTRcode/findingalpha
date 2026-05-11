from __future__ import annotations

from tests.test_features import sample_bars
from trading_screener.signals.screeners import build_ranked_screen


def test_build_ranked_screen_snapshot_schema() -> None:
    screen = build_ranked_screen(
        bars=sample_bars(days=90),
        provider="test",
        universe="AAA,BBB",
        config_version="test-config",
        code_version="test-code",
    )

    required = {
        "run_timestamp_utc",
        "provider",
        "market_data_timestamp",
        "ticker",
        "price",
        "volume",
        "composite_score",
        "signal_explanation",
        "risk_flags",
        "universe",
        "config_version",
        "code_version",
    }
    assert required.issubset(screen.columns)
    assert list(screen["composite_score"]) == sorted(screen["composite_score"], reverse=True)

