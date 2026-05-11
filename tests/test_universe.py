from __future__ import annotations

from pathlib import Path

import pytest

from trading_screener.universe.loader import load_universe, load_universe_metadata


def test_load_universe_from_path(tmp_path: Path) -> None:
    path = tmp_path / "watchlist.txt"
    path.write_text("SPY\nQQQ\nSPY\n# comment\n\nNVDA\n")

    assert load_universe(str(path)) == ["SPY", "QQQ", "NVDA"]


def test_load_universe_rejects_unknown_name() -> None:
    with pytest.raises(ValueError, match="Unknown universe"):
        load_universe("does_not_exist")


def test_load_universe_metadata_for_known_name() -> None:
    metadata = load_universe_metadata("liquid_large_caps")

    assert metadata["point_in_time"] is False
    assert metadata["survivorship_bias"] == "high"
