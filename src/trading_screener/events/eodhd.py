from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(dotenv_path=Path.cwd() / ".env")


EODHD_EARNINGS_URL = "https://eodhd.com/api/calendar/earnings"


def fetch_eodhd_earnings_sample(
    symbols: list[str] | None = None,
    start: str = "2024-01-01",
    end: str = "2026-12-31",
) -> pd.DataFrame:
    token = os.getenv("EODHD_API_TOKEN")
    if not token:
        raise RuntimeError("Missing EODHD_API_TOKEN. Add it to .env or export it in this shell.")

    request_symbols = symbols or ["AAPL.US", "MSFT.US", "NVDA.US"]
    payload = _get_json(
        EODHD_EARNINGS_URL,
        {
            "symbols": ",".join(request_symbols),
            "from": start,
            "to": end,
            "api_token": token,
            "fmt": "json",
        },
    )
    rows = payload.get("earnings") if isinstance(payload, dict) and "earnings" in payload else payload
    if not isinstance(rows, list):
        raise RuntimeError(f"EODHD returned an unexpected payload shape: {str(payload)[:300]}")
    return pd.DataFrame(rows)


def _get_json(url: str, params: dict[str, str]) -> object:
    request_url = f"{url}?{urlencode(params)}"
    request = Request(request_url, headers={"User-Agent": "findingalpha/0.1"})
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"EODHD request failed with HTTP {exc.code}: {_redact_token(body)}") from exc

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"EODHD returned non-JSON response: {_redact_token(body[:500])}") from exc

    if isinstance(payload, dict) and payload.get("errors"):
        raise RuntimeError(f"EODHD returned an error: {_redact_token(str(payload)[:500])}")
    if isinstance(payload, dict) and str(payload.get("message", "")).lower().startswith("you are not"):
        raise RuntimeError(f"EODHD returned an access error: {_redact_token(str(payload)[:500])}")
    return payload


def _redact_token(text: str) -> str:
    token = os.getenv("EODHD_API_TOKEN")
    return text.replace(token, "***") if token else text
