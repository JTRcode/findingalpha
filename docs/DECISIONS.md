# Decision Index

| ADR | Title | Status | Summary | Link |
|---:|---|---|---|---|
| 0001 | Market Data Provider | Accepted | Use yfinance first behind a provider interface; upgrade to Polygon/Tiingo/FMP when needed. | [0001-market-data-provider.md](decisions/0001-market-data-provider.md) |
| 0002 | Storage Layer | Accepted | Use Parquet files with DuckDB querying for MVP; migrate later if data scale requires. | [0002-storage-layer.md](decisions/0002-storage-layer.md) |
| 0003 | Dashboard Framework | Accepted | Use Streamlit for local MVP dashboard. | [0003-dashboard-framework.md](decisions/0003-dashboard-framework.md) |
| 0004 | Backtesting Engine | Accepted | Use pandas/vectorized forward-return analysis first; consider vectorbt/event-driven later. | [0004-backtesting-engine.md](decisions/0004-backtesting-engine.md) |
| 0005 | Broker Path Later | Accepted | Keep IBKR Canada in mind for future phases; no execution now. | [0005-broker-path-later.md](decisions/0005-broker-path-later.md) |
| 0006 | Alpha Research Methodology | Accepted | Use score buckets, forward returns, benchmark comparison, and simple basket tests. | [0006-alpha-research-methodology.md](decisions/0006-alpha-research-methodology.md) |
| 0007 | Intraday Market Data Provider | Accepted | Add Alpaca and Massive/Polygon market data for 1-minute stock/ETF bars; data only, no execution. | [0007-intraday-market-data-provider.md](decisions/0007-intraday-market-data-provider.md) |
| 0008 | Setup B Research Methodology | Accepted | Freeze `setup_b_v1_broad_scanner`; use broad candidates, strict audit gates, quality buckets, slices, variants, and benchmark-relative tests. | [0008-setup-b-research-methodology.md](decisions/0008-setup-b-research-methodology.md) |
