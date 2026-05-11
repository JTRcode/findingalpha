from __future__ import annotations

import pytest

from trading_screener.data.providers import (
    AlpacaMarketDataProvider,
    MassiveMarketDataProvider,
    YFinanceProvider,
    get_provider,
)


def test_get_provider_returns_yfinance_provider() -> None:
    assert isinstance(get_provider("yfinance"), YFinanceProvider)


def test_get_provider_rejects_unknown_provider() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        get_provider("unknown")


def test_get_provider_returns_alpaca_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALPACA_API_KEY_ID", "key")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "secret")

    assert isinstance(get_provider("alpaca"), AlpacaMarketDataProvider)


def test_get_provider_accepts_apca_env_names(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.delenv("ALPACA_API_SECRET_KEY", raising=False)
    monkeypatch.setenv("APCA_API_KEY_ID", "key")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "secret")

    assert isinstance(get_provider("alpaca"), AlpacaMarketDataProvider)


def test_get_provider_returns_massive_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MASSIVE_API_KEY", "key")

    assert isinstance(get_provider("massive"), MassiveMarketDataProvider)
    assert isinstance(get_provider("polygon"), MassiveMarketDataProvider)
