# ADR 0005: Broker Path Later

Date: 2026-05-10
Status: Accepted

## Context
The user is in Vancouver, Canada. Later phases may include paper trading or supervised trading, but phase 1 must not implement execution.

## Options considered
- Interactive Brokers Canada: Canadian-accessible, broad global markets, TWS/Client Portal APIs, paper trading, market-data subscriptions. Complex but serious.
- Questrade API: Canadian brokerage API with account/market data and some partner trade scope. Customer order execution access appears constrained.
- Alpaca: Strong API/paper environment and U.S. market data. Live brokerage availability is not the default Canadian path.
- Wealthsimple: No suitable public trading API found for this use case.

## Decision
Keep Interactive Brokers Canada as the likely future broker path. Do not implement broker execution in phase 1. Any broker placeholder must raise `NotImplementedError` and include `future phase only`.

## Rationale
IBKR is the most complete Canadian-accessible API path for later research-to-paper-to-supervised workflows, but it adds unnecessary risk and complexity before alpha validation.

## Consequences
Phase 1 remains provider/data/research focused. Later IBKR integration will require separate compliance, market-data, risk-control, and testing work.

## Review triggers
- Signals show out-of-sample promise.
- Paper trading becomes an explicit phase.
- Broker account permissions and data subscriptions are confirmed.
- Risk controls and audit logging are implemented.

