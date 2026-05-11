from __future__ import annotations

import json
import os
from datetime import date
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from trading_screener.data.providers.base import MarketDataProvider


class AlpacaMarketDataProvider(MarketDataProvider):
    name = "alpaca"
    base_url = "https://data.alpaca.markets/v2"

    def __init__(self, key_id: str | None = None, secret_key: str | None = None) -> None:
        self.key_id = (key_id or os.getenv("ALPACA_API_KEY_ID") or os.getenv("APCA_API_KEY_ID") or "").strip()
        self.secret_key = (
            secret_key or os.getenv("ALPACA_API_SECRET_KEY") or os.getenv("APCA_API_SECRET_KEY") or ""
        ).strip()
        if not self.key_id or not self.secret_key:
            raise RuntimeError(
                "Set ALPACA_API_KEY_ID/ALPACA_API_SECRET_KEY or APCA_API_KEY_ID/APCA_API_SECRET_KEY "
                "to use Alpaca market data"
            )

    def fetch_daily_bars(
        self,
        tickers: list[str],
        start: date | str,
        end: date | str | None = None,
    ) -> pd.DataFrame:
        bars = self._fetch_stock_bars(tickers=tickers, start=str(start), end=None if end is None else str(end), timeframe="1Day")
        if bars.empty:
            return bars
        bars["date"] = pd.to_datetime(bars["timestamp"]).dt.date
        bars["adj_close"] = bars["close"]
        return bars[["ticker", "date", "open", "high", "low", "close", "adj_close", "volume", "provider"]]

    def fetch_intraday_bars(
        self,
        tickers: list[str],
        start: str,
        end: str | None = None,
        timeframe: str = "1Min",
        feed: str | None = None,
    ) -> pd.DataFrame:
        return self._fetch_stock_bars(tickers=tickers, start=start, end=end, timeframe=timeframe, feed=feed)

    def _fetch_stock_bars(
        self,
        tickers: list[str],
        start: str,
        end: str | None,
        timeframe: str,
        feed: str | None = None,
    ) -> pd.DataFrame:
        rows: list[dict[str, object]] = []
        page_token: str | None = None
        while True:
            params = {
                "symbols": ",".join(tickers),
                "timeframe": timeframe,
                "start": start,
                "limit": "10000",
            }
            if end:
                params["end"] = end
            if feed:
                params["feed"] = feed
            if page_token:
                params["page_token"] = page_token

            payload = self._get_json(f"{self.base_url}/stocks/bars?{urlencode(params)}")
            bars_by_symbol = payload.get("bars", {})
            for ticker, bars in bars_by_symbol.items():
                for bar in bars:
                    rows.append(
                        {
                            "ticker": ticker,
                            "timestamp": pd.to_datetime(bar["t"], utc=True),
                            "open": bar.get("o"),
                            "high": bar.get("h"),
                            "low": bar.get("l"),
                            "close": bar.get("c"),
                            "volume": bar.get("v"),
                            "trade_count": bar.get("n"),
                            "vwap": bar.get("vw"),
                            "provider": self.name,
                            "timeframe": timeframe,
                            "feed": feed,
                        }
                    )

            page_token = payload.get("next_page_token")
            if not page_token:
                break

        return pd.DataFrame(rows)

    def _get_json(self, url: str) -> dict[str, object]:
        request = Request(
            url,
            headers={
                "APCA-API-KEY-ID": self.key_id or "",
                "APCA-API-SECRET-KEY": self.secret_key or "",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 401:
                raise RuntimeError(
                    "Alpaca market data returned 401 Unauthorized. Check that your API key ID and secret are "
                    "set in this shell, not reversed, and copied from the same Alpaca account. Supported env vars: "
                    "ALPACA_API_KEY_ID/ALPACA_API_SECRET_KEY or APCA_API_KEY_ID/APCA_API_SECRET_KEY."
                ) from exc
            raise RuntimeError(f"Alpaca market data request failed with HTTP {exc.code}: {body}") from exc
