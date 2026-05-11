# Finding Alpha Agent Guide

## Mission
Build a personal stock screener and alpha research dashboard that can test whether interpretable signals predict future returns. The phase 1 system is research and analysis only. It must not submit orders, automate trading, or imply that a high score is a validated trading signal.

## Agent Responsibilities
- Follow the workflow: research -> document -> decide -> implement -> test -> update docs.
- Keep assumptions explicit in docs, code comments where useful, and run outputs.
- Prefer a practical MVP, but make data, storage, and validation choices deliberately.
- Preserve modular provider interfaces so market data vendors can be replaced later.
- Save timestamped signal snapshots on every screener run for later alpha validation.
- Update docs and ADRs whenever implementation choices differ from the plan.

## Research-First Workflow
Before adding main screener code, create or update:
- `docs/RESEARCH_PLAN.md`
- `docs/API_COMPARISON.md`
- `docs/DATA_REQUIREMENTS.md`
- `docs/ARCHITECTURE_OPTIONS.md`
- `docs/PROJECT_PLAN.md`
- `docs/ALPHA_RESEARCH.md`
- `docs/RISK_AND_COMPLIANCE.md`
- `docs/BACKTESTING_NOTES.md`
- `docs/RESEARCH_LOG.md`
- `docs/DECISIONS.md`
- ADR files under `docs/decisions/`

## Alpha-Research-First Mindset
A screen ranks interesting stocks. A signal is a measurable hypothesis. A strategy defines portfolio construction and rebalancing. An execution system sends orders. Phase 1 only builds screens, signal snapshots, and alpha evaluation. Do not treat a composite score as tradable until it has survived forward-return testing, robustness checks, and paper trading in a later phase.

## No Live Trading in Phase 1
- Do not implement live order submission.
- Do not implement automated execution.
- Do not place orders.
- Do not add broker credentials.
- Broker/execution modules, if added as placeholders, must raise `NotImplementedError` and include the exact phrase `future phase only`.

## Safety and Compliance Rules
- This project is for personal research only.
- Do not provide financial advice.
- Research Canadian/CIRO, broker, tax, and market-data licensing requirements before any automation.
- Later execution phases require risk controls: max position size, max daily loss, max open trades, duplicate-order prevention, kill switch, market-hours guard, rejected-order handling, broker disconnect handling, full decision logs, and audit trails.

## Decision Documentation
Use ADRs for major choices: data provider, storage, dashboard, backtesting engine, broker path, and alpha methodology. Keep `docs/DECISIONS.md` as the index.

### ADR Format
Each ADR must use:

```markdown
# ADR N: Title

Date:
Status: Proposed / Accepted / Superseded

## Context
What decision needs to be made and why.

## Options considered
List realistic options with pros/cons.

## Decision
State the chosen option.

## Rationale
Explain why this choice fits the current phase.

## Consequences
Explain tradeoffs, risks, and what may need to change later.

## Review triggers
List conditions that should cause this decision to be revisited.
```

## Adding Data Providers
- Implement providers behind a common interface.
- Keep vendor-specific symbol formats, rate-limit handling, authentication, and response parsing inside provider modules.
- Record provider name, data timestamp, retrieval timestamp, adjusted/unadjusted status, and known limitations.
- Do not hardcode API keys. Read credentials from environment variables only.
- Add provider tests with mocked responses when practical.

## Coding Standards
- Use Python with clear package boundaries.
- Prefer pandas for simple daily-bar feature engineering and forward-return analysis.
- Keep raw data separate from processed data.
- Keep features, signals, research evaluation, storage, and dashboard code separate.
- Prefer inspectable baseline logic over complex ML.
- Avoid LLM-based trading decisions.
- Avoid high-frequency/tick prediction work in phase 1.

## Testing Expectations
- Add tests for feature calculations, scoring, snapshot schema, storage paths, and forward-return evaluation.
- Include edge cases for missing values, short histories, zero volume, insufficient forward data, and adjusted-price handling.
- Tests must not require real API keys.

## Secrets and API Keys
- Never commit secrets.
- Keep `.env.example` limited to variable names and safe examples.
- Use environment variables for API keys and account identifiers.
- Do not log secrets.

## Signal Snapshot Requirement
Every screener run must save a timestamped snapshot with:
- screener run date/time
- data provider
- latest market data timestamp
- ticker
- price
- volume
- calculated features
- composite score
- signal explanation
- risk flags
- universe used
- code/config version if available

Snapshots are required so future alpha tests can evaluate what was knowable when the signal was generated.
