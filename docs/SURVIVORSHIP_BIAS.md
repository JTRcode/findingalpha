# Survivorship Bias

Date: 2026-05-11

## What It Is
Survivorship bias happens when historical tests use only companies that still exist or are still in an index today. Failed, acquired, bankrupt, or removed companies disappear from the test, which can make signals look better than they really were.

Example: testing a 2020 strategy on today's S&P 500 excludes companies that were in the index in 2020 but later fell out, and includes companies that were not in the index yet.

## How To Prevent It
Use point-in-time universes. For each historical date, the backtest should only include tickers that were actually eligible on that date.

For S&P 500 research, this means the system needs:
- index constituent start date
- index constituent end date
- ticker/symbol history
- delisted symbols
- adjusted daily prices through delisting
- delisting returns where available

## Practical Stages

### Stage 1: MVP Daily Research
Use current or manually curated universes, but label results as survivorship-biased. This is acceptable for testing the app, feature calculations, dashboard, and rough signal behavior.

### Stage 2: Better Daily Research
Add a provider with historical S&P 500 constituents and delisted-security prices. EODHD is a practical retail-accessible candidate. Norgate is strong for survivorship-bias-free daily data but is Windows-oriented and does not provide intraday data. CRSP is the institutional/academic gold standard but may be hard to access personally.

### Stage 3: Cleaner Alpha Claims
Run tests using point-in-time membership and delisted returns. Report which universe methodology was used in every result.

## Provider Options
- EODHD: historical S&P 500 constituents and delisted tickers are available through paid APIs.
- Norgate Data: survivorship-bias-free daily data for U.S., Australian, and Canadian stocks; no intraday data.
- CRSP: survivor-bias-free U.S. stock data with active and inactive securities; institutional/academic access.
- Bloomberg/Capital IQ/LSEG: professional terminals can provide historical index constituents, but cost/access may be high.

## Current Repo Rule
Universe metadata lives in `config/universes/metadata.json`. If a universe is not point-in-time, the CLI warns that historical alpha tests may be survivorship-biased.

## Recommendation
Start daily research now with `liquid_large_caps` or a current S&P 500 list to validate workflow. Do not treat results as strong evidence until a point-in-time constituent source and delisted-price coverage are added.
