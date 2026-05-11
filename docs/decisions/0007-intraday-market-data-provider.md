# ADR 0007: Intraday Market Data Provider

Date: 2026-05-11
Status: Accepted

## Context
The daily-only MVP is not enough for the user's swing/intraday playbook. The next research layer needs 1-minute bars, volume spikes, VWAP/EMA reclaim and loss events, and setup-specific candidates for trend pullback continuation, exhaustion pullback, and failed bounce reversal.

## Options considered
- Alpaca Market Data: Historical stock bars support `1Min`; free Basic plan supports IEX and historical data with recent-data restrictions; paid Algo Trader Plus supports broader SIP access and higher limits. Good fit for a small research universe and the user's existing paper account.
- Massive/Polygon.io: Strong U.S. equities market data and broad historical coverage. Current stock free tier advertises 100% market coverage, minute aggregates, two years of history, and 5 API calls/minute.
- Interactive Brokers: Good future Canadian-accessible broker path, but historical API pacing and setup complexity make it a poor bulk research source for this phase.
- yfinance: Useful for quick daily experiments, but not reliable enough for historical 1-minute alpha research.

## Decision
Add Alpaca as the first intraday market-data provider for historical U.S. stock and ETF bars, and add Massive/Polygon as a second provider for consolidated aggregate bars. Use both providers only through market-data APIs. Do not add trading, broker execution, order submission, options trading, crypto trading, or live automation.

## Rationale
Alpaca provides the 1-minute OHLCV data needed to study volume spikes, VWAP reclaims/losses, and intraday confirmation behavior. Massive/Polygon is worth testing because its current stock free tier advertises 100% market coverage and minute aggregates, which may be more useful than IEX-only volume for the user's setup research.

## Consequences
The free Alpaca Basic plan uses IEX for unsubscribed equity data, which may not represent full-market volume. SIP/full-market data and unrestricted recent data may require a paid subscription. Massive/Polygon free access has rate limits and historical-range constraints. Its aggregate endpoint is one request per ticker/range/timeframe for this use case; grouped daily exists for all-stock daily bars, but not arbitrary historical 1-minute grouped watchlist bars through the endpoint used here. Research results must record the provider and feed/source because IEX-only volume spikes can differ from consolidated market volume.

## Review triggers
- IEX-only volume proves too noisy or incomplete.
- The universe expands beyond a small watchlist.
- Need full-market SIP volume, quotes, or more reliable historical breadth.
- Provider limits block repeatable research.
- Project moves toward paper trading or supervised execution.
