from __future__ import annotations

import json
from pathlib import Path
from typing import Any


UNIVERSE_DIR = Path("config/universes")
UNIVERSE_METADATA_PATH = UNIVERSE_DIR / "metadata.json"


def load_universe(name_or_path: str) -> list[str]:
    path = Path(name_or_path)
    if not path.exists():
        path = UNIVERSE_DIR / f"{name_or_path}.txt"
    if not path.exists():
        available = sorted(file.stem for file in UNIVERSE_DIR.glob("*.txt"))
        raise ValueError(f"Unknown universe '{name_or_path}'. Available universes: {available}")

    tickers: list[str] = []
    for line in path.read_text().splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#"):
            continue
        tickers.append(clean)
    return dedupe_preserve_order(tickers)


def load_universe_metadata(name_or_path: str | None) -> dict[str, Any]:
    if name_or_path is None:
        return {
            "description": "Built-in default universe.",
            "survivorship_bias": "unknown",
            "point_in_time": False,
            "notes": "No explicit universe metadata was provided.",
        }
    metadata = _read_metadata()
    name = Path(name_or_path).stem
    return metadata.get(
        name,
        {
            "description": f"Universe loaded from {name_or_path}.",
            "survivorship_bias": "unknown",
            "point_in_time": False,
            "notes": "No metadata found. Document whether this universe is current-only or point-in-time.",
        },
    )


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output


def _read_metadata() -> dict[str, dict[str, Any]]:
    if not UNIVERSE_METADATA_PATH.exists():
        return {}
    return json.loads(UNIVERSE_METADATA_PATH.read_text())
