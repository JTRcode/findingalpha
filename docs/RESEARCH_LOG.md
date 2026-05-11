# Research Log

Date format: YYYY-MM-DD

## 2026-05-10: Market Data Required for MVP
- Question: Which market data is necessary first?
- Sources checked: yfinance PyPI, Alpha Vantage docs, Polygon docs, Alpaca docs, SEC EDGAR docs.
- Findings: Daily adjusted OHLCV is enough for baseline signals and forward returns. Intraday, quotes, tick, fundamentals, earnings, news, and filings are useful later but increase cost and leakage risk.
- Decision: Start with adjusted daily OHLCV.
- Open questions: Best paid TSX provider for later.

## 2026-05-10: Data APIs
- Question: Which provider should be used first?
- Sources checked: yfinance, Stooq, Alpha Vantage, FMP, Tiingo, Polygon, Nasdaq Data Link, Alpaca, IBKR, Finnhub, Benzinga, SEC EDGAR.
- Findings: yfinance is fastest but unofficial. Polygon/Tiingo/FMP are stronger paid upgrade candidates. SEC EDGAR is official for U.S. filings but not prices.
- Decision: Use yfinance behind a provider interface for MVP; keep Polygon/Tiingo/FMP as upgrade paths.
- Open questions: Verify live pricing and terms before paid subscription.

## 2026-05-10: Canadian Broker Path
- Question: What broker/API path makes sense later?
- Sources checked: IBKR Canada, Questrade API, Alpaca docs, Wealthsimple API availability search.
- Findings: IBKR Canada offers global API trading, market data, paper/delayed data constraints, and broad asset access. Questrade exposes data/account APIs, but trade scope appears partner-limited for customers. Alpaca paper accounts are broadly available, but live brokerage is not the primary Canadian path. Wealthsimple has no public trading API suitable for this project.
- Decision: Keep IBKR Canada as likely future path; no execution code now.
- Open questions: Exact account permissions, subscriptions, and tax/compliance review before phase 3.

## 2026-05-10: Storage
- Question: What storage should the MVP use?
- Sources checked: DuckDB docs and common database tradeoffs.
- Findings: Parquet is simple and durable for local research. DuckDB queries Parquet directly and supports pandas/Arrow workflows. PostgreSQL/Timescale/ClickHouse are unnecessary initially.
- Decision: Use Parquet files plus DuckDB query capability.
- Open questions: Migration threshold for PostgreSQL/ClickHouse if intraday/tick data grows.

## 2026-05-10: Backtesting
- Question: Which backtesting method is best first?
- Sources checked: vectorbt docs, backtrader docs, common pandas practices.
- Findings: Forward-return bucket analysis is better than full strategy simulation for early alpha testing. Vectorbt/backtrader are useful later.
- Decision: Implement pandas-based forward returns and simple basket research.
- Open questions: Whether to adopt vectorbt after baseline tests.

## 2026-05-10: Dashboard
- Question: Which UI is best first?
- Sources checked: Streamlit docs and framework tradeoffs.
- Findings: Streamlit is the fastest local data app path. Dash/FastAPI+React are heavier.
- Decision: Use Streamlit for MVP.
- Open questions: Whether multi-user/web deployment is ever required.

## 2026-05-10: MVP Implementation
- Question: Did implementation follow the research plan?
- Sources checked: Local source tree and documented ADR decisions.
- Findings: Implemented the planned Python MVP with provider interface, yfinance provider, Parquet output helpers, technical features, composite scoring, timestamped signal snapshots, forward-return bucket evaluation, top/bottom spreads, benchmark comparison, simple basket helper, transaction-cost sensitivity, CLI, Streamlit dashboard, and tests.
- Decision: Keep the documented MVP stack unchanged.
- Open questions: Full pytest and API runtime verification require a Python environment with `pip` and dependencies installed.

## 2026-05-11: Intraday Alpaca Research Layer
- Question: How should the project support the user's swing/intraday playbook?
- Sources checked: Alpaca official Market Data API docs for historical stock bars and historical stock data feed options.
- Findings: Alpaca historical stock bars support `1Min` timeframes through the market-data API. The Basic plan supports IEX data and historical data, while broader SIP/full-market data and less restrictive recent access may require a paid plan. IEX-only volume may not match full consolidated market volume.
- Decision: Add Alpaca market data for historical stock/ETF bars only. Keep execution and trading APIs out of scope.
- Open questions: Whether IEX volume is good enough for volume-spike research or whether SIP data is worth paying for after initial testing.

## 2026-05-11: Massive/Polygon Intraday Provider
- Question: Should the project also test Massive/Polygon for intraday bars?
- Sources checked: Current Polygon/Massive stock pricing and docs pages.
- Findings: Polygon has rebranded to Massive while Polygon URLs and API patterns remain relevant. The current stock free tier advertises 2 years of historical data, 5 API calls/min, 100% market coverage, and minute aggregates. This may be a better free comparison point than Alpaca IEX for volume-spike research. The aggregate endpoint used for historical minute bars is one request per ticker/range/timeframe; grouped daily exists for all-stock daily bars, and flat files are the likely bulk path.
- Decision: Add Massive/Polygon as a market-data-only provider alias using `massive`, `polygon`, or `polygonio`.
- Open questions: How the free-tier rate limit behaves for multi-symbol historical pulls and whether a paid tier is needed once the watchlist expands.
