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

## 2026-05-11: Setup B Slice Findings and Variant Plan
- Question: Does the stricter Setup B scanner show useful alpha in buckets, slices, or interaction slices?
- Sources checked: Local generated backtest artifacts under `data/backtests/`, including Setup B bucket diagnostics, single-factor slices, and interaction slices.
- Findings: Broad Setup B score buckets were mixed and not strong enough to trust alone. The most interesting evidence appeared in subsets: high ATR candidates, strong confirmation quality, strong volume dry-up, and combinations such as positive SPY regime plus high ATR or strong dry-up plus strong confirmation. These are promising research leads, not tradeable proof. Sample-size risk remains high for narrow interactions, and benchmark-relative returns need to be tracked explicitly.
- Decision: Add Setup B variant diagnostics on top of the existing gates and scores. Variants classify candidates into `conservative_continuation`, `momentum_rebound`, `high_atr_watch`, and `other_setup_b`; also report forward returns relative to SPY when benchmark data is present.
- Open questions: Whether the variants remain useful over longer history, across sectors, after benchmark adjustment, after transaction costs, and with point-in-time universe data.

## 2026-05-11: Setup B Market Regime Diagnostics
- Question: Why did weak/choppy market-regime slices sometimes look better than positive regimes?
- Sources checked: Local `scored_history.parquet` and generated Setup B slice data.
- Findings: The surprising result was mainly in absolute returns at 10D/20D. In the current data, `spy_weak_or_chop` had better absolute 10D/20D averages, but worse SPY-relative returns at every tested horizon. Weak/chop candidates are also clustered in specific months, so rebound months can distort aggregate absolute returns.
- Decision: Add dedicated Setup B market-regime diagnostics with both absolute and SPY-relative forward returns, plus monthly regime breakdowns.
- Open questions: Whether market regime should use more nuanced definitions such as benchmark slope, volatility regime, breadth, rate-sensitive ETF behavior, or sector-specific regime instead of only SPY price-vs-SMA50 and 20D momentum.

## 2026-05-11: Memory Review
- Question: Why does running the S&P 500 research workflow use enough memory to affect other applications?
- Sources checked: Local file sizes, `scored_history.parquet` shape and dtypes, CLI research flow, forward-return helper, Setup B diagnostics, yfinance provider, and dashboard loading path.
- Findings: No long-lived leak was identified. The main problem was repeated full-DataFrame materialization: `scored_history.parquet` expands to roughly 375 MB in memory, and several diagnostics re-added forward returns or copied the full frame. The dashboard also rebuilt Setup B slice context from the full scored history during reruns. yfinance fetched large universes in one wide request, increasing peak memory during S&P 500 pulls.
- Decision: Reuse existing forward-return columns, compute CLI forward returns in place after writing the base scored file, shrink Setup B diagnostic frames to candidate rows and required columns, cache dashboard parquet reads, reduce dashboard Setup B context to candidate rows, and batch yfinance requests.
- Open questions: Whether to add a CLI `--skip-heavy-diagnostics` flag or migrate large historical studies to DuckDB/Parquet queries if intraday or longer daily history increases memory pressure again.

## 2026-05-11: Setup B Two-Level Scanner
- Question: Should Setup B become broader so research has enough candidates, with strictness moved into ranking and diagnostics?
- Sources checked: Current Setup B candidate counts and dashboard filtering behavior.
- Findings: The all-gates Setup B definition produced too few high-threshold candidates after slice filters, increasing overfit risk. A broad scanner with strict gate labels preserves more research samples while still showing whether each chart satisfies the original high-quality playbook definition.
- Decision: Add `setup_b_scanner_gate` for broad eligibility, keep `setup_b_strict_gate` and individual strict gates for auditability, and lower the default candidate threshold from `0.75` to `0.60`.
- Open questions: Whether the broad gate is now too permissive and should be tuned using bucket behavior, chart review, and out-of-sample signal snapshots.

## 2026-05-11: Setup B Broad Scanner Slice Review
- Question: After broadening Setup B, do the previously interesting slice trends still exist?
- Sources checked: Fresh in-memory run from `data/processed/daily_bars.parquet` using the two-level Setup B scanner, current feature generation, forward returns, and slice helpers.
- Findings: The broad scanner produced 51,772 Setup B research candidates across 505 tickers from 2021-03-31 to 2026-05-11, including 2,738 strict matches. Score buckets still showed a useful ranking gradient: top bucket beat bottom bucket by roughly 0.25 percentage points at 5D, 0.42 percentage points at 10D, and 0.77 percentage points at 20D in absolute mean return; SPY-relative mean also improved from bottom to top. High ATR remained the clearest surviving slice, with positive SPY-relative mean at 5D/10D/20D and healthier sample sizes than before. Trend strength also helped, especially when combined with high ATR. Confirmation quality alone was weaker than expected; strong confirmation was not consistently better than moderate/weak confirmation after broadening. Volume dry-up alone was also weaker than expected; strong dry-up improved strict-match rate but did not improve raw forward returns by itself. Market regime alone remained modest; `spy_positive` was better than weak/chop in SPY-relative terms, but the strongest interaction was high ATR inside weak/chop regimes, likely reflecting rebound behavior and requiring caution.
- Decision: Keep the broad scanner. Treat high ATR, strong trend plus high ATR, and score-bucket rank as the most useful current research leads. Do not promote confirmation or volume dry-up as standalone filters yet; keep them as score components and chart-review context.
- Open questions: Whether high ATR is genuine Setup B alpha or mostly rebound/beta/crash-recovery exposure; whether results survive sector neutralization, date/month de-clustering, transaction costs, and out-of-sample signal snapshots.

## 2026-05-11: Setup B Declustering and Benchmark-Relative Tests
- Question: Do the high ATR and score-bucket trends survive date de-clustering and SPY/QQQ-relative monthly tests?
- Sources checked: Fresh diagnostics generated from `data/processed/daily_bars.parquet`, including `setup_b_benchmark_relative_monthly`, `setup_b_date_declustered`, and `setup_b_sector_declustered`.
- Findings: Date de-clustering preserved the score-bucket gradient. Against SPY, bucket 5 date-declustered relative mean was about +0.14% at 5D, +0.16% at 10D, and +0.35% at 20D, while bucket 1 was negative at each horizon. The pattern was similar against QQQ, though slightly weaker. High ATR remained the strongest slice after date de-clustering: against SPY it showed about +0.70% at 5D, +2.14% at 10D, and +4.59% at 20D; QQQ-relative results were similar. Month-by-month, high ATR had positive SPY-relative monthly mean in 36/63 months at 5D, 38/62 months at 10D, and 42/62 months at 20D. Top-minus-bottom score bucket spreads were positive in about 62%-65% of months for SPY and QQQ. Sector de-clustering could not be performed because the current dataset has no sector/industry metadata.
- Decision: Add benchmark-relative monthly diagnostics, date-declustered diagnostics, and an explicit sector-metadata-missing artifact. Continue treating high ATR as a research lead, not proof of alpha.
- Open questions: Whether high ATR is mainly rebound beta, whether a beta/volatility-adjusted benchmark should replace simple SPY/QQQ comparisons, and which sector metadata provider should be added for true sector-neutral tests.

## 2026-05-11: Earnings Overlay for Candidate Charts
- Question: Should daily candidate charts show earnings context?
- Sources checked: Local dashboard chart flow and data requirements.
- Findings: Earnings can explain gaps, ATR spikes, failed pullbacks, and continuation moves. It is useful chart context before adding earnings as a scored feature. Provider choice remains unresolved, so hard-wiring a vendor now would create unnecessary coupling.
- Decision: Add a provider-neutral local earnings overlay. The dashboard reads optional `data/events/earnings.csv` or `data/events/earnings.parquet` and marks earnings on candidate candle charts. After-close events are mapped to the next trading session; before-open and unknown events are mapped to the reported date.
- Open questions: Which point-in-time earnings calendar provider should be used later, and whether earnings proximity should become a risk flag, exclusion rule, or separate event-study feature.

## 2026-05-13: Screener Cleanup Review
- Question: Has the screener become redundant or unclear after adding Setup B diagnostics?
- Sources checked: Local screener, playbook, CLI, and setup evaluation code.
- Findings: The CLI calculated technical features and playbook scores, then rebuilt the ranked screen by recalculating the same features and scores from raw bars. Rows with no daily playbook score were also labelled as Setup B because the best-setup logic picked the first zero-valued score column. The generic composite score and Setup B score serve different purposes and should stay separate, but the Setup B rule set needs an explicit version so future changes do not silently redefine prior research outputs.
- Decision: Reuse the already-scored history when building the latest ranked screen, label zero-score rows as `none`, exclude `none` rows from daily setup evaluation, and stamp Setup B output with `setup_b_v1_broad_scanner`.
- Open questions: Whether the dashboard should eventually hide the generic composite score on the Setup B tab or rename it more clearly as a generic technical score.
