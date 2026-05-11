from __future__ import annotations

import pandas as pd


FEATURE_WEIGHTS = {
    "momentum_20d": 0.25,
    "momentum_5d": 0.15,
    "price_vs_sma20": 0.15,
    "price_vs_sma50": 0.15,
    "relative_volume": 0.10,
    "proximity_52w_high": 0.10,
    "atr_pct": -0.10,
}


def add_composite_score(features: pd.DataFrame) -> pd.DataFrame:
    df = features.copy()
    score = pd.Series(0.0, index=df.index)
    for column, weight in FEATURE_WEIGHTS.items():
        if column not in df:
            continue
        ranks = df.groupby("date")[column].rank(pct=True, na_option="keep")
        if weight < 0:
            ranks = 1 - ranks
        score = score.add(ranks.fillna(0.5) * abs(weight), fill_value=0)
    df["composite_score"] = (score / sum(abs(v) for v in FEATURE_WEIGHTS.values())).round(4)
    return df


def explain_signal(row: pd.Series) -> str:
    parts: list[str] = []
    if row.get("momentum_20d", 0) > 0:
        parts.append("positive 20d momentum")
    if row.get("relative_volume", 0) > 1.5:
        parts.append("elevated relative volume")
    if row.get("proximity_52w_high", 0) > 0.95:
        parts.append("near 52w high")
    if row.get("atr_pct", 0) > 0.08:
        parts.append("high volatility")
    return "; ".join(parts) if parts else "baseline technical profile"


def risk_flags(row: pd.Series) -> str:
    flags: list[str] = []
    if row.get("dollar_volume", 0) < 10_000_000:
        flags.append("low_liquidity")
    if row.get("atr_pct", 0) > 0.08:
        flags.append("high_volatility")
    if abs(row.get("gap_pct", 0)) > 0.08:
        flags.append("large_gap")
    return ",".join(flags)

