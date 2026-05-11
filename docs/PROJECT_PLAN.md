# Project Plan

Date: 2026-05-10

## Phase 0: Research and Decisions
Definition of done:
- Required docs created.
- ADRs created and indexed.
- MVP architecture chosen.
- Risks and exclusions documented.

## Phase 1: Daily Screener and Alpha MVP
Definition of done:
- Installable Python package.
- Provider interface with one daily-bar provider.
- Fetch historical daily data for a small universe.
- Store raw/processed data locally.
- Calculate basic interpretable features.
- Rank tickers and export timestamped CSV.
- Detect daily playbook setup candidates for Setup A, B, and C.
- Save timestamped signal snapshots.
- Evaluate forward returns by score bucket.
- Launch a simple Streamlit dashboard.
- Add tests for features, scoring, snapshots, and forward returns.
- No live trading code or secrets.

Status: Implemented as MVP code in `src/trading_screener/` with tests in `tests/`. The implementation saves raw bars, processed bars, scored feature history, timestamped signal snapshots, forward-return bucket summaries, top/bottom spreads, benchmark comparisons, simple top-ranked basket results, and transaction-cost sensitivity outputs. Runtime verification in this environment was limited because `pip`, `pytest`, and runtime dependencies such as pandas/yfinance are unavailable, but syntax compilation passed with `python3 -m compileall src tests`.

## Phase 1A: Intraday Setup Research Layer
Definition of done:
- Alpaca market-data provider added for historical stock/ETF bars.
- 1-minute OHLCV ingestion stores provider, timeframe, and feed.
- Intraday features include session VWAP, 20 EMA, relative minute volume, volume spikes, volume dry-up, VWAP reclaim, and VWAP loss.
- Setup candidate scores are saved for Setup B trend pullback continuation, Setup A exhaustion pullback, and Setup C failed bounce reversal.
- Intraday forward returns are calculated for short horizons.
- Dashboard shows latest intraday setup candidates.
- No Alpaca trading API, broker execution, options trading, crypto trading, or order placement.
- Named universe files exist so runs do not require manually typed ticker lists.

Status: Implemented as research-only data and signal code.

## Phase 2: Data Quality and Research Depth
- Add provider comparison checks.
- Add benchmarks and sector/industry data.
- Add point-in-time fundamentals if provider supports them.
- Add earnings/event flags with conservative timestamps.
- Track alpha decay and turnover.
- Add transaction-cost sensitivity.

## Phase 3: Paper Trading Readiness Gate
Do not start until:
- Signals show out-of-sample evidence.
- Transaction costs and slippage assumptions are documented.
- Paper trading objectives and risk controls are written.
- Broker API constraints for a Canadian user are verified.

## Phase 4: Supervised Trading Readiness Gate
Do not start until:
- Paper trading results are reviewed.
- CIRO/broker/tax/compliance questions are researched.
- Hard risk controls, audit logs, and manual approval flow exist.
- Execution code has extensive tests and dry-run behavior.

## Explicit Exclusions
- Live order submission.
- Automated trading.
- High-frequency tick prediction.
- Options trading.
- Crypto trading unless separately planned.
- Social media sentiment scraping.
- Complex ML before baseline backtests.
- Reinforcement learning.
- LLM-only trading decisions.
