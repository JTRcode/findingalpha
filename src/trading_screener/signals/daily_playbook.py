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
SETUP_B_GATE_COLUMNS = {
    "Trend": ("setup_b_trend_gate", "setup_b_trend_quality"),
    "Pullback": ("setup_b_pullback_gate", "setup_b_pullback_quality"),
    "Volume Dry-Up": ("setup_b_volume_dryup_gate", "setup_b_volume_quality"),
    "Structure": ("setup_b_structure_gate", "setup_b_structure_quality"),
    "Confirmation": ("setup_b_confirmation_gate", "setup_b_confirmation_quality"),
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


def setup_b_condition_definitions(df: pd.DataFrame) -> list[dict[str, object]]:
    condition_order = 0

    def numbered_condition(*args: object) -> dict[str, object]:
        nonlocal condition_order
        condition_order += 1
        definition = _condition_def(*args)
        definition["condition_order"] = condition_order
        definition["gate_order"] = _setup_b_gate_order(str(definition["gate"]))
        return definition

    return [
        numbered_condition("Trend", "60D momentum", "momentum_60d", "> 4%", df["momentum_60d"] > 0.04, "> 10%", df["momentum_60d"] > 0.10),
        numbered_condition("Trend", "Price vs 50 SMA", "price_vs_sma50", "> -2%", df["price_vs_sma50"] > -0.02, "> 2%", df["price_vs_sma50"] > 0.02),
        numbered_condition("Trend", "Price vs 200 SMA", "price_vs_sma200", "> -5%", df["price_vs_sma200"] > -0.05, "> 0%", df["price_vs_sma200"] > 0),
        numbered_condition(
            "Trend",
            "Moving-average alignment",
            "sma_20,sma_50,close",
            "20 SMA > 50 SMA OR close > 50 SMA",
            (df["sma_20"] > df["sma_50"]) | (df["close"] > df["sma_50"]),
            "20 SMA > 50 SMA",
            df["sma_20"] > df["sma_50"],
        ),
        numbered_condition(
            "Pullback",
            "Pullback from 10D high",
            "pullback_from_10d_high",
            "-10% to -0.5%",
            df["pullback_from_10d_high"].between(-0.10, -0.005),
            "-7% to -1.5%",
            df["pullback_from_10d_high"].between(-0.07, -0.015),
        ),
        numbered_condition(
            "Pullback",
            "Down days in last 7 sessions",
            "pullback_days_7d",
            "1 to 7",
            df["pullback_days_7d"].between(1, 7),
            "2 to 6",
            df["pullback_days_7d"].between(2, 6),
        ),
        numbered_condition(
            "Pullback",
            "Large red candles in last 5 sessions",
            "large_red_candles_5d",
            "<= 1",
            df["large_red_candles_5d"] <= 1,
            "== 0",
            df["large_red_candles_5d"] == 0,
        ),
        numbered_condition(
            "Pullback",
            "Orderly pullback proxy",
            "orderly_pullback_proxy",
            "not required",
            pd.Series(True, index=df.index),
            "required",
            df["orderly_pullback_proxy"],
        ),
        numbered_condition(
            "Volume",
            "Current relative volume",
            "relative_volume,pullback_volume_ratio",
            "< 1.25 OR pullback volume ratio < 1.10",
            (df["relative_volume"] < 1.25) | (df["pullback_volume_ratio"] < 1.10),
            "< 0.90",
            df["relative_volume"] < 0.90,
        ),
        numbered_condition(
            "Volume",
            "Pullback volume ratio",
            "relative_volume,pullback_volume_ratio",
            "< 1.10 OR relative volume < 1.25",
            (df["relative_volume"] < 1.25) | (df["pullback_volume_ratio"] < 1.10),
            "< 0.90",
            df["pullback_volume_ratio"] < 0.90,
        ),
        numbered_condition(
            "Structure",
            "Price holds 20/50 SMA area",
            "price_vs_sma20,price_vs_sma50",
            "price vs 20 SMA > -5% OR price vs 50 SMA > -3%",
            (df["price_vs_sma20"] > -0.05) | (df["price_vs_sma50"] > -0.03),
            "price vs 20 SMA > -2% OR price vs 50 SMA > -1%",
            (df["price_vs_sma20"] > -0.02) | (df["price_vs_sma50"] > -0.01),
        ),
        numbered_condition("Structure", "20D momentum not broken", "momentum_20d", "> -8%", df["momentum_20d"] > -0.08, "> -2%", df["momentum_20d"] > -0.02),
        numbered_condition(
            "Structure",
            "Close vs 50 SMA",
            "close,sma_50",
            "close > 96% of 50 SMA",
            df["close"] > df["sma_50"] * 0.96,
            "close > 50 SMA",
            df["close"] > df["sma_50"],
        ),
        numbered_condition("Confirmation", "1D return", "return_1d", "> -0.5%", df["return_1d"] > -0.005, "> 0%", df["return_1d"] > 0),
        numbered_condition(
            "Confirmation",
            "Close position in daily range",
            "close_position_in_range",
            "> 45%",
            df["close_position_in_range"] > 0.45,
            "> 65%",
            df["close_position_in_range"] > 0.65,
        ),
        numbered_condition(
            "Confirmation",
            "Reclaim / close above 20 SMA / positive day",
            "reclaims_prior_high,close,sma_20,return_1d",
            "reclaim prior high OR close > 20 SMA OR 1D return > 0",
            df["reclaims_prior_high"] | (df["close"] > df["sma_20"]) | (df["return_1d"] > 0),
            "reclaim prior high OR close > 20 SMA",
            df["reclaims_prior_high"] | (df["close"] > df["sma_20"]),
        ),
    ]


def setup_b_gate_masks(df: pd.DataFrame, rule_set: str) -> list[tuple[str, pd.Series]]:
    definitions = setup_b_condition_definitions(df)
    mask_key = "broad_mask" if rule_set == "broad" else "strict_mask"
    return [
        (gate, _and_masks([definition[mask_key] for definition in definitions if definition["gate"] == gate]))
        for gate in ["Trend", "Pullback", "Volume", "Structure", "Confirmation"]
    ]


def setup_b_gate_audit(row: pd.Series) -> pd.DataFrame:
    rows: list[dict[str, object]] = [
        {
            "Gate": "Broad Scanner",
            "Role": "Eligibility",
            "Status": _pass_fail(row.get("setup_b_scanner_gate")),
            "Quality Score": _format_float(row.get("best_daily_setup_score")),
            "What It Checks": "Loose trend, pullback, volume, structure, and confirmation evidence. Required for candidate inclusion.",
        },
        {
            "Gate": "Strict Match",
            "Role": "Clean-playbook audit",
            "Status": _pass_fail(row.get("setup_b_strict_gate")),
            "Quality Score": _format_float(row.get("best_daily_setup_score")),
            "What It Checks": "Original stricter all-gates definition. Useful for chart quality, not required for broad research.",
        },
    ]
    rows.extend(
        {
            "Gate": gate,
            "Role": "Strict component",
            "Status": _pass_fail(row.get(gate_column)),
            "Quality Score": _format_float(row.get(quality_column)),
            "What It Checks": _setup_b_gate_description(gate),
        }
        for gate, (gate_column, quality_column) in SETUP_B_GATE_COLUMNS.items()
    )
    return pd.DataFrame(rows)


def setup_b_condition_audit(row: pd.Series) -> pd.DataFrame:
    rules = [
        {
            "Gate": "Trend",
            "Condition": "60D momentum",
            "Value": _format_pct(row.get("momentum_60d")),
            "Broad Rule": "> 4%",
            "Broad Pass": _pass_fail(_gt(row, "momentum_60d", 0.04)),
            "Strict Rule": "> 10%",
            "Strict Pass": _pass_fail(_gt(row, "momentum_60d", 0.10)),
        },
        {
            "Gate": "Trend",
            "Condition": "Price vs 50 SMA",
            "Value": _format_pct(row.get("price_vs_sma50")),
            "Broad Rule": "> -2%",
            "Broad Pass": _pass_fail(_gt(row, "price_vs_sma50", -0.02)),
            "Strict Rule": "> 2%",
            "Strict Pass": _pass_fail(_gt(row, "price_vs_sma50", 0.02)),
        },
        {
            "Gate": "Trend",
            "Condition": "Price vs 200 SMA",
            "Value": _format_pct(row.get("price_vs_sma200")),
            "Broad Rule": "> -5%",
            "Broad Pass": _pass_fail(_gt(row, "price_vs_sma200", -0.05)),
            "Strict Rule": "> 0%",
            "Strict Pass": _pass_fail(_gt(row, "price_vs_sma200", 0)),
        },
        {
            "Gate": "Trend",
            "Condition": "Moving-average alignment",
            "Value": _ma_alignment_value(row),
            "Broad Rule": "20 SMA > 50 SMA OR close > 50 SMA",
            "Broad Pass": _pass_fail(_greater_values(row.get("sma_20"), row.get("sma_50")) or _greater_values(row.get("close"), row.get("sma_50"))),
            "Strict Rule": "20 SMA > 50 SMA",
            "Strict Pass": _pass_fail(_greater_values(row.get("sma_20"), row.get("sma_50"))),
        },
        {
            "Gate": "Pullback",
            "Condition": "Pullback from 10D high",
            "Value": _format_pct(row.get("pullback_from_10d_high")),
            "Broad Rule": "-10% to -0.5%",
            "Broad Pass": _pass_fail(_between(row, "pullback_from_10d_high", -0.10, -0.005)),
            "Strict Rule": "-7% to -1.5%",
            "Strict Pass": _pass_fail(_between(row, "pullback_from_10d_high", -0.07, -0.015)),
        },
        {
            "Gate": "Pullback",
            "Condition": "Down days in last 7 sessions",
            "Value": _format_float(row.get("pullback_days_7d"), digits=0),
            "Broad Rule": "1 to 7",
            "Broad Pass": _pass_fail(_between(row, "pullback_days_7d", 1, 7)),
            "Strict Rule": "2 to 6",
            "Strict Pass": _pass_fail(_between(row, "pullback_days_7d", 2, 6)),
        },
        {
            "Gate": "Pullback",
            "Condition": "Large red candles in last 5 sessions",
            "Value": _format_float(row.get("large_red_candles_5d"), digits=0),
            "Broad Rule": "<= 1",
            "Broad Pass": _pass_fail(_le(row, "large_red_candles_5d", 1)),
            "Strict Rule": "== 0",
            "Strict Pass": _pass_fail(_eq(row, "large_red_candles_5d", 0)),
        },
        {
            "Gate": "Pullback",
            "Condition": "Orderly pullback proxy",
            "Value": _pass_fail(row.get("orderly_pullback_proxy")),
            "Broad Rule": "not required",
            "Broad Pass": "n/a",
            "Strict Rule": "required",
            "Strict Pass": _pass_fail(row.get("orderly_pullback_proxy")),
        },
        {
            "Gate": "Volume",
            "Condition": "Current relative volume",
            "Value": _format_float(row.get("relative_volume")),
            "Broad Rule": "< 1.25 OR pullback volume ratio < 1.10",
            "Broad Pass": _pass_fail(_lt(row, "relative_volume", 1.25) or _lt(row, "pullback_volume_ratio", 1.10)),
            "Strict Rule": "< 0.90",
            "Strict Pass": _pass_fail(_lt(row, "relative_volume", 0.90)),
        },
        {
            "Gate": "Volume",
            "Condition": "Pullback volume ratio",
            "Value": _format_float(row.get("pullback_volume_ratio")),
            "Broad Rule": "< 1.10 OR relative volume < 1.25",
            "Broad Pass": _pass_fail(_lt(row, "relative_volume", 1.25) or _lt(row, "pullback_volume_ratio", 1.10)),
            "Strict Rule": "< 0.90",
            "Strict Pass": _pass_fail(_lt(row, "pullback_volume_ratio", 0.90)),
        },
        {
            "Gate": "Structure",
            "Condition": "Price holds 20/50 SMA area",
            "Value": f"20SMA {_format_pct(row.get('price_vs_sma20'))}; 50SMA {_format_pct(row.get('price_vs_sma50'))}",
            "Broad Rule": "price vs 20 SMA > -5% OR price vs 50 SMA > -3%",
            "Broad Pass": _pass_fail(_gt(row, "price_vs_sma20", -0.05) or _gt(row, "price_vs_sma50", -0.03)),
            "Strict Rule": "price vs 20 SMA > -2% OR price vs 50 SMA > -1%",
            "Strict Pass": _pass_fail(_gt(row, "price_vs_sma20", -0.02) or _gt(row, "price_vs_sma50", -0.01)),
        },
        {
            "Gate": "Structure",
            "Condition": "20D momentum not broken",
            "Value": _format_pct(row.get("momentum_20d")),
            "Broad Rule": "> -8%",
            "Broad Pass": _pass_fail(_gt(row, "momentum_20d", -0.08)),
            "Strict Rule": "> -2%",
            "Strict Pass": _pass_fail(_gt(row, "momentum_20d", -0.02)),
        },
        {
            "Gate": "Structure",
            "Condition": "Close vs 50 SMA",
            "Value": _format_pct(row.get("price_vs_sma50")),
            "Broad Rule": "close > 96% of 50 SMA",
            "Broad Pass": _pass_fail(_greater_values(row.get("close"), _multiply(row.get("sma_50"), 0.96))),
            "Strict Rule": "close > 50 SMA",
            "Strict Pass": _pass_fail(_greater_values(row.get("close"), row.get("sma_50"))),
        },
        {
            "Gate": "Confirmation",
            "Condition": "1D return",
            "Value": _format_pct(row.get("return_1d")),
            "Broad Rule": "> -0.5%",
            "Broad Pass": _pass_fail(_gt(row, "return_1d", -0.005)),
            "Strict Rule": "> 0%",
            "Strict Pass": _pass_fail(_gt(row, "return_1d", 0)),
        },
        {
            "Gate": "Confirmation",
            "Condition": "Close position in daily range",
            "Value": _format_pct(row.get("close_position_in_range")),
            "Broad Rule": "> 45%",
            "Broad Pass": _pass_fail(_gt(row, "close_position_in_range", 0.45)),
            "Strict Rule": "> 65%",
            "Strict Pass": _pass_fail(_gt(row, "close_position_in_range", 0.65)),
        },
        {
            "Gate": "Confirmation",
            "Condition": "Reclaim / close above 20 SMA / positive day",
            "Value": _confirmation_value(row),
            "Broad Rule": "reclaim prior high OR close > 20 SMA OR 1D return > 0",
            "Broad Pass": _pass_fail(row.get("reclaims_prior_high") or _greater_values(row.get("close"), row.get("sma_20")) or _gt(row, "return_1d", 0)),
            "Strict Rule": "reclaim prior high OR close > 20 SMA",
            "Strict Pass": _pass_fail(row.get("reclaims_prior_high") or _greater_values(row.get("close"), row.get("sma_20"))),
        },
    ]
    return pd.DataFrame(rules)


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


def _condition_def(
    gate: str,
    condition: str,
    source_columns: str,
    broad_rule: str,
    broad_mask: pd.Series,
    strict_rule: str,
    strict_mask: pd.Series,
) -> dict[str, object]:
    return {
        "gate": gate,
        "condition": condition,
        "source_columns": source_columns,
        "broad_rule": broad_rule,
        "broad_mask": broad_mask.fillna(False).astype(bool),
        "strict_rule": strict_rule,
        "strict_mask": strict_mask.fillna(False).astype(bool),
    }


def _setup_b_gate_order(gate: str) -> int:
    return {
        "Trend": 1,
        "Pullback": 2,
        "Volume": 3,
        "Structure": 4,
        "Confirmation": 5,
    }.get(gate, 99)


def _and_masks(masks: list[pd.Series]) -> pd.Series:
    if not masks:
        return pd.Series(dtype=bool)
    result = masks[0].copy()
    for mask in masks[1:]:
        result = result & mask
    return result.fillna(False).astype(bool)


def _setup_b_gate_description(gate: str) -> str:
    descriptions = {
        "Trend": "Strong 60D trend and moving-average alignment.",
        "Pullback": "Controlled pullback depth/duration without large red breakdown candles.",
        "Volume Dry-Up": "Current and recent pullback volume are lower than prior activity.",
        "Structure": "Price holds the 20/50 SMA area and short-term momentum has not broken.",
        "Confirmation": "Positive or constructive candle with upper-range close and level reclaim.",
    }
    return descriptions.get(gate, "")


def _pass_fail(value: object) -> str:
    if pd.isna(value):
        return "n/a"
    return "PASS" if bool(value) else "FAIL"


def _format_float(value: object, digits: int = 2) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):.{digits}f}"


def _format_pct(value: object) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value) * 100:.2f}%"


def _bool(value: object) -> bool:
    if pd.isna(value):
        return False
    return bool(value)


def _gt(row: pd.Series, column: str, threshold: float) -> bool:
    value = row.get(column)
    return False if pd.isna(value) else bool(float(value) > threshold)


def _lt(row: pd.Series, column: str, threshold: float) -> bool:
    value = row.get(column)
    return False if pd.isna(value) else bool(float(value) < threshold)


def _le(row: pd.Series, column: str, threshold: float) -> bool:
    value = row.get(column)
    return False if pd.isna(value) else bool(float(value) <= threshold)


def _eq(row: pd.Series, column: str, threshold: float) -> bool:
    value = row.get(column)
    return False if pd.isna(value) else bool(float(value) == threshold)


def _between(row: pd.Series, column: str, low: float, high: float) -> bool:
    value = row.get(column)
    return False if pd.isna(value) else bool(low <= float(value) <= high)


def _multiply(value: object, multiplier: float) -> float:
    return np.nan if pd.isna(value) else float(value) * multiplier


def _greater_values(left: object, right: object) -> bool:
    if pd.isna(left) or pd.isna(right):
        return False
    return bool(float(left) > float(right))


def _ma_alignment_value(row: pd.Series) -> str:
    sma_20 = row.get("sma_20")
    sma_50 = row.get("sma_50")
    close = row.get("close")
    if pd.isna(sma_20) or pd.isna(sma_50) or pd.isna(close):
        return ""
    sma_spread = float(sma_20) / float(sma_50) - 1 if float(sma_50) != 0 else np.nan
    close_vs_50 = float(close) / float(sma_50) - 1 if float(sma_50) != 0 else np.nan
    return f"20/50 spread {_format_pct(sma_spread)}; close vs 50 {_format_pct(close_vs_50)}"


def _confirmation_value(row: pd.Series) -> str:
    reclaim = _pass_fail(row.get("reclaims_prior_high"))
    close_above_20 = _pass_fail(_greater_values(row.get("close"), row.get("sma_20")))
    positive_day = _pass_fail(_gt(row, "return_1d", 0))
    return f"reclaim {reclaim}; close > 20 SMA {close_above_20}; positive day {positive_day}"


def _setup_b_broad_scanner_gate(df: pd.DataFrame) -> pd.Series:
    return _and_masks([mask for _, mask in setup_b_gate_masks(df, rule_set="broad")])
