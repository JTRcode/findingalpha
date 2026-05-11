# ADR 0001: Market Data Provider

Date: 2026-05-10
Status: Accepted

## Context
The MVP needs historical daily market data for a small stock universe so it can calculate interpretable features, rank stocks, save signal snapshots, and evaluate forward returns. The provider must be easy to start with but replaceable.

## Options considered
- yfinance: Free, easy Python integration, supports adjusted daily OHLCV for many U.S. and some Canadian symbols. Unofficial, Yahoo terms/reliability concerns, not suitable for professional distribution.
- Stooq: Free CSV-style EOD data. Simple, but metadata, adjustments, and coverage need verification.
- Alpha Vantage: Broad endpoints and simple API. Free tier is too small for multi-ticker research; premium needed.
- FMP: Strong combined price/fundamentals product. Paid dependency and licensing need verification.
- Tiingo: Strong paid EOD/news/fundamentals candidate. Requires subscription for serious use.
- Polygon.io: Excellent U.S. equities bars/trades/quotes/reference data. Paid plans for broader history/realtime; no core TSX focus.
- IBKR: Useful broker/data path later, but too complex for phase 1 research.

## Decision
Use yfinance as the first MVP provider behind a provider interface. Treat Polygon.io, Tiingo, and FMP as the main paid upgrade candidates. Add SEC EDGAR later for official U.S. fundamentals/filings, not for price data.

## Rationale
yfinance gives the fastest path to a working personal research MVP without committing to a paid vendor before the workflow proves useful. The provider interface prevents vendor lock-in and keeps the project ready for a more reliable paid source.

## Consequences
MVP data may have reliability, licensing, and point-in-time limitations. Results from yfinance should be treated as preliminary research. Any professional, shared, or capital-risking workflow requires provider terms review and likely a paid provider.

## Review triggers
- Need reliable point-in-time data.
- Need TSX/Canadian coverage.
- Need intraday bars, quotes, or corporate-action auditability.
- yfinance breaks, rate-limits, or produces inconsistent data.
- Project moves toward paper trading.

