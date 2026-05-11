from __future__ import annotations

from trading_screener.universe.update_sp500 import to_yahoo_symbol


def test_to_yahoo_symbol_converts_class_dot() -> None:
    assert to_yahoo_symbol("BRK.B") == "BRK-B"
    assert to_yahoo_symbol("AAPL") == "AAPL"
