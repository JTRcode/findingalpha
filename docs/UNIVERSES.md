# Universes

Date: 2026-05-11

## Purpose
Universes define which symbols are included in a research run. They make runs repeatable and avoid manually typing long ticker lists.

## Current Files
- `config/universes/core_etfs.txt`: small ETF list for quick intraday testing.
- `config/universes/liquid_large_caps.txt`: practical large-cap watchlist for daily and early intraday research.
- `config/universes/sp500_sample.txt`: starter sample, not a complete current S&P 500 list.
- `config/universes/sp500_current.txt`: current S&P 500 list generated from Wikipedia when updated.

## Recommended Sizes
- 10-50 tickers: best for early intraday REST pulls and setup debugging.
- 100-500 tickers: good for daily screens and cross-sectional alpha tests.
- 500+ tickers: useful later, but intraday data should use a bulk/flat-file workflow and stronger storage.

## S&P 500
The S&P 500 is a reasonable next daily universe. It is not too large for daily OHLCV research, but it can be slow or rate-limited for REST-based 1-minute intraday pulls.

For intraday setup research, start with liquid ETFs and large caps. Expand after:
- provider choice is stable
- setup definitions are readable
- storage paths are not overwritten
- rate limits/costs are understood
- forward-return tests are useful

## Updating Universes
Add one ticker per line:

```text
SPY
QQQ
NVDA
AAPL
```

Blank lines and `#` comments are ignored.

To refresh the current S&P 500 list:

```bash
findingalpha-update-sp500
```

This updates `config/universes/sp500_current.txt` and `config/universes/metadata.json`.

## Important Bias Note
Using today’s S&P 500 list for historical tests introduces survivorship bias. It is acceptable for early MVP research but should be replaced by point-in-time constituent data before making stronger claims.

Universe metadata is stored in `config/universes/metadata.json`. Any current-only universe should be marked with `"point_in_time": false` so the CLI and dashboard can warn about biased historical tests.

See `docs/SURVIVORSHIP_BIAS.md` for the upgrade path.
