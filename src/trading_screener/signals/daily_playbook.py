from __future__ import annotations

import numpy as np
import pandas as pd


DAILY_SETUP_COLUMNS = [
    "daily_setup_b_trend_pullback_score",
    "daily_setup_a_exhaustion_score",
    "daily_setup_c_failed_bounce_score",
]

SETUP_B_VERSION = "setup_b_v1_broad_scanner"
SETUP_B_DEFAULT_MIN_SCORE = 0.60
SETUP_B_QUALITY_WEIGHTS = {
    "trend": 0.25,
    "pullback": 0.25,
    "structure": 0.20,
    "volume": 0.15,
    "confirmation": 0.15,
}


def add_daily_playbook_scores(features: pd.DataFrame) -> pd.DataFrame:
    df = features.copy()
    df["daily_setup_b_version"] = SETUP_B_VERSION

    df["setup_b_trend_gate"] = (
        (df["momentum_60d"] > 0.10)
        & (df["price_vs_sma50"] > 0.02)
        & (df["price_vs_sma200"] > 0)
        & (df["sma_20"] > df["sma_50"])
    )
    df["setup_b_pullback_gate"] = (
        df["pullback_from_10d_high"].between(-0.07, -0.015)
        & df["pullback_days_7d"].between(2, 6)
        & (df["large_red_candles_5d"] == 0)
        & df["orderly_pullback_proxy"]
    )
    df["setup_b_volume_dryup_gate"] = (df["relative_volume"] < 0.90) & (df["pullback_volume_ratio"] < 0.90)
    df["setup_b_structure_gate"] = (
        ((df["price_vs_sma20"] > -0.02) | (df["price_vs_sma50"] > -0.01))
        & (df["momentum_20d"] > -0.02)
        & (df["close"] > df["sma_50"])
    )
    df["setup_b_confirmation_gate"] = (
        (df["return_1d"] > 0)
        & (df["close_position_in_range"] > 0.65)
        & (df["reclaims_prior_high"] | (df["close"] > df["sma_20"]))
    )
    setup_b_gate = (
        df["setup_b_trend_gate"]
        & df["setup_b_pullback_gate"]
        & df["setup_b_volume_dryup_gate"]
        & df["setup_b_structure_gate"]
        & df["setup_b_confirmation_gate"]
    )
    df["setup_b_strict_gate"] = setup_b_gate
    df["setup_b_scanner_gate"] = _setup_b_broad_scanner_gate(df)

    trend_momentum_quality = _clip01((df["momentum_60d"] - 0.10) / 0.20)
    trend_ma_quality = _clip01((df["price_vs_sma50"] - 0.02) / 0.08)
    df["setup_b_trend_quality"] = ((trend_momentum_quality * 0.65) + (trend_ma_quality * 0.35)).fillna(0)

    pullback_depth = df["pullback_from_10d_high"].abs()
    pullback_depth_quality = _triangular_quality(pullback_depth, ideal=0.04, half_width=0.035)
    pullback_duration_quality = _triangular_quality(df["pullback_days_7d"], ideal=4.0, half_width=3.0)
    orderly_quality = df["orderly_pullback_proxy"].astype(float)
    df["setup_b_pullback_quality"] = (
        pullback_depth_quality * 0.45 + pullback_duration_quality * 0.35 + orderly_quality * 0.20
    ).fillna(0)

    current_volume_quality = _clip01((0.90 - df["relative_volume"]) / 0.40)
    pullback_volume_quality = _clip01((0.90 - df["pullback_volume_ratio"]) / 0.40)
    df["setup_b_volume_quality"] = (current_volume_quality * 0.45 + pullback_volume_quality * 0.55).fillna(0)

    sma20_hold_quality = _clip01((df["price_vs_sma20"] + 0.02) / 0.06)
    sma50_hold_quality = _clip01((df["price_vs_sma50"] + 0.01) / 0.06)
    df["setup_b_structure_quality"] = (sma20_hold_quality * 0.55 + sma50_hold_quality * 0.45).fillna(0)

    close_strength_quality = _clip01((df["close_position_in_range"] - 0.65) / 0.35)
    reclaim_quality = df["reclaims_prior_high"].astype(float)
    return_quality = _clip01(df["return_1d"] / 0.03)
    df["setup_b_confirmation_quality"] = (
        close_strength_quality * 0.45 + reclaim_quality * 0.30 + return_quality * 0.25
    ).fillna(0)

    setup_b_quality_score = (
        df["setup_b_trend_quality"] * SETUP_B_QUALITY_WEIGHTS["trend"]
        + df["setup_b_pullback_quality"] * SETUP_B_QUALITY_WEIGHTS["pullback"]
        + df["setup_b_structure_quality"] * SETUP_B_QUALITY_WEIGHTS["structure"]
        + df["setup_b_volume_quality"] * SETUP_B_QUALITY_WEIGHTS["volume"]
        + df["setup_b_confirmation_quality"] * SETUP_B_QUALITY_WEIGHTS["confirmation"]
    )

    df["daily_setup_b_trend_pullback_score"] = setup_b_quality_score * df["setup_b_scanner_gate"].astype(float)

    extended_run = (df["momentum_5d"] > 0.10) | (df["extension_from_20d_low"] > 0.22)
    stretched_from_ma = df["price_vs_sma20"] > 0.10
    high_volume = df["relative_volume"] > 1.8
    failed_strength = ((df["gap_pct"] > 0.02) | df["reclaims_prior_high"]) & (df["return_1d"] < 0)
    downside_reversal = (df["return_1d"] < -0.03) & (df["close_position_in_range"] < 0.35)
    setup_a_gate = extended_run & stretched_from_ma & high_volume & failed_strength & downside_reversal

    df["daily_setup_a_exhaustion_score"] = (
        extended_run.astype(float) * 0.25
        + stretched_from_ma.astype(float) * 0.20
        + high_volume.astype(float) * 0.20
        + failed_strength.astype(float) * 0.20
        + downside_reversal.astype(float) * 0.15
    ) * setup_a_gate.astype(float)

    weak_structure = (df["price_vs_sma20"] < 0) & (df["price_vs_sma50"] < 0)
    bounce_attempt = (df["up_days_5d"] >= 2) & (df["momentum_5d"] > -0.03)
    failed_reclaim = (df["price_vs_sma20"] < 0) & (df["return_1d"] < -0.01)
    downside_volume = (df["return_1d"] < 0) & (df["relative_volume"] > 1.25)
    lower_high_proxy = df["proximity_52w_high"] < 0.9
    confirmation_down = df["breaks_prior_low"] | (df["close_position_in_range"] < 0.35)
    setup_c_gate = weak_structure & bounce_attempt & failed_reclaim & downside_volume & confirmation_down

    df["daily_setup_c_failed_bounce_score"] = (
        weak_structure.astype(float) * 0.25
        + bounce_attempt.astype(float) * 0.15
        + failed_reclaim.astype(float) * 0.20
        + downside_volume.astype(float) * 0.20
        + lower_high_proxy.astype(float) * 0.10
        + confirmation_down.astype(float) * 0.10
    ) * setup_c_gate.astype(float)

    best_scores = df[DAILY_SETUP_COLUMNS].max(axis=1)
    df["best_daily_setup"] = df[DAILY_SETUP_COLUMNS].idxmax(axis=1).str.replace("daily_", "", regex=False).str.replace("_score", "", regex=False)
    df.loc[best_scores <= 0, "best_daily_setup"] = "none"
    df["best_daily_setup_score"] = best_scores
    df["daily_setup_explanation"] = df.apply(_explain_daily_row, axis=1)
    return df


def daily_setup_candidates(scored: pd.DataFrame, min_score: float = SETUP_B_DEFAULT_MIN_SCORE) -> pd.DataFrame:
    candidates = scored[(scored["best_daily_setup_score"] >= min_score) & (scored["best_daily_setup"] != "none")].copy()
    return candidates.sort_values(["date", "best_daily_setup_score"], ascending=[False, False]).reset_index(drop=True)


def _explain_daily_row(row: pd.Series) -> str:
    setup = row.get("best_daily_setup", "")
    parts: list[str] = []
    if setup == "none":
        return "no daily playbook setup"
    if setup == "setup_b_trend_pullback":
        if row.get("setup_b_scanner_gate", False):
            parts.append("broad scanner match")
        if row.get("setup_b_strict_gate", False):
            parts.append("strict setup match")
        gate_labels = [
            ("setup_b_trend_gate", "trend gate"),
            ("setup_b_pullback_gate", "pullback gate"),
            ("setup_b_volume_dryup_gate", "volume dry-up gate"),
            ("setup_b_structure_gate", "structure gate"),
            ("setup_b_confirmation_gate", "confirmation gate"),
        ]
        parts.extend(label for column, label in gate_labels if bool(row.get(column, False)))
    elif setup == "setup_a_exhaustion":
        if row.get("momentum_5d", 0) > 0.08:
            parts.append("extended 5d run")
        if row.get("price_vs_sma20", 0) > 0.08:
            parts.append("stretched above 20 SMA")
        if row.get("relative_volume", 0) > 1.5:
            parts.append("high relative volume")
        if row.get("return_1d", 0) < 0:
            parts.append("failed strength")
    elif setup == "setup_c_failed_bounce":
        if row.get("price_vs_sma20", 0) < 0:
            parts.append("below 20 SMA")
        if row.get("price_vs_sma50", 0) < 0:
            parts.append("below 50 SMA")
        if row.get("up_days_5d", 0) >= 2:
            parts.append("recent bounce attempt")
        if row.get("relative_volume", 0) > 1.1 and row.get("return_1d", 0) < 0:
            parts.append("downside volume")
    return "; ".join(parts) if parts else "prototype setup match"


def _clip01(series: pd.Series) -> pd.Series:
    return series.replace([np.inf, -np.inf], np.nan).clip(lower=0, upper=1)


def _triangular_quality(series: pd.Series, ideal: float, half_width: float) -> pd.Series:
    return _clip01(1 - ((series - ideal).abs() / half_width))


def _setup_b_broad_scanner_gate(df: pd.DataFrame) -> pd.Series:
    trend = (
        (df["momentum_60d"] > 0.04)
        & (df["price_vs_sma50"] > -0.02)
        & (df["price_vs_sma200"] > -0.05)
        & ((df["sma_20"] > df["sma_50"]) | (df["close"] > df["sma_50"]))
    )
    pullback = (
        df["pullback_from_10d_high"].between(-0.10, -0.005)
        & df["pullback_days_7d"].between(1, 7)
        & (df["large_red_candles_5d"] <= 1)
    )
    volume = (df["relative_volume"] < 1.25) | (df["pullback_volume_ratio"] < 1.10)
    structure = (
        ((df["price_vs_sma20"] > -0.05) | (df["price_vs_sma50"] > -0.03))
        & (df["momentum_20d"] > -0.08)
        & (df["close"] > df["sma_50"] * 0.96)
    )
    confirmation = (
        (df["return_1d"] > -0.005)
        & (df["close_position_in_range"] > 0.45)
        & (df["reclaims_prior_high"] | (df["close"] > df["sma_20"]) | (df["return_1d"] > 0))
    )
    return trend & pullback & volume & structure & confirmation
