# API Comparison

Date: 2026-05-10

Pricing and limits change often. Verify before relying on any vendor for production or redistribution.

## Summary Recommendation
Use `yfinance` first for a no-cost daily MVP, but isolate it behind a provider interface because it is unofficial, subject to Yahoo terms, and not suitable as a durable professional data dependency. For intraday setup research, compare Alpaca IEX data against Massive/Polygon aggregate bars. Add SEC EDGAR later for official U.S. fundamentals/filings. Add a Canadian provider only after TSX coverage becomes a hard requirement.

## API Comparison Table

| Provider | U.S. stocks | Canada/TSX | Daily history | Adjusted data | Intraday/tick | Fundamentals/earnings/news | Limits/pricing notes | Python SDK | MVP fit | Later fit |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| yfinance | Yes | Often via Yahoo suffixes | Yes | Yes | Limited intraday | Some fundamentals/news | Free unofficial; personal/research terms concern | Yes | High | Low/medium |
| Stooq | Yes | Limited/uncertain | Yes | Usually EOD CSV | No serious intraday/tick | No | Free; coverage/licensing verification needed | Community/manual CSV | Medium | Low |
| Alpha Vantage | Global equities | Some global symbols | Yes | Yes on adjusted endpoint | Intraday; realtime/delayed entitlements | Fundamentals, economic data, indicators | Free tier is very small; premium needed for scale | Community/offical examples | Medium | Medium |
| Financial Modeling Prep | Broad global | Likely some Canada | Yes | Yes | Some intraday | Strong fundamentals, earnings, transcripts | Free/premium tiers; verify current quotas | Yes/community | Medium | Medium/high |
| Tiingo | U.S. equities strong | Some global/FX/crypto depending plan | Yes | Yes | IEX intraday on some plans | News, fundamentals depending product | Paid tiers; good reputation | Yes | Medium | High |
| Massive/Polygon.io | U.S. equities excellent | No core TSX | Yes | Corporate actions/reference | Minute, trades, quotes by plan | News, financials on higher plans | Current free stock tier advertises 2 years historical data, 5 calls/min, 100% market coverage, and minute aggregates; aggregate endpoint is per ticker, while grouped daily can fetch all-stock daily bars | Yes | High for intraday MVP | High |
| Nasdaq Data Link | Dataset marketplace | Dataset-dependent | Dataset-dependent | Dataset-dependent | Some realtime/delayed products | Strong macro/alt/premium datasets | Mostly a-la-carte premium; good for special datasets | Yes | Low | Medium/high |
| Alpaca market data | U.S. equities/options/crypto | No TSX | 7+ years | Corporate actions | Realtime/delayed bars/websocket | Limited fundamentals | Free and paid trading-data plans; live account availability varies by country | Yes | Medium | Medium |
| Interactive Brokers market data | Global | Yes through broker subscriptions | Yes | Depends endpoint/subscription | Realtime/delayed, historical | News/data subscriptions | Broker account and market-data subscriptions; complex | Yes | Low | High for broker phase |
| IEX Cloud | U.S. market data | Limited | Yes | Yes | IEX feed | Fundamentals/data sets | Status appears operational in 2026, but relevance/pricing needs verification | Yes/community | Low | Low/medium |
| Finnhub | U.S./global | Some global | Yes | Varies | Candles/websocket | Fundamentals, earnings, news | Free and paid tiers; verify limits | Yes | Medium | Medium |
| Benzinga | U.S./North America focus | Some Canadian news | Historical bars plus news | Varies | Real-time streams | Strong news, calendars, analyst data | Enterprise/licensed orientation | Clients/docs | Low | High for event/news alpha |
| SEC EDGAR | U.S. issuers only | Canadian issuers if SEC filers | No prices | N/A | N/A | Official filings/XBRL | Free; User-Agent and access rules required | Many wrappers | Low for prices | High for fundamentals |
| SEDAR+ | Canadian filings | Yes | No prices | N/A | N/A | Official Canadian filings | API availability for bulk research is limited/unclear; manual/paid vendors may be needed | Limited | Low | Medium for Canada filings |

## Data Type Needs

| Data type | Useful for | Needed now? | Difficulty/cost | Pitfalls | Alpha value |
|---|---|---:|---|---|---|
| Daily OHLCV | Basic trend, volume, volatility, liquidity | Yes | Low | Unadjusted split artifacts | Immediate baseline |
| Adjusted daily OHLCV | Return and indicator consistency | Yes | Low/medium | Vendor adjustment methodology differs | Immediate baseline |
| Intraday bars | Event timing, opening gaps, execution simulation | No | Medium | Timezones, survivorship, storage growth | Later |
| Tick data | Microstructure/HFT research | No | High | Huge cost/storage; easy leakage | Not phase 1 |
| Bid/ask quotes | Spread/slippage estimates | No | Medium/high | NBBO licensing, timestamps | Later cost modeling |
| Level 2/order book | Queue/microstructure | No | Very high | Exchange fees, complexity | Not phase 1 |
| Fundamentals | Value/quality filters | Later | Medium | Point-in-time availability | Strong later |
| Earnings calendar | Event risk flags | Later/optional | Low/medium | Announce-time leakage | Useful later |
| News/headlines | Event flags | Later | Medium/high | Timestamp leakage, licensing | Useful after baseline |
| Filings | Fundamental/event research | Later | Low for SEC, harder for Canada | Filing timestamp and parsing | Useful later |
| Macro data | Regime/context | Later | Low/medium | Release calendars/revisions | Later robustness |

## Strengths and Weaknesses
- `yfinance`: fastest path to personal daily adjusted bars; weakest legal/reliability footing.
- Stooq: simple free EOD alternative; weaker metadata and coverage clarity.
- Alpha Vantage: broad endpoints and simple HTTP; free limits too restrictive for multi-ticker research.
- FMP: strong all-in-one price/fundamental offering; paid dependency and licensing need review.
- Tiingo: good candidate for reliable EOD/news/fundamentals; paid plan likely needed.
- Massive/Polygon.io: strong U.S. market-data path for full-market aggregate bars/trades/quotes; no TSX focus.
- Nasdaq Data Link: useful marketplace, not a single simple equities API decision.
- Alpaca: useful U.S. market data and later paper concepts; live brokerage availability is not the Canadian default.
- IBKR: best later Canadian-accessible global broker/data path, but too complex for phase 1 data.
- Finnhub: convenient broad API, good for prototypes; verify data quality and limits.
- Benzinga: excellent event/news/calendar path, not a cheap first daily-bar source.
- SEC EDGAR: official U.S. filings and XBRL; not a price feed.
- SEDAR+: official Canadian filing venue; programmatic research workflow needs later verification.

## Sources Checked
- yfinance PyPI legal notes: https://pypi.org/project/yfinance/
- Alpha Vantage docs/pricing: https://www.alphavantage.co/documentation/ and https://www.alphavantage.co/premium/
- Massive/Polygon stocks/pricing/docs: https://polygon.io/stocks and https://polygon.io/docs/
- Nasdaq Data Link docs: https://docs.data.nasdaq.com/docs/getting-started
- Alpaca market data docs: https://docs.alpaca.markets/docs/about-market-data-api and https://docs.alpaca.markets/reference/stockbars
- IBKR Canada API/data: https://www.interactivebrokers.ca/en/trading/ib-api.php and https://www.interactivebrokers.ca/en/pricing/market-data-pricing.php
- Questrade API docs: https://www.questrade.com/api/documentation
- SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- Benzinga API docs: https://docs.benzinga.com/services/overview

## Unknowns for Later Verification
- Exact vendor redistribution and derived-data restrictions.
- Current paid pricing at subscription time.
- Reliable point-in-time fundamentals with delisted securities.
- Best Canadian/TSX historical adjusted daily provider.
- SEDAR+ programmatic access options.
