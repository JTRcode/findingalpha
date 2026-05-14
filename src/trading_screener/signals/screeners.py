from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from trading_screener.features.technicals import add_technical_features
from trading_screener.signals.daily_playbook import add_daily_playbook_scores
from trading_screener.signals.scoring import add_composite_score, explain_signal, risk_flags


def build_ranked_screen(
    bars: pd.DataFrame,
    provider: str,
    universe: str,
    config_version: str,
    code_version: str,
) -> pd.DataFrame:
    features = add_technical_features(bars)
    scored = add_daily_playbook_scores(add_composite_score(features))
    return build_ranked_screen_from_scored(
        scored=scored,
        provider=provider,
        universe=universe,
        config_version=config_version,
        code_version=code_version,
    )


def build_ranked_screen_from_scored(
    scored: pd.DataFrame,
    provider: str,
    universe: str,
    config_version: str,
    code_version: str,
) -> pd.DataFrame:
    latest_dates = scored.groupby("ticker")["date"].transform("max")
    latest = scored[scored["date"] == latest_dates].copy()
    latest["run_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    latest["provider"] = provider
    latest["market_data_timestamp"] = latest["date"].astype(str)
    latest["price"] = latest["adj_close"].fillna(latest["close"])
    latest["signal_explanation"] = latest.apply(explain_signal, axis=1)
    latest["risk_flags"] = latest.apply(risk_flags, axis=1)
    latest["universe"] = universe
    latest["config_version"] = config_version
    latest["code_version"] = code_version
    return latest.sort_values("composite_score", ascending=False).reset_index(drop=True)
