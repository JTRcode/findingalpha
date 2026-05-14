# Research Log

Date format: YYYY-MM-DD

## 2026-05-14: Portfolio Presentation Cleanup
- Question: How should the project be presented for software engineering and investment-research-engineering portfolio review?
- Sources checked: `README.md`, `docs/DESIGN.md`, `docs/SETUP_B_V1_RESEARCH_REPORT.md`, `docs/SETUP_B_V2_PROPOSAL.md`, dashboard scope, and current generated artifact policy.
- Findings: The project is strongest when framed as a research-first signal-validation platform, not a trading bot. A public demo is useful, but exposing the local dashboard directly is not appropriate because local data, `.env`, and provider credentials must stay private. The safest near-term portfolio artifact is a polished README, case study, screenshots, and a short video. A hosted Streamlit demo should use only sanitized sample artifacts and should not make API calls or include secrets.
- Decision: Rewrite the README for employer-facing review, add `docs/PORTFOLIO_CASE_STUDY.md`, and add `docs/DEMO_PLAN.md`. Recommend screenshots/video first and a hosted read-only demo only after creating a small demo-safe dataset.
- Open questions: Whether to create a small committed demo dataset, where to host a read-only dashboard, and which screenshots best communicate the Setup B workflow.

## 2026-05-14: Setup B v1 Filter Diagnostics Review
- Question: Why do the broad Volume and Structure gates show high pass rates from the prior step but low pass rates of total?
- Sources checked: `data/backtests/setup_b_filter_diagnostics_20260514T071215Z.parquet`, `src/trading_screener/research/setup_eval.py`, `src/trading_screener/signals/daily_playbook.py`, `docs/SETUP_B_V1_RESEARCH_REPORT.md`.
- Findings: `pass_rate_from_prior_step` is stored as `pass_rate_of_available` in the diagnostic artifact. In the cumulative funnel, `available_count` means the number of ticker-days that survived all previous gates. `pass_rate_of_total` is cumulative against the full research dataset. Broad Trend reduces the sample to 42.08% of total ticker-days, Pullback to 24.05%, Volume to 21.59%, Structure to 21.47%, and Confirmation to 8.18%. Volume passes 89.75% of the already trend-plus-pullback-filtered set, and Structure passes 99.44% of the already filtered set.
- Decision: Keep Setup B v1 frozen. Treat broad Volume and Structure as audit/safety gates rather than primary selectivity drivers. For v2 research, prioritize Confirmation quality, Pullback quality, and diagnostic momentum-reset features before changing Volume or Structure thresholds.
- Open questions: Does stricter Volume improve forward returns enough to justify reducing candidate count? Is Structure redundant after Trend and Pullback, or does it still protect against visibly broken charts in edge cases? Does Confirmation quality explain more forward-return variation than the current composite score?

## 2026-05-14: Setup B v1 Condition-Level Filter Deep Dive
- Question: Which specific v1 conditions are doing the filtering inside each gate, and which conditions are redundant?
- Sources checked: `data/backtests/setup_b_filter_diagnostics_20260514T071215Z.parquet`, `data/features/scored_history.parquet`, `src/trading_screener/signals/daily_playbook.py`.
- Findings: The broad scanner is mostly filtered by 60D momentum, pullback depth from the 10D high, 1D return, and close position in the daily range. Broad Volume is represented as two condition rows, but both rows use the same OR expression and therefore are not two independent broad filters. Broad Structure is mostly redundant after Trend/Pullback/Volume; its price-hold and close-vs-50 checks remove little to nothing once earlier gates have passed, while the 20D momentum condition removes only a small tail. Strict Volume is materially more restrictive than broad Volume and may be worth testing as a possible v2 diagnostic, but only if forward-return evidence improves.
- Decision: Document Volume duplication and Structure redundancy in the v1 report. Keep v1 unchanged. Treat broad v1 as a candidate generator and strict v1 as a clean-playbook label.
- Open questions: Should the dashboard display broad Volume as a single combined condition? Does strict Volume improve 5D/10D/20D returns after de-clustering and benchmark-relative checks? Should a future v2 include a stronger Structure condition, or should Structure stay an audit-only safety gate?

## 2026-05-14: Setup B v1 Absolute vs Benchmark-Relative Returns
- Question: Does Setup B's apparent forward-return pattern survive comparison against SPY and QQQ?
- Sources checked: `data/backtests/setup_b_bucket_diagnostics_20260514T071218Z.parquet`, `data/backtests/setup_b_top_bottom_spreads_20260514T071218Z.parquet`, `data/backtests/setup_b_benchmark_relative_monthly_20260514T071235Z.parquet`, `data/backtests/setup_b_date_declustered_20260514T071239Z.parquet`.
- Findings: Absolute bucket returns rise with score bucket mostly at 20D and 60D. The top-minus-bottom mean spread is 0.3999% at 20D and 1.4924% at 60D, but win-rate spreads are negative, suggesting the effect is not a simple higher-hit-rate edge. Aggregate Setup B is mildly positive versus SPY at 5D/10D and more positive at 20D/60D, but negative versus QQQ across 5D/10D/20D/60D. The highest score bucket is positive versus SPY at 5D/10D/20D/60D and positive versus QQQ at 20D/60D only. Date-declustered results preserve the top-minus-bottom pattern at 20D/60D, but QQQ-relative win rates remain near 50%.
- Decision: Treat Setup B v1 as a possible longer-horizon swing research signal, not a short-horizon entry signal and not a validated strategy. Any v2 proposal must explain whether the top-bucket effect is true alpha or exposure to sector, beta, rebound, or momentum regimes.
- Open questions: Is the 20D/60D top-bucket effect concentrated in a small number of sectors or market regimes? Does the effect remain after sector/date de-clustering and SPY/QQQ-relative monthly checks? Are larger winners driving the mean while most candidates remain ordinary?

## 2026-05-14: Setup B v1 Slice and Interaction Review
- Question: Do Setup B slices or interaction slices show anything promising enough for v2 research?
- Sources checked: `data/backtests/setup_b_slices_20260514T071219Z.parquet`, `data/backtests/setup_b_interaction_slices_20260514T071221Z.parquet`, `data/backtests/setup_b_benchmark_relative_monthly_20260514T071235Z.parquet`, `data/backtests/setup_b_date_declustered_20260514T071239Z.parquet`.
- Findings: High ATR is the strongest single slice. It leads absolute returns at 5D/10D/20D/60D and remains positive versus SPY and QQQ, including date-declustered QQQ-relative results at 20D/60D. Strong trend quality is also positive at longer horizons, but weaker than high ATR. Deeper pullback slices look strong in absolute returns, but the current benchmark-relative monthly artifact does not cover pullback-depth slices, so confidence is lower. Volume dry-up and confirmation quality do not show clean monotonic improvement. Interaction slices are dominated by high ATR combinations, especially `moderate_confirmation + high_atr` and market-regime-plus-high-ATR combinations.
- Decision: Treat high ATR as the leading v2 research hypothesis, not an accepted rule. Do not promote volume dry-up or stronger confirmation based on current slice evidence.
- Open questions: Is the high ATR effect sector concentration, beta/rebound exposure, or true stock-selection alpha? Do pullback-depth slices survive SPY/QQQ-relative and date-declustered testing once added to benchmark-relative artifacts? How much of the high ATR mean comes from outliers?

## 2026-05-14: Setup B v1 Pre-v2 Evidence Hardening
- Question: After adding broader benchmark-relative, date-declustered, outlier, and yearly-consistency diagnostics, which v2 hypotheses remain credible?
- Sources checked: `data/backtests/setup_b_benchmark_relative_monthly_20260514T075532Z.parquet`, `data/backtests/setup_b_date_declustered_20260514T075544Z.parquet`, `data/backtests/setup_b_outlier_diagnostics_20260514T075548Z.parquet`, `data/backtests/setup_b_time_consistency_20260514T075555Z.parquet`.
- Findings: High ATR remains the strongest v2 hypothesis. At 20D it has 3.66% absolute mean, 2.05% QQQ-relative mean, and 2.13% date-declustered QQQ-relative mean. At 60D it has 11.67% absolute mean, 6.41% QQQ-relative mean, and 7.15% date-declustered QQQ-relative mean. High ATR has a 75% positive-year rate versus QQQ at 60D. `moderate_confirmation + high_atr` is stronger than `strong_confirmation + high_atr`, so stronger confirmation should not be promoted blindly. Outlier diagnostics show high ATR's 60D mean falls from 11.67% to 9.34% after 5-95% trimming, so large winners help but do not fully explain the result. `too_deep` pullbacks also survive new QQQ-relative checks and may be a separate rebound-style hypothesis.
- Decision: Keep Setup B v1 frozen. Use the new hardening artifacts as required inputs before writing `SETUP_B_V2_PROPOSAL.md`. The leading v2 path is high-ATR Setup B, with a separate decision needed on whether this is a continuation variant, rebound variant, or separate label.
- Open questions: Is high ATR still strong after sector-neutral testing? Is the `too_deep` pullback branch psychologically and operationally compatible with the core trend-continuation playbook? What transaction-cost/slippage penalty is realistic for high-ATR candidates?

## 2026-05-14: Setup B v2 Proposal
- Question: How should v2 exploration be framed before coding new Setup B rules?
- Sources checked: `docs/SETUP_B_V1_RESEARCH_REPORT.md`, `docs/SETUP_B_V2_TRANSITION_PLAN.md`, current indicator diagnostics, and current hardening findings.
- Findings: The user wants v2 research to explore RSI reset, MACD histogram improvement, ADX trend strength, ROC acceleration, slope confirmation, and high ATR as a context flag. These should be tested separately first, then in combinations, before becoming gates or score components. High ATR remains important but should not automatically become a mandatory Setup B filter.
- Decision: Add `docs/SETUP_B_V2_PROPOSAL.md`. The proposal recommends first building diagnostic comparisons and likely starting with a momentum-reset score while keeping high ATR as a separate context flag.
- Open questions: Whether v2 should become one enhanced score, a named momentum-reset variant, a high-ATR watch variant, or separate labels for continuation and high-volatility rebound.

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

## 2026-05-13: ADR Usage Audit
- Question: Are ADRs being used and updated as the project changes?
- Sources checked: `docs/DECISIONS.md`, `docs/decisions/`, `docs/DESIGN.md`, `docs/RESEARCH_LOG.md`, and recent screener/research changes.
- Findings: ADRs covered the original architecture and the intraday provider addition, but Setup B evolved into a major research-methodology decision without its own ADR. The detailed findings were documented in the research log and design doc, but the ADR index did not clearly record the accepted Setup B methodology.
- Decision: Add ADR 0008 for Setup B research methodology and update the decision index.
- Open questions: Whether a future ADR should decide if Setup A and Setup C stay in the main dashboard or move to a prototype/experimental area.

## 2026-05-13: Dashboard Setup B Focus
- Question: How should the dashboard be cleaned up so Setup B is not buried under prototypes and diagnostics?
- Sources checked: Streamlit dashboard code and current design document.
- Findings: The daily setup tab mixed active Setup B research, Setup A/C prototype rows, candidate chart review, and many expanded diagnostic tables. This made the dashboard harder to scan and made A/C look as mature as Setup B.
- Decision: Rename the daily setup tab to Setup B Research, show Setup B candidates by default, move Setup A/C behind a prototype toggle, remove A/C score columns from the main daily setup table, and collapse heavier diagnostics by default.
- Open questions: Whether generic `composite_score` should be hidden or renamed on Setup B-specific views.

## 2026-05-13: Setup B Rule Audit View
- Question: How can Setup B rules be audited before changing thresholds?
- Sources checked: Setup B signal code, feature definitions, and dashboard candidate chart flow.
- Findings: The dashboard showed gate pass/fail status but did not show the raw feature values against the broad and strict thresholds. This made it hard to debug whether the setup rules were admitting the wrong charts or rejecting the right ones.
- Decision: Add signal-layer Setup B audit helpers that produce gate summaries and condition-level threshold tables, then display them in the Setup B candidate chart workflow.
- Open questions: Which specific conditions should be revised after chart-by-chart review, and whether any revised definition should become `setup_b_v2`.

## 2026-05-13: Setup B Filter Diagnostics
- Question: How many rows does each Setup B condition filter out?
- Sources checked: Setup B signal conditions, CLI research artifact generation, and dashboard diagnostics.
- Findings: Gate pass/fail on one chart is useful, but it does not show which conditions are generally restrictive across the universe. Because conditions overlap, both independent counts and cumulative funnel counts are needed.
- Decision: Add `setup_b_filter_diagnostics` artifacts. The independent view counts how many rows pass each condition by itself. The funnel view applies gate groups in order and reports how many rows are removed at each stage.
- Open questions: Which conditions should be revised after reviewing filter rates and chart quality together.

## 2026-05-13: Setup B Indicator Diagnostics
- Question: Should richer indicators be added to Setup B?
- Sources checked: Setup B feature generation, dashboard candidate review flow, and research diagnostics.
- Findings: SMA and simple momentum are interpretable but may be too blunt to audit trend acceleration, pullback reset, and momentum improvement. RSI, MACD, ADX, ROC acceleration, moving-average slope, and linear-regression slope can provide richer context, but adding them directly to the gate or score would change `setup_b_v1_broad_scanner`.
- Decision: Add these indicators as feature columns and diagnostics only. They are visible in the dashboard and tested through `setup_b_indicator_diagnostics`, but they do not affect Setup B candidate eligibility or score.
- Open questions: Whether any indicator slice improves forward returns enough to justify a future `setup_b_v2`.

## 2026-05-14: Setup B v1 Freeze and v2 Transition Plan
- Question: What must happen before collecting evidence for Setup B v2?
- Sources checked: Setup B methodology ADR, design document, alpha research notes, and current diagnostics.
- Findings: Setup B v1 needed a single baseline report and an explicit v2 transition checklist. Without that, it would be too easy to keep changing conditions in place and lose comparability.
- Decision: Freeze `setup_b_v1_broad_scanner`, add `docs/SETUP_B_V1_RESEARCH_REPORT.md`, and add `docs/SETUP_B_V2_TRANSITION_PLAN.md`. V2 work must start with evidence collection and a proposal, not direct rule edits.
- Open questions: Whether the first v2 candidate should be an enhanced score or a stricter named variant.
