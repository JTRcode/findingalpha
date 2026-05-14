from __future__ import annotations

from tests.test_features import sample_bars
from trading_screener.features.technicals import add_technical_features
from trading_screener.research.setup_eval import (
    evaluate_daily_setups,
    evaluate_setup_b_benchmark_relative_monthly,
    evaluate_setup_b_bucket_diagnostics,
    evaluate_setup_b_date_declustering,
    evaluate_setup_b_filter_diagnostics,
    evaluate_setup_b_indicator_diagnostics,
    evaluate_setup_b_interaction_slices,
    evaluate_setup_b_market_regime_diagnostics,
    evaluate_setup_b_outlier_diagnostics,
    evaluate_setup_b_score_buckets,
    evaluate_setup_b_sector_declustering,
    evaluate_setup_b_slices,
    evaluate_setup_b_time_consistency,
    evaluate_setup_b_variants,
    interpret_setup_b_spread,
)
from trading_screener.signals.daily_playbook import (
    add_daily_playbook_scores,
    daily_setup_candidates,
    setup_b_condition_audit,
    setup_b_gate_audit,
)
from trading_screener.signals.scoring import add_composite_score


def test_daily_playbook_scores_add_expected_columns() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))

    assert "best_daily_setup" in scored.columns
    assert "best_daily_setup_score" in scored.columns
    assert "daily_setup_b_version" in scored.columns
    assert "setup_b_trend_gate" in scored.columns
    assert "setup_b_scanner_gate" in scored.columns
    assert "setup_b_strict_gate" in scored.columns
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
    zero_score = scored["best_daily_setup_score"] == 0
    if zero_score.any():
        assert set(scored.loc[zero_score, "best_daily_setup"]) == {"none"}


def test_daily_setup_candidates_and_eval() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    candidate_index = scored.index[30]
    scored.loc[candidate_index, "best_daily_setup"] = "setup_b_trend_pullback"
    scored.loc[candidate_index, "best_daily_setup_score"] = 0.80
    scored.loc[candidate_index, "daily_setup_b_trend_pullback_score"] = 0.80
    candidates = daily_setup_candidates(scored, min_score=0.0)
    summary = evaluate_daily_setups(scored, min_score=0.0)

    assert not candidates.empty
    assert {"setup", "horizon_days", "count", "mean", "median", "win_rate"}.issubset(summary.columns)


def test_default_daily_setup_candidates_are_more_selective_than_loose_threshold() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    loose = daily_setup_candidates(scored, min_score=0.0)
    default = daily_setup_candidates(scored)

    assert len(default) <= len(loose)


def test_setup_b_audit_helpers_return_debug_tables() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    row = scored.iloc[-1]
    gate_audit = setup_b_gate_audit(row)
    condition_audit = setup_b_condition_audit(row)

    assert {"Gate", "Role", "Status", "Quality Score", "What It Checks"}.issubset(gate_audit.columns)
    assert {"Gate", "Condition", "Value", "Broad Rule", "Broad Pass", "Strict Rule", "Strict Pass"}.issubset(
        condition_audit.columns
    )
    assert "Trend" in set(condition_audit["Gate"])
    assert "Pullback" in set(condition_audit["Gate"])


def test_setup_b_bucket_eval_returns_dataframe() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    summary = evaluate_setup_b_score_buckets(scored)

    assert hasattr(summary, "columns")


def test_setup_b_filter_diagnostics_counts_conditions_and_funnel() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    diagnostics = evaluate_setup_b_filter_diagnostics(scored)

    assert {"diagnostic_type", "rule_set", "gate", "condition", "pass_count", "filtered_out_count"}.issubset(
        diagnostics.columns
    )
    assert {"independent_condition", "cumulative_funnel", "final_gate"}.issubset(
        set(diagnostics["diagnostic_type"])
    )
    assert {"broad", "strict"}.issubset(set(diagnostics["rule_set"]))


def test_setup_b_indicator_diagnostics_returns_dataframe() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    diagnostics = evaluate_setup_b_indicator_diagnostics(scored)

    assert hasattr(diagnostics, "columns")
    if not diagnostics.empty:
        assert {"indicator", "value", "horizon_days", "count", "mean", "median", "win_rate"}.issubset(
            diagnostics.columns
        )


def test_setup_b_bucket_diagnostics_returns_dataframes() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    diagnostics, spreads = evaluate_setup_b_bucket_diagnostics(scored)

    assert hasattr(diagnostics, "columns")
    assert hasattr(spreads, "columns")


def test_setup_b_slices_returns_dataframe() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    slices = evaluate_setup_b_slices(scored)

    assert hasattr(slices, "columns")


def test_setup_b_interaction_slices_returns_dataframe() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    interactions = evaluate_setup_b_interaction_slices(scored)

    assert hasattr(interactions, "columns")


def test_setup_b_variants_returns_dataframe() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    variants = evaluate_setup_b_variants(scored)

    assert hasattr(variants, "columns")


def test_setup_b_variants_include_benchmark_relative_returns() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    scored_with_spy = scored.copy()
    scored_with_spy.loc[scored_with_spy["ticker"] == "AAA", "ticker"] = "SPY"
    variants = evaluate_setup_b_variants(scored_with_spy)

    if not variants.empty:
        assert "relative_mean" in variants.columns


def test_setup_b_market_regime_diagnostics_return_dataframes() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    scored_with_spy = scored.copy()
    scored_with_spy.loc[scored_with_spy["ticker"] == "AAA", "ticker"] = "SPY"
    summary, monthly = evaluate_setup_b_market_regime_diagnostics(scored_with_spy)

    assert hasattr(summary, "columns")
    assert hasattr(monthly, "columns")
    if not summary.empty:
        assert "market_regime" in summary.columns


def test_setup_b_declustering_diagnostics_return_dataframes() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    scored_with_benchmarks = scored.copy()
    scored_with_benchmarks.loc[scored_with_benchmarks["ticker"] == "AAA", "ticker"] = "SPY"
    monthly = evaluate_setup_b_benchmark_relative_monthly(scored_with_benchmarks)
    date_declustered = evaluate_setup_b_date_declustering(scored_with_benchmarks)
    sector_declustered = evaluate_setup_b_sector_declustering(scored_with_benchmarks)

    assert hasattr(monthly, "columns")
    assert hasattr(date_declustered, "columns")
    assert hasattr(sector_declustered, "columns")
    if not sector_declustered.empty:
        assert "status" in sector_declustered.columns


def test_setup_b_hardening_diagnostics_return_dataframes() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    scored_with_benchmarks = scored.copy()
    scored_with_benchmarks.loc[scored_with_benchmarks["ticker"] == "AAA", "ticker"] = "SPY"
    outliers = evaluate_setup_b_outlier_diagnostics(scored_with_benchmarks)
    consistency = evaluate_setup_b_time_consistency(scored_with_benchmarks)

    assert hasattr(outliers, "columns")
    assert hasattr(consistency, "columns")
    if not outliers.empty:
        assert {"group_type", "group_value", "horizon_days", "trimmed_mean_5_95", "top_1pct_return_share"}.issubset(
            outliers.columns
        )
    if not consistency.empty:
        assert {"benchmark", "group_type", "group_value", "positive_year_rate"}.issubset(consistency.columns)


def test_setup_b_market_regime_uses_benchmark_when_present() -> None:
    scored = add_daily_playbook_scores(add_composite_score(add_technical_features(sample_bars(days=260))))
    scored_with_spy = scored.copy()
    scored_with_spy.loc[scored_with_spy["ticker"] == "AAA", "ticker"] = "SPY"
    slices = evaluate_setup_b_slices(scored_with_spy)
    regimes = set(slices[slices["slice"] == "market_regime"]["value"]) if not slices.empty else set()

    assert "benchmark_missing" not in regimes


def test_interpret_setup_b_spread_labels_strength() -> None:
    assert interpret_setup_b_spread(5, -0.01, 0.10, 3) == "weak_or_negative"
    assert interpret_setup_b_spread(5, 0.012, 0.06, 2.5) == "promising"
    assert interpret_setup_b_spread(5, 0.006, 0.03, 1.8) == "interesting"
