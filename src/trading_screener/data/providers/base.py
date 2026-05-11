from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

import pandas as pd


class MarketDataProvider(ABC):
    name: str

    @abstractmethod
    def fetch_daily_bars(
        self,
        tickers: list[str],
        start: date | str,
        end: date | str | None = None,
    ) -> pd.DataFrame:
        """Return daily bars with ticker, date, open, high, low, close, adj_close, volume."""

    def fetch_intraday_bars(
        self,
        tickers: list[str],
        start: str,
        end: str | None = None,
        timeframe: str = "1Min",
        feed: str | None = None,
    ) -> pd.DataFrame:
        raise NotImplementedError(f"{self.name} does not support intraday bars")
