from __future__ import annotations

import json
import os
import time
from datetime import date
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse
from urllib.request import Request, urlopen

import pandas as pd

from trading_screener.data.providers.base import MarketDataProvider


class MassiveMarketDataProvider(MarketDataProvider):
    name = "massive"
    base_url = "https://api.polygon.io"

    def __init__(self, api_key: str | None = None, rate_limit_sleep_seconds: float | None = None) -> None:
        self.api_key = (api_key or os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY") or "").strip()
        self.rate_limit_sleep_seconds = rate_limit_sleep_seconds or float(
            os.getenv("MASSIVE_RATE_LIMIT_SLEEP_SECONDS", "13")
        )
        self._last_request_at: float | None = None
        if not self.api_key:
            raise RuntimeError("Set MASSIVE_API_KEY or POLYGON_API_KEY to use Massive/Polygon market data")

    def fetch_daily_bars(
        self,
        tickers: list[str],
        start: date | str,
        end: date | str | None = None,
    ) -> pd.DataFrame:
        end_value = str(end or date.today())
        frames = [
            self._fetch_aggregates(ticker=ticker, multiplier=1, timespan="day", start=str(start), end=end_value)
            for ticker in tickers
        ]
        bars = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        if bars.empty:
            return bars
        bars["date"] = pd.to_datetime(bars["timestamp"], utc=True).dt.date
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
        multiplier, timespan = _parse_timeframe(timeframe)
        end_value = end or str(date.today())
        frames = [
            self._fetch_aggregates(ticker=ticker, multiplier=multiplier, timespan=timespan, start=start, end=end_value)
            for ticker in tickers
        ]
        bars = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        if not bars.empty:
            bars["timeframe"] = timeframe
            bars["feed"] = feed or "consolidated"
        return bars

    def _fetch_aggregates(
        self,
        ticker: str,
        multiplier: int,
        timespan: str,
        start: str,
        end: str,
    ) -> pd.DataFrame:
        rows: list[dict[str, object]] = []
        url = (
            f"{self.base_url}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start}/{end}?"
            + urlencode({"adjusted": "true", "sort": "asc", "limit": "50000", "apiKey": self.api_key})
        )
        while url:
            payload = self._get_json(url)
            for bar in payload.get("results", []) or []:
                rows.append(
                    {
                        "ticker": ticker,
                        "timestamp": pd.to_datetime(bar.get("t"), unit="ms", utc=True),
                        "open": bar.get("o"),
                        "high": bar.get("h"),
                        "low": bar.get("l"),
                        "close": bar.get("c"),
                        "volume": bar.get("v"),
                        "trade_count": bar.get("n"),
                        "vwap": bar.get("vw"),
                        "provider": self.name,
                    }
                )
            next_url = payload.get("next_url")
            url = self._with_api_key(next_url) if isinstance(next_url, str) else None

        return pd.DataFrame(rows)

    def _get_json(self, url: str) -> dict[str, object]:
        request = Request(url, headers={"Accept": "application/json"})
        for attempt in range(2):
            self._pace_requests()
            try:
                with urlopen(request, timeout=60) as response:
                    self._last_request_at = time.monotonic()
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                self._last_request_at = time.monotonic()
                body = exc.read().decode("utf-8", errors="replace")
                if exc.code == 429 and attempt == 0:
                    time.sleep(max(65, self.rate_limit_sleep_seconds))
                    continue
                if exc.code in {401, 403}:
                    raise RuntimeError(
                        "Massive/Polygon market data authorization failed. Check MASSIVE_API_KEY or POLYGON_API_KEY "
                        "and confirm your plan supports the requested historical range/timeframe."
                    ) from exc
                if exc.code == 429:
                    raise RuntimeError(
                        "Massive/Polygon rate limit hit. The free tier is 5 REST requests/minute; reduce tickers, "
                        "use --intraday-only, wait a minute, or set MASSIVE_RATE_LIMIT_SLEEP_SECONDS higher."
                    ) from exc
                raise RuntimeError(f"Massive/Polygon market data request failed with HTTP {exc.code}: {body}") from exc
        raise RuntimeError("Massive/Polygon request failed unexpectedly")

    def _pace_requests(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        wait_seconds = self.rate_limit_sleep_seconds - elapsed
        if wait_seconds > 0:
            time.sleep(wait_seconds)

    def _with_api_key(self, url: str) -> str:
        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query))
        query.setdefault("apiKey", self.api_key)
        return urlunparse(parsed._replace(query=urlencode(query)))


def _parse_timeframe(timeframe: str) -> tuple[int, str]:
    normalized = timeframe.strip().lower()
    if normalized.endswith("min"):
        value = normalized.removesuffix("min") or "1"
        return int(value), "minute"
    if normalized.endswith("day"):
        value = normalized.removesuffix("day") or "1"
        return int(value), "day"
    raise ValueError(f"Unsupported Massive/Polygon timeframe: {timeframe}")
