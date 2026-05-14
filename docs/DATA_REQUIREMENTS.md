# Data Requirements

Date: 2026-05-10

## Needed Now
For MVP daily screens:
- ticker
- trading date
- open, high, low, close
- adjusted close or adjusted OHLC where available
- volume
- data provider
- retrieval timestamp
- latest market data timestamp
- named universe used for the run

For the intraday research layer:
- ticker
- UTC timestamp
- open, high, low, close
- volume
- VWAP when provider supplies it
- trade count when provider supplies it
- provider
- timeframe
- feed, such as Alpaca `iex` or `sip`

## Needed Later
- corporate actions: splits and dividends
- delisted symbols and historical constituents
- fundamentals and point-in-time financial statements
- earnings calendar and actual announce timestamps
- sector/industry classification
- benchmark bars for SPY, QQQ, and later Canadian benchmarks
- intraday bars for event studies and execution modeling
- bid/ask quotes for realistic slippage estimates
- filings/news timestamps for event flags

## Frequency
- Daily screens: daily bars.
- Intraday setup research: 1-minute bars for a small liquid watchlist.
- Tick/order-book data is explicitly excluded from phase 1.

## Storage Format
- Raw provider pulls: `data/raw/<provider>/<dataset>/...`
- Processed bars: `data/processed/bars/...`
- Feature tables: `data/features/...`
- Signal snapshots: `data/signals/...`
- Research/backtest outputs: `data/backtests/...`
- Preferred file format: Parquet for tables, CSV export for human-readable ranked outputs.

## Data Quality Checks
- Required columns exist.
- Dates are parseable and timezone policy is explicit.
- OHLC values are non-negative.
- `high >= low`.
- Volume is non-negative.
- Duplicate ticker/date rows are rejected or deduplicated deterministically.
- Missing adjusted data is flagged.
- Split-sized jumps are investigated before research use.
- Latest bar timestamp is stored with every signal snapshot.
- Intraday rows must not duplicate ticker/timestamp pairs.
- Intraday feed must be recorded because IEX-only and SIP/full-market volume can differ.

## Timestamp and Timezone Rules
- Store run timestamps in UTC.
- Store market dates as exchange-local trading dates.
- For U.S. equities, assume America/New_York market calendar unless provider supplies a calendar.
- For Vancouver user-facing display, localize UI timestamps to America/Vancouver when useful.
- Never use news, earnings, filings, or fundamentals unless the availability timestamp is known or conservatively lagged.

## Earnings Event Overlay
The dashboard can overlay earnings events on daily candidate candle charts when a local file exists at:
- `data/events/earnings.csv`
- `data/events/earnings.parquet`

Supported columns:
- `ticker` or `symbol`
- `date`, `report_date`, or `earnings_date`
- `time`, `when`, or `session`
- optional: `eps_actual`, `eps_estimate`, `revenue_actual`, `revenue_estimate`

Timing rules:
- before-open or unknown events are marked on the reported date.
- after-close/post-market events are marked on the next available trading session.
- earnings data is chart context only right now; it is not yet used in alpha tests or scores.

Example CSV:

```csv
ticker,date,time,eps_actual,eps_estimate
NVDA,2026-02-25,after_close,1.24,1.18
AAPL,2026-01-29,after_close,2.05,2.01
```

## Signal Snapshot Schema
Every screener run must save one row per ticker with:
- `run_timestamp_utc`
- `provider`
- `market_data_timestamp`
- `ticker`
- `price`
- `volume`
- calculated feature columns
- `composite_score`
- `signal_explanation`
- `risk_flags`
- `universe`
- `config_version`
- `code_version`

## Universe Rules
- Do not type large ticker lists manually in commands; use files under `config/universes/`.
- Daily research can use larger universes such as S&P 500-sized lists.
- Intraday REST research should start smaller, around 10-50 highly liquid ETFs and large caps, because 1-minute bars are much heavier and providers have rate limits.
- Full-market intraday research should wait for a bulk/flat-file workflow and a storage plan.

## Alpha Validation Data
For each historical date/ticker:
- score and features known at that date
- future returns at 1, 5, 10, 20, and 60 trading-day horizons
- benchmark forward returns
- bucket labels such as quintile or decile
- transaction-cost scenario, when modeled
