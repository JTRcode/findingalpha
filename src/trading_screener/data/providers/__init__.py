from trading_screener.data.providers.alpaca_provider import AlpacaMarketDataProvider
from trading_screener.data.providers.base import MarketDataProvider
from trading_screener.data.providers.massive_provider import MassiveMarketDataProvider
from trading_screener.data.providers.yfinance_provider import YFinanceProvider


def get_provider(name: str) -> MarketDataProvider:
    normalized = name.lower().strip()
    if normalized == "yfinance":
        return YFinanceProvider()
    if normalized == "alpaca":
        return AlpacaMarketDataProvider()
    if normalized in {"massive", "polygon", "polygonio"}:
        return MassiveMarketDataProvider()
    raise ValueError(f"Unsupported market data provider: {name}")


__all__ = [
    "AlpacaMarketDataProvider",
    "MarketDataProvider",
    "MassiveMarketDataProvider",
    "YFinanceProvider",
    "get_provider",
]
