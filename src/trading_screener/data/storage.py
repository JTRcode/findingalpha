from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def utc_timestamp_slug(now: datetime | None = None) -> str:
    ts = now or datetime.now(timezone.utc)
    return ts.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_data_dirs(data_dir: Path) -> None:
    for child in ["raw", "processed", "features", "signals", "backtests", "events"]:
        (data_dir / child).mkdir(parents=True, exist_ok=True)


def write_parquet(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


def read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def write_timestamped_outputs(df: pd.DataFrame, directory: Path, stem: str) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    slug = utc_timestamp_slug()
    parquet_path = directory / f"{stem}_{slug}.parquet"
    csv_path = directory / f"{stem}_{slug}.csv"
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False)
    return parquet_path, csv_path
