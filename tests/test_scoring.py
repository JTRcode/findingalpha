from __future__ import annotations

from tests.test_features import sample_bars
from trading_screener.features.technicals import add_technical_features
from trading_screener.signals.scoring import add_composite_score, explain_signal, risk_flags


def test_add_composite_score_bounds_scores() -> None:
    scored = add_composite_score(add_technical_features(sample_bars()))

    assert scored["composite_score"].between(0, 1).all()
    assert scored["composite_score"].notna().all()


def test_explanation_and_risk_flags_are_strings() -> None:
    row = add_composite_score(add_technical_features(sample_bars())).iloc[-1]

    assert isinstance(explain_signal(row), str)
    assert isinstance(risk_flags(row), str)

