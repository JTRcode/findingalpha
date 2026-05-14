# Finding Alpha

Personal stock screener and alpha research dashboard.

Phase 1 is research-only analytics: fetch historical daily data, calculate interpretable features, rank stocks, save timestamped signal snapshots, and evaluate whether scores predict forward returns. It does not place orders or implement live trading.

## MVP Stack Decision
- Language: Python
- Initial market data: `yfinance` for frictionless personal research, behind a provider interface
- Storage: partitioned Parquet files, queryable with DuckDB
- Features: daily adjusted OHLCV technical/liquidity features
- Alpha testing: forward-return bucket analysis plus simple top-ranked basket research
- Dashboard: Streamlit
- Broker path: Interactive Brokers Canada later, placeholders only

## Safety
This project is for personal research. It is not financial advice. No live trading, automated trading, order submission, broker credentials, or execution logic belongs in phase 1.

## Planned Workflow
1. Research and document assumptions.
2. Create ADRs for major decisions.
3. Implement the smallest useful MVP.
4. Add tests for calculations and alpha evaluation.
5. Save every screener run as a timestamped signal snapshot.
6. Update docs when implementation changes.

## Local Use
After installing dependencies in an environment with `pip`:

```bash
python3 -m pip install -e ".[dev]"
findingalpha --provider yfinance --tickers AAPL MSFT NVDA SPY QQQ --start 2024-01-01
streamlit run src/trading_screener/dashboard/app.py
python3 -m pytest
```

You can also use named universes instead of typing tickers manually:

```bash
findingalpha --provider yfinance --universe liquid_large_caps --start 2024-01-01
findingalpha --provider yfinance --universe sp500_current --start 2024-01-01
findingalpha --provider massive --universe core_etfs --intraday-only --intraday --intraday-start 2026-05-01 --intraday-timeframe 1Min
```

Universe files live in `config/universes/`. Add one ticker per line.

Refresh the current S&P 500 universe with:

```bash
findingalpha-update-sp500
```

For Alpaca historical intraday bars, put your credentials in `.env` or export them in your shell:

```bash
ALPACA_API_KEY_ID=your_key_id
ALPACA_API_SECRET_KEY=your_secret_key
ALPACA_DATA_FEED=iex
```

The provider also accepts Alpaca's common `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` names. Make sure the key ID and secret are not reversed and come from the same Alpaca account.

Use Alpaca's Paper Trading API key, not an OAuth app/client ID. A UUID-looking value is usually the wrong credential type for this market-data request.

For Massive/Polygon historical bars, add:

```bash
MASSIVE_API_KEY=your_api_key
```

`POLYGON_API_KEY` is also accepted.

Then run a small 1-minute research pull:

```bash
findingalpha --provider alpaca --tickers SPY QQQ GLD TLT NVDA AAPL --start 2025-01-01 --intraday --intraday-start 2026-05-01 --intraday-timeframe 1Min --feed iex
```

The Alpaca integration uses market-data endpoints only. It does not use Alpaca trading endpoints and cannot place orders.

To use Massive/Polygon 1-minute aggregate bars instead:

```bash
findingalpha --provider massive --tickers SPY QQQ GLD TLT NVDA AAPL --intraday-only --intraday --intraday-start 2026-05-01 --intraday-timeframe 1Min
```

The provider aliases `massive`, `polygon`, and `polygonio` all use the same market-data-only integration.

Massive/Polygon free REST access is rate-limited. The provider makes one aggregate-bars request per ticker for daily data and one per ticker for intraday data, then paces requests using `MASSIVE_RATE_LIMIT_SLEEP_SECONDS`, default `13`. Use `--intraday-only` when you only want 1-minute setup candidates, reduce the ticker list, or raise `MASSIVE_RATE_LIMIT_SLEEP_SECONDS` in `.env` if you still see 429s.

## Universe Guidance
Use different universe sizes for different jobs:

- Daily alpha tests: S&P 500-sized universes are reasonable and useful.
- Intraday REST pulls: start with 10-50 liquid ETFs/large caps because one-minute data is much heavier and provider rate limits matter.
- Full-market scans: later phase, likely using Massive/Polygon flat files or a database-backed workflow.

For now, the best default is `liquid_large_caps` for daily research and `core_etfs` for early intraday setup testing. Move toward the full S&P 500 once the setup definitions and provider choice are stable.

Outputs are written under `data/`:
- raw bars: `data/raw/`
- processed bars: `data/processed/`
- scored feature history: `data/features/`
- timestamped signal snapshots: `data/signals/`
- forward-return bucket summaries, top/bottom spreads, benchmark comparisons, top-ranked basket results, and transaction-cost sensitivity: `data/backtests/`
- intraday setup candidates: `data/signals/<provider>/intraday_setup_candidates_*.csv`

Daily raw/processed feature files currently act as latest-run working files. Timestamped signal and backtest outputs are preserved. Intraday raw bars, scored features, and candidates are provider-specific and timestamped so Alpaca and Massive/Polygon runs can be compared side by side.

## Dashboard Guide
The dashboard has four tabs:

- Overview: project flow from data provider to forward-return testing.
- Daily Screener: latest daily signal snapshot and an explanation of the composite score.
- Daily Setups: multi-day rule-based candidates for Setup A, B, and C.
- Alpha Tests: score buckets, benchmark comparison, and simple top-ranked basket results.
- Intraday Setups: latest Setup A/B/C candidates with setup score breakdowns and forward returns.

A signal snapshot is a timestamped record of what the screener saw at run time. A bucket is a score group: with five buckets, bucket 1 is the lowest-scored group and bucket 5 is the highest-scored group for that date.

The Daily Setups tab has a minimum setup score slider. Increase it to make candidates rarer and stricter; decrease it to inspect looser prototype matches.

The Daily Setups tab also includes a Setup B candlestick/volume chart. Select a candidate to inspect price action before and after the candidate date; the blue dashed line marks the signal date.

Setup B candidates are split into visible pass/fail gates: trend, pullback, volume dry-up, structure, and confirmation. Each gate also has a 0-1 quality score. Gates decide whether a row is eligible; quality scores rank the eligible candidates.

Setup B diagnostics are written to `data/backtests/setup_b_bucket_diagnostics_*.csv` and `data/backtests/setup_b_top_bottom_spreads_*.csv`. These include count, mean, median, win rate, standard error, t-stat, and top-bottom spread interpretation.

Setup B slice results are written to `data/backtests/setup_b_slices_*.csv`. Slices show whether the setup behaves differently by market regime, pullback depth/duration, volume dry-up, trend quality, confirmation quality, and ATR.

Market regime slices need benchmark context. Daily runs automatically fetch SPY/QQQ alongside the selected universe for regime analysis, but candidates remain restricted to the selected universe. If old slice files show only `benchmark_missing` or `unknown`, rerun the daily pipeline.

Setup B interaction slices are written to `data/backtests/setup_b_interaction_slices_*.csv`. Interaction slices test two conditions at once, such as market regime plus confirmation quality. The dashboard also lets you filter the Setup B candidate view by ATR slice, confirmation slice, and market regime.

## Implementation Status
The MVP code includes a provider interface, yfinance daily provider, Alpaca historical market-data provider, Massive/Polygon historical market-data provider, Parquet storage helpers, feature generation, composite scoring, timestamped signal snapshots, forward-return bucket evaluation, intraday setup candidates, benchmark comparison, top/bottom spread summaries, a simple basket research helper, transaction-cost sensitivity, CLI, Streamlit dashboard, and tests. This remains phase 1 research software only.

## Documentation
- [Research plan](docs/RESEARCH_PLAN.md)
- [API comparison](docs/API_COMPARISON.md)
- [Data requirements](docs/DATA_REQUIREMENTS.md)
- [Architecture options](docs/ARCHITECTURE_OPTIONS.md)
- [Project plan](docs/PROJECT_PLAN.md)
- [Alpha research](docs/ALPHA_RESEARCH.md)
- [Risk and compliance](docs/RISK_AND_COMPLIANCE.md)
- [Backtesting notes](docs/BACKTESTING_NOTES.md)
- [Survivorship bias](docs/SURVIVORSHIP_BIAS.md)
- [Universes](docs/UNIVERSES.md)
- [Decision index](docs/DECISIONS.md)
