# Demo Plan

Date: 2026-05-14
Status: Initial read-only demo dataset implemented

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
Recommended after verifying screenshots and local demo mode.

Requirements:

- use small sanitized sample artifacts from `demo_data/`
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
The repo now includes a small demo dataset at `demo_data/`.

It includes:

- `demo_data/features/scored_history.parquet`
- one `demo_data/signals/signal_snapshot_*.parquet`
- one `demo_data/signals/daily_setup_candidates_*.parquet`
- representative `setup_b_*` backtest artifacts

The sample should:

- use public tickers only
- contain no secrets
- be small enough for git or release assets
- clearly state that it is sample research data
- avoid claiming point-in-time institutional correctness

Regenerate it from local research artifacts with:

```bash
python3 scripts/build_demo_dataset.py
```

Run the dashboard against it with:

```bash
FINDINGALPHA_DATA_DIR=demo_data streamlit run src/trading_screener/dashboard/app.py
```

The dashboard also falls back to `demo_data/` automatically when `data/` has no local artifacts. For hosted demos, setting `FINDINGALPHA_DATA_DIR=demo_data` is still clearer.

## Current Recommendation
For the portfolio update now:

1. Verify the local read-only demo with `FINDINGALPHA_DATA_DIR=demo_data`.
2. Capture screenshots and a short video.
3. Link to the GitHub repo and portfolio case study.
4. Host the read-only Streamlit demo only after confirming the demo dataset renders well.
