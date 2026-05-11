from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


WIKIPEDIA_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
UNIVERSE_DIR = Path("config/universes")
UNIVERSE_PATH = UNIVERSE_DIR / "sp500_current.txt"
METADATA_PATH = UNIVERSE_DIR / "metadata.json"


def fetch_sp500_symbols(url: str = WIKIPEDIA_SP500_URL) -> list[str]:
    request = Request(url, headers={"User-Agent": "FindingAlpha personal research"})
    with urlopen(request, timeout=30) as response:
        html = response.read()

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "constituents"})
    if table is None:
        raise RuntimeError("Could not find S&P 500 constituents table")

    symbols: list[str] = []
    for row in table.find_all("tr")[1:]:
        cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
        if not cells:
            continue
        symbols.append(to_yahoo_symbol(cells[0]))

    return sorted(dict.fromkeys(symbols))


def to_yahoo_symbol(symbol: str) -> str:
    return symbol.replace(".", "-")


def write_sp500_universe(symbols: list[str], path: Path = UNIVERSE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(symbols) + "\n")


def update_metadata(count: int, metadata_path: Path = METADATA_PATH) -> None:
    metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
    metadata["sp500_current"] = {
        "description": "Current S&P 500 constituent list fetched from Wikipedia.",
        "survivorship_bias": "high",
        "point_in_time": False,
        "source": WIKIPEDIA_SP500_URL,
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        "symbol_count": count,
        "notes": "Current-only S&P 500 list. Good for daily workflow development; not valid for clean historical index backtests.",
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update current S&P 500 universe from Wikipedia")
    parser.add_argument("--output", default=str(UNIVERSE_PATH), help="Output ticker file")
    args = parser.parse_args()

    symbols = fetch_sp500_symbols()
    output = Path(args.output)
    write_sp500_universe(symbols, output)
    if output == UNIVERSE_PATH:
        update_metadata(len(symbols))
    print(f"Wrote {len(symbols)} symbols to {output}")


if __name__ == "__main__":
    main()
