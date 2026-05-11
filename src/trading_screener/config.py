from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(dotenv_path=Path.cwd() / ".env")


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path("data")
    provider: str = os.getenv("FINDINGALPHA_PROVIDER", "yfinance")
    alpaca_data_feed: str = os.getenv("ALPACA_DATA_FEED", "iex")
    universe: tuple[str, ...] = ("AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "SPY", "QQQ")
    benchmark_tickers: tuple[str, ...] = ("SPY", "QQQ")
    config_version: str = "mvp-0.1"


def default_settings() -> Settings:
    return Settings()
