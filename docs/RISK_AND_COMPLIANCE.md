# Risk and Compliance

Date: 2026-05-10

## Scope
This project is for personal research only. It is not financial advice and must not place orders in phase 1.

## Canada Considerations
The user is in Vancouver, Canada. Before any automation, research broker rules, account permissions, tax implications, CIRO considerations, market-data agreements, and whether any activity could be considered advising or managing money for others. Keep the project personal unless professional compliance advice says otherwise.

## Phase 1 Rules
- No live trading.
- No automated trading.
- No broker credentials.
- No order placement.
- No execution algorithms.
- No LLM-only trading decisions.

## Future Required Risk Controls
- max position size
- max daily loss
- max open trades
- duplicate-order prevention
- kill switch
- market-hours guard
- rejected-order handling
- broker disconnect handling
- full decision logs
- audit trail for every signal and later every order

## Major Research Risks
- survivorship bias
- lookahead bias
- adjusted vs unadjusted price confusion
- stock splits and dividends
- delisted symbols
- bad timestamp handling
- delayed vs real-time data confusion
- API rate limits
- licensing restrictions
- transaction costs
- slippage
- overfitting
- data snooping
- news timestamp leakage
- using today’s index constituents for old periods
- concentrated results
- regime-specific results mistaken for durable alpha

## Vendor and Licensing Risk
Do not redistribute vendor data or derived datasets without checking terms. yfinance/Yahoo data is suitable only as a personal research starting point and should be replaced before any professional or shared use.

