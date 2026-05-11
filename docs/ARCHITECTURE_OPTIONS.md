# Architecture Options

Date: 2026-05-10

## Option A: Simple Daily Research MVP

```text
yfinance/Stooq -> provider interface -> raw/processed Parquet
                                  -> feature generation
                                  -> scoring + signal snapshots
                                  -> forward-return evaluation
                                  -> Streamlit dashboard + CSV outputs
```

Effort: low. Cost: free. Data quality: adequate for personal baseline research, not institutional. Best for quickly validating the workflow and snapshot discipline.

## Option B: Serious Paid Data MVP

```text
Polygon/Tiingo/FMP -> provider interface -> Parquet + DuckDB
                                      -> validation layer
                                      -> feature/scoring pipeline
                                      -> alpha research reports
                                      -> Streamlit or Dash dashboard
```

Effort: medium. Cost: paid monthly. Data quality: better. Best once the workflow proves useful and broader coverage, reliability, or fundamentals matter.

## Option C: Broker/Data Integrated Research

```text
IBKR market data -> provider interface -> local research store
                                      -> dashboard
                                      -> paper-trading placeholders only
```

Effort: high. Cost: broker account plus market data subscriptions. Complexity: high. Useful later for Canadian-accessible paper/supervised trading, but not appropriate for the first research MVP.

## Recommendation
Choose Option A with clean provider interfaces and storage boundaries. Use yfinance first, store Parquet snapshots, query with DuckDB when helpful, and implement Streamlit for a fast local dashboard.

## Rejected for Now
- Broker-integrated build: too much setup and execution risk before alpha validation.
- Tick/intraday-first system: expensive, complex, and unnecessary for daily baseline signals.
- Full web app with FastAPI/React: unnecessary before research workflow is proven.

