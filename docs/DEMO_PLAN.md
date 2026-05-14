# Demo Plan

Date: 2026-05-14
Status: Recommended portfolio approach

## Should This Project Have A Demo?
Yes, but it should be a controlled research demo, not access to the private working dashboard.

A demo is useful for employers because it shows:

- the dashboard actually runs
- the workflow is understandable
- research artifacts are inspectable
- the project is more than static code

However, exposing the live local dashboard is not recommended.

## Recommended Demo Options

### Option A: Screenshots And Short Video
Recommended first.

Create:

- one screenshot of the Setup B Research tab
- one screenshot of the candidate candlestick chart
- one screenshot of filter diagnostics
- one screenshot of benchmark-relative diagnostics
- one 60-90 second screen recording

Pros:

- safest
- fastest
- no hosting
- no secrets risk
- easy to embed on a portfolio site

Cons:

- not interactive

### Option B: Hosted Read-Only Streamlit Demo
Recommended later after sample data is prepared.

Requirements:

- use small sanitized sample artifacts
- commit only demo-safe data
- no `.env`
- no API calls in the hosted app
- no provider credentials
- no full local `data/` directory
- clear research-only disclaimer

Pros:

- interactive
- strong portfolio signal

Cons:

- needs demo-data curation
- hosting can break
- Streamlit public apps may sleep or expose app internals

### Option C: Local Reviewer Demo
Good for interviews.

Provide commands:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
findingalpha --provider yfinance --universe liquid_large_caps --start 2024-01-01
streamlit run src/trading_screener/dashboard/app.py
```

Pros:

- reviewer can run the real workflow
- no hosted infrastructure

Cons:

- depends on network and yfinance availability
- slower for recruiters

## Do Not Demo
Do not expose:

- local `.env`
- API keys
- broker credentials
- full `data/` directory
- live trading or order screens
- private notes that imply financial advice

Do not claim:

- proven alpha
- profitable strategy
- automated trading readiness

## Recommended Portfolio Page Section
Use this framing:

```text
Finding Alpha is a research-first equity screening platform that tests whether interpretable swing-trading setups have predictive value. The dashboard visualizes signal snapshots, Setup B pullback candidates, forward-return buckets, benchmark-relative diagnostics, and robustness checks.
```

Add links:

- GitHub repo
- case study
- screenshots or video
- optional hosted demo when sample data exists

## Demo Data Requirement
Before hosting a public dashboard, create a small demo dataset that includes:

- `data/features/scored_history.parquet`
- one `signal_snapshot_*.parquet`
- one `daily_setup_candidates_*.parquet`
- representative `setup_b_*` backtest artifacts

The sample should:

- use public tickers only
- contain no secrets
- be small enough for git or release assets
- clearly state that it is sample research data
- avoid claiming point-in-time institutional correctness

## Current Recommendation
For the portfolio update now:

1. Use screenshots and a short video first.
2. Link to the GitHub repo and portfolio case study.
3. Add a hosted read-only demo only after creating sanitized sample artifacts.
