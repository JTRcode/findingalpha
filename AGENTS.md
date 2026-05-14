# Finding Alpha Agent Guide

## Mission
Build a personal stock screener and alpha research dashboard that can test whether interpretable signals predict future returns. The phase 1 system is research and analysis only. It must not submit orders, automate trading, or imply that a high score is a validated trading signal.

## Agent Responsibilities
- Follow the workflow: research -> document -> decide -> implement -> test -> update docs.
- Read `docs/DESIGN.md` before making architecture, screener, signal, dashboard, or research-methodology changes.
- Keep assumptions explicit in docs, code comments where useful, and run outputs.
- Prefer a practical MVP, but make data, storage, and validation choices deliberately.
- Preserve modular provider interfaces so market data vendors can be replaced later.
- Save timestamped signal snapshots on every screener run for later alpha validation.
- Keep `docs/DESIGN.md` current when system boundaries, layer ownership, active scope, or signal definitions change.
- Update docs and ADRs whenever implementation choices differ from the plan.

## Research-First Workflow
Before adding main screener code, create or update:
- `docs/DESIGN.md`
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
Use `docs/DESIGN.md` as the short design authority for current system structure, layer ownership, scope, and active signal definitions. Use ADRs for major choices: data provider, storage, dashboard, backtesting engine, broker path, and alpha methodology. Keep `docs/DECISIONS.md` as the index.

Before changing a signal, dashboard page, research diagnostic, provider, or storage flow, check whether the change fits the design document. If it does not, update the design document first and explain the reason in `docs/RESEARCH_LOG.md` or an ADR.

### Change Control Checklist
Before implementing a new feature or changing an existing one, answer:
- What research question does this answer?
- Which layer owns it: data, feature, signal, research, dashboard, or docs?
- Does this duplicate an existing metric, slice, score, or chart?
- Does this change a frozen signal definition?
- Does it require a new signal version?
- Does it require an ADR?
- What tests or research artifact will verify it?
- Which docs need to be updated?

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
