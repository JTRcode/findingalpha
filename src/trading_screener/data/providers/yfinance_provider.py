from __future__ import annotations

from datetime import date

import pandas as pd

from trading_screener.data.providers.base import MarketDataProvider


class YFinanceProvider(MarketDataProvider):
    name = "yfinance"

    def fetch_daily_bars(
        self,
        tickers: list[str],
        start: date | str,
        end: date | str | None = None,
    ) -> pd.DataFrame:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError("Install yfinance to use YFinanceProvider") from exc

        raw = yf.download(
            tickers=tickers,
            start=str(start),
            end=None if end is None else str(end),
            auto_adjust=False,
            group_by="ticker",
            progress=False,
            threads=True,
        )
        if raw.empty:
            return pd.DataFrame(columns=_BAR_COLUMNS)

        frames: list[pd.DataFrame] = []
        if isinstance(raw.columns, pd.MultiIndex):
            for ticker in tickers:
                if ticker not in raw.columns.get_level_values(0):
                    continue
                frame = raw[ticker].copy()
                frame["ticker"] = ticker
                frames.append(frame)
        else:
            frame = raw.copy()
            frame["ticker"] = tickers[0]
            frames.append(frame)

        bars = pd.concat(frames).reset_index()
        bars = bars.rename(
            columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )
        bars["date"] = pd.to_datetime(bars["date"]).dt.date
        bars["provider"] = self.name
        return bars[_BAR_COLUMNS + ["provider"]].dropna(subset=["date", "ticker"])


_BAR_COLUMNS = ["ticker", "date", "open", "high", "low", "close", "adj_close", "volume"]

