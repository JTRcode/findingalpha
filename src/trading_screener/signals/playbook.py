from __future__ import annotations

import pandas as pd


def add_intraday_setup_scores(features: pd.DataFrame) -> pd.DataFrame:
    df = features.copy()
    df["setup_b_trend_pullback_score"] = (
        (df["close"] > df["session_vwap"]).astype(float) * 0.25
        + (df["close"] > df["ema_20"]).astype(float) * 0.20
        + df["vwap_reclaim"].astype(float) * 0.25
        + df["volume_spike"].astype(float) * 0.20
        + (df["near_vwap"] | df["near_ema20"]).astype(float) * 0.10
    )
    df["setup_a_exhaustion_score"] = (
        (df["range_30m_pct"] > 0.025).astype(float) * 0.25
        + df["volume_spike"].astype(float) * 0.25
        + df["vwap_loss"].astype(float) * 0.30
        + (df["return_1m"] < -0.005).astype(float) * 0.20
    )
    df["setup_c_failed_bounce_score"] = (
        (df["close"] < df["session_vwap"]).astype(float) * 0.20
        + (df["close"] < df["ema_20"]).astype(float) * 0.20
        + df["vwap_loss"].astype(float) * 0.25
        + df["volume_spike"].astype(float) * 0.20
        + (df["return_1m"] < 0).astype(float) * 0.15
    )
    setup_columns = [
        "setup_b_trend_pullback_score",
        "setup_a_exhaustion_score",
        "setup_c_failed_bounce_score",
    ]
    df["best_intraday_setup"] = df[setup_columns].idxmax(axis=1).str.replace("_score", "", regex=False)
    df["best_intraday_setup_score"] = df[setup_columns].max(axis=1)
    df["intraday_signal_explanation"] = df.apply(_explain_intraday_row, axis=1)
    return df


def intraday_candidates(scored: pd.DataFrame, min_score: float = 0.65) -> pd.DataFrame:
    candidates = scored[scored["best_intraday_setup_score"] >= min_score].copy()
    return candidates.sort_values(["timestamp", "best_intraday_setup_score"], ascending=[False, False]).reset_index(drop=True)


def _explain_intraday_row(row: pd.Series) -> str:
    parts: list[str] = []
    if row.get("vwap_reclaim", False):
        parts.append("VWAP reclaim")
    if row.get("vwap_loss", False):
        parts.append("VWAP loss")
    if row.get("volume_spike", False):
        parts.append("1m volume spike")
    if row.get("volume_dryup", False):
        parts.append("volume dry-up")
    if row.get("near_vwap", False):
        parts.append("near VWAP")
    if row.get("near_ema20", False):
        parts.append("near 20 EMA")
    return "; ".join(parts) if parts else "intraday structure watch"

