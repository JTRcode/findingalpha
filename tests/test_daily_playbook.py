from __future__ import annotations

from tests.test_features import sample_bars
from trading_screener.features.technicals import add_technical_features
from trading_screener.research.setup_eval import (
    evaluate_daily_setups,
    evaluate_setup_b_bucket_diagnostics,
    evaluate_setup_b_score_buckets,
    interpret_setup_b_spread,
)
from trading_screener.signals.daily_playbook import add_daily_playbook_scores, daily_setup_candidates
from trading_screener.signals.scoring import add_composite_score


def test_daily_playbook_scores_add_expected_columns() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))

    assert "best_daily_setup" in scored.columns
    assert "best_daily_setup_score" in scored.columns
    assert "setup_b_trend_gate" in scored.columns
    assert "setup_b_pullback_gate" in scored.columns
    assert "setup_b_volume_dryup_gate" in scored.columns
    assert "setup_b_structure_gate" in scored.columns
    assert "setup_b_confirmation_gate" in scored.columns
    assert "setup_b_trend_quality" in scored.columns
    assert "setup_b_pullback_quality" in scored.columns
    assert "setup_b_volume_quality" in scored.columns
    assert "setup_b_structure_quality" in scored.columns
    assert "setup_b_confirmation_quality" in scored.columns
    assert scored["best_daily_setup_score"].between(0, 1).all()
    assert scored["setup_b_trend_quality"].between(0, 1).all()


def test_daily_setup_candidates_and_eval() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    candidates = daily_setup_candidates(scored, min_score=0.0)
    summary = evaluate_daily_setups(scored, min_score=0.0)

    assert not candidates.empty
    assert {"setup", "horizon_days", "count", "mean", "median", "win_rate"}.issubset(summary.columns)


def test_default_daily_setup_candidates_are_more_selective_than_loose_threshold() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    loose = daily_setup_candidates(scored, min_score=0.0)
    default = daily_setup_candidates(scored)

    assert len(default) <= len(loose)


def test_setup_b_bucket_eval_returns_dataframe() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    summary = evaluate_setup_b_score_buckets(scored)

    assert hasattr(summary, "columns")


def test_setup_b_bucket_diagnostics_returns_dataframes() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    diagnostics, spreads = evaluate_setup_b_bucket_diagnostics(scored)

    assert hasattr(diagnostics, "columns")
    assert hasattr(spreads, "columns")


def test_interpret_setup_b_spread_labels_strength() -> None:
    assert interpret_setup_b_spread(5, -0.01, 0.10, 3) == "weak_or_negative"
    assert interpret_setup_b_spread(5, 0.012, 0.06, 2.5) == "promising"
    assert interpret_setup_b_spread(5, 0.006, 0.03, 1.8) == "interesting"
