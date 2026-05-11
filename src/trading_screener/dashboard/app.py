from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from trading_screener.signals.scoring import FEATURE_WEIGHTS


DATA_DIR = Path("data")
SETUP_LABELS = {
    "setup_b_trend_pullback": "Setup B - Trend Pullback Continuation",
    "setup_a_exhaustion": "Setup A - Exhaustion Pullback",
    "setup_c_failed_bounce": "Setup C - Failed Bounce Reversal",
}
DAILY_SETUP_LABELS = SETUP_LABELS


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern))
    return files[-1] if files else None


def latest_recursive_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern)) + sorted(directory.glob(f"*/{pattern}"))
    return files[-1] if files else None


def load_latest(directory: Path, pattern: str, recursive: bool = False) -> tuple[pd.DataFrame | None, Path | None]:
    path = latest_recursive_file(directory, pattern) if recursive else latest_file(directory, pattern)
    if path is None:
        return None, None
    return pd.read_parquet(path), path


def pct(value: object) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value) * 100:.2f}%"


def num(value: object) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):,.2f}"


def intish(value: object) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):,.0f}"


def format_daily_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    rename = {
        "ticker": "Ticker",
        "price": "Price",
        "volume": "Volume",
        "composite_score": "Score",
        "momentum_20d": "20D Momentum",
        "momentum_5d": "5D Momentum",
        "relative_volume": "Rel Volume",
        "proximity_52w_high": "52W High Proximity",
        "atr_pct": "ATR %",
        "signal_explanation": "Why It Scored",
        "risk_flags": "Risk Flags",
    }
    columns = [column for column in rename if column in out.columns]
    out = out[columns].rename(columns=rename)
    for column in ["20D Momentum", "5D Momentum", "52W High Proximity", "ATR %"]:
        if column in out:
            out[column] = out[column].map(pct)
    if "Price" in out:
        out["Price"] = out["Price"].map(num)
    if "Volume" in out:
        out["Volume"] = out["Volume"].map(intish)
    return out


def format_bucket_summary(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().rename(
        columns={
            "setup": "Setup",
            "score_bucket": "Bucket",
            "bucket": "Bucket",
            "count": "Observations",
            "mean": "Avg Forward Return",
            "median": "Median Forward Return",
            "win_rate": "Win Rate",
            "horizon_days": "Horizon Days",
        }
    )
    for column in ["Avg Forward Return", "Median Forward Return", "Win Rate"]:
        if column in out:
            out[column] = out[column].map(pct)
    return out


def format_intraday(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "best_intraday_setup" in out:
        out["best_intraday_setup"] = out["best_intraday_setup"].map(lambda value: SETUP_LABELS.get(value, value))
    rename = {
        "timestamp": "Timestamp",
        "provider": "Provider",
        "ticker": "Ticker",
        "close": "Close",
        "volume": "1m Volume",
        "session_vwap": "VWAP",
        "ema_20": "20 EMA",
        "relative_volume_20m": "Rel 1m Volume",
        "best_intraday_setup": "Best Setup",
        "best_intraday_setup_score": "Setup Score",
        "setup_b_trend_pullback_score": "Setup B Score",
        "setup_a_exhaustion_score": "Setup A Score",
        "setup_c_failed_bounce_score": "Setup C Score",
        "intraday_signal_explanation": "Why It Matched",
        "fwd_return_30m": "30m Fwd Return",
        "fwd_return_60m": "60m Fwd Return",
        "fwd_return_120m": "120m Fwd Return",
        "fwd_return_390m": "1D Fwd Return",
    }
    columns = [column for column in rename if column in out.columns]
    out = out[columns].rename(columns=rename)
    for column in ["Close", "VWAP", "20 EMA"]:
        if column in out:
            out[column] = out[column].map(num)
    for column in ["30m Fwd Return", "60m Fwd Return", "120m Fwd Return", "1D Fwd Return"]:
        if column in out:
            out[column] = out[column].map(pct)
    if "1m Volume" in out:
        out["1m Volume"] = out["1m Volume"].map(intish)
    return out


def format_daily_setups(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "best_daily_setup" in out:
        out["best_daily_setup"] = out["best_daily_setup"].map(lambda value: DAILY_SETUP_LABELS.get(value, value))
    rename = {
        "date": "Date",
        "ticker": "Ticker",
        "adj_close": "Close",
        "best_daily_setup": "Best Setup",
        "best_daily_setup_score": "Setup Score",
        "daily_setup_b_trend_pullback_score": "Setup B Score",
        "daily_setup_a_exhaustion_score": "Setup A Score",
        "daily_setup_c_failed_bounce_score": "Setup C Score",
        "momentum_60d": "60D Momentum",
        "pullback_from_10d_high": "Pullback From 10D High",
        "relative_volume": "Rel Volume",
        "daily_setup_explanation": "Why It Matched",
        "setup_b_trend_gate": "B Trend Gate",
        "setup_b_pullback_gate": "B Pullback Gate",
        "setup_b_volume_dryup_gate": "B Volume Gate",
        "setup_b_structure_gate": "B Structure Gate",
        "setup_b_confirmation_gate": "B Confirmation Gate",
        "setup_b_trend_quality": "B Trend Quality",
        "setup_b_pullback_quality": "B Pullback Quality",
        "setup_b_volume_quality": "B Volume Quality",
        "setup_b_structure_quality": "B Structure Quality",
        "setup_b_confirmation_quality": "B Confirmation Quality",
        "fwd_return_5d": "5D Fwd Return",
        "fwd_return_10d": "10D Fwd Return",
        "fwd_return_20d": "20D Fwd Return",
    }
    columns = [column for column in rename if column in out.columns]
    out = out[columns].rename(columns=rename)
    for column in ["60D Momentum", "Pullback From 10D High", "5D Fwd Return", "10D Fwd Return", "20D Fwd Return"]:
        if column in out:
            out[column] = out[column].map(pct)
    if "Close" in out:
        out["Close"] = out["Close"].map(num)
    for column in [
        "B Trend Gate",
        "B Pullback Gate",
        "B Volume Gate",
        "B Structure Gate",
        "B Confirmation Gate",
    ]:
        if column in out:
            out[column] = out[column].map(lambda value: "PASS" if bool(value) else "FAIL")
    return out


def format_setup_b_gate_panel(row: pd.Series) -> pd.DataFrame:
    gates = [
        ("Trend", "Strong 60d trend, above 50/200 SMA, 20 SMA above 50 SMA", row.get("setup_b_trend_gate"), row.get("setup_b_trend_quality")),
        ("Pullback", "2-6 down days in 7d, 1.5-7% below 10d high, no large red breakdown candles", row.get("setup_b_pullback_gate"), row.get("setup_b_pullback_quality")),
        ("Volume Dry-Up", "Current and recent pullback volume below prior activity", row.get("setup_b_volume_dryup_gate"), row.get("setup_b_volume_quality")),
        ("Structure", "Holds 20/50 SMA area, above 50 SMA, 20d momentum not broken", row.get("setup_b_structure_gate"), row.get("setup_b_structure_quality")),
        ("Confirmation", "Positive close in upper range, reclaim prior high or close above 20 SMA", row.get("setup_b_confirmation_gate"), row.get("setup_b_confirmation_quality")),
    ]
    return pd.DataFrame(
        {
            "Gate": [gate for gate, _, _, _ in gates],
            "Status": ["PASS" if bool(status) else "FAIL" for _, _, status, _ in gates],
            "Quality Score": [f"{float(quality or 0):.2f}" for _, _, _, quality in gates],
            "What It Checks": [description for _, description, _, _ in gates],
        }
    )


def load_scored_history() -> pd.DataFrame | None:
    path = DATA_DIR / "features" / "scored_history.parquet"
    if not path.exists():
        return None
    history = pd.read_parquet(path)
    history["date"] = pd.to_datetime(history["date"]).dt.date
    return history


def render_candlestick_with_volume(history: pd.DataFrame, ticker: str, signal_date: date, window_days: int) -> None:
    start = signal_date - timedelta(days=window_days)
    end = signal_date + timedelta(days=window_days)
    chart_data = history[(history["ticker"] == ticker) & (history["date"] >= start) & (history["date"] <= end)].copy()
    if chart_data.empty:
        st.info("No price history found for the selected candidate.")
        return

    chart_data["date_ts"] = pd.to_datetime(chart_data["date"])
    chart_data = chart_data.sort_values("date_ts").reset_index(drop=True)
    chart_data["date_label"] = chart_data["date"].astype(str)
    chart_data["session_index"] = list(range(len(chart_data)))
    chart_data["volume_color"] = chart_data.apply(
        lambda row: "#167A3A" if row["close"] >= row["open"] else "#B42318",
        axis=1,
    )

    visible_sessions = len(chart_data)
    chart_width = max(900, min(1800, visible_sessions * 18))

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25],
    )
    fig.add_trace(
        go.Candlestick(
            x=chart_data["session_index"],
            open=chart_data["open"],
            high=chart_data["high"],
            low=chart_data["low"],
            close=chart_data["close"],
            increasing_line_color="#167A3A",
            increasing_fillcolor="rgba(22,122,58,0.65)",
            decreasing_line_color="#B42318",
            decreasing_fillcolor="rgba(180,35,24,0.65)",
            name="Price",
            customdata=chart_data[["date_label", "volume"]],
            hovertemplate=(
                "Date: %{customdata[0]}<br>"
                "Open: %{open:.2f}<br>"
                "High: %{high:.2f}<br>"
                "Low: %{low:.2f}<br>"
                "Close: %{close:.2f}<br>"
                "Volume: %{customdata[1]:,.0f}<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=chart_data["session_index"],
            y=chart_data["volume"],
            marker_color=chart_data["volume_color"],
            opacity=0.55,
            name="Volume",
            customdata=chart_data[["date_label", "relative_volume"]] if "relative_volume" in chart_data else chart_data[["date_label"]],
            hovertemplate="Date: %{customdata[0]}<br>Volume: %{y:,.0f}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    signal_index = chart_data.loc[chart_data["date"] == signal_date, "session_index"]
    if not signal_index.empty:
        fig.add_vline(
            x=int(signal_index.iloc[0]),
            line_color="#1D4ED8",
            line_dash="dash",
            line_width=2,
            row="all",
            col=1,
        )

    tick_step = max(1, len(chart_data) // 8)
    tick_values = chart_data["session_index"][::tick_step]
    tick_text = chart_data["date_label"][::tick_step]
    fig.update_xaxes(
        tickmode="array",
        tickvals=tick_values,
        ticktext=tick_text,
        rangeslider_visible=False,
        showgrid=True,
        gridcolor="#243041",
        zeroline=False,
        color="#CBD5E1",
    )
    fig.update_yaxes(showgrid=True, gridcolor="#243041", zeroline=False, color="#CBD5E1", row=1, col=1)
    fig.update_yaxes(showgrid=True, gridcolor="#243041", zeroline=False, color="#CBD5E1", row=2, col=1)
    fig.update_layout(
        width=chart_width,
        height=620,
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        font={"color": "#CBD5E1"},
        margin={"l": 48, "r": 18, "t": 8, "b": 28},
        showlegend=False,
        xaxis_rangeslider_visible=False,
        bargap=0.18,
        dragmode="pan",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


def normalize_date_range(value: object, fallback_start: date, fallback_end: date) -> tuple[date, date]:
    if isinstance(value, list | tuple):
        if len(value) == 2:
            return pd.to_datetime(value[0]).date(), pd.to_datetime(value[1]).date()
        if len(value) == 1:
            selected = pd.to_datetime(value[0]).date()
            return selected, selected
    if value:
        selected = pd.to_datetime(value).date()
        return selected, selected
    return fallback_start, fallback_end


def date_months_back(end_date: date, months: int, min_date: date) -> date:
    # Good enough for dashboard filtering; avoids adding dateutil for calendar-month arithmetic.
    return max(min_date, end_date - timedelta(days=months * 30))


def render_sidebar() -> None:
    st.sidebar.title("Finding Alpha")
    st.sidebar.markdown(
        """
        **Flow**

        Data provider -> features -> scores -> signal snapshots -> forward-return tests -> dashboard.

        **Signal snapshot**

        A timestamped record of what the screener saw at run time. It preserves the ticker, price, features, score,
        explanation, provider, and universe so future research can ask: what happened after this signal existed?

        **Bucket**

        A score group. With 5 buckets, bucket 1 is the lowest-scored group and bucket 5 is the highest-scored group
        for that date. Good alpha evidence means higher buckets later outperform lower buckets consistently.
        """
    )


def render_overview() -> None:
    st.header("Research Pipeline")
    st.markdown(
        """
        ```text
        Run findingalpha
              |
              v
        Fetch daily or 1-minute bars
              |
              v
        Calculate features: momentum, pullback structure, VWAP, EMA, volume spikes, volatility
              |
              v
        Score stocks or intraday setup moments
              |
              v
        Save timestamped signal snapshots
              |
              v
        Calculate forward returns
              |
              v
        Check whether high scores predicted better future returns
        ```

        The dashboard is a viewer for saved research outputs. It does not stream live data and it does not trade.
        """
    )


def render_daily() -> None:
    st.header("Daily Screener")
    st.markdown(
        """
        This table is the latest daily signal snapshot. The score is a cross-sectional rank blend, not a trade signal.
        It answers: which tickers currently look strongest by simple daily features?
        """
    )
    snapshot, path = load_latest(DATA_DIR / "signals", "signal_snapshot_*.parquet")
    if snapshot is None:
        st.info("No daily signal snapshot found. Run `findingalpha --provider yfinance --tickers SPY QQQ NVDA AAPL --start 2024-01-01`.")
        return

    st.caption(f"File: {path}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Tickers", len(snapshot))
    col2.metric("Top Score", f"{snapshot['composite_score'].max():.2f}")
    col3.metric("Provider", str(snapshot["provider"].iloc[0]) if "provider" in snapshot else "unknown")

    if len(snapshot) < 5:
        st.warning(
            "This daily snapshot has fewer than 5 tickers. Daily bucket alpha tests need a broader universe; "
            "with one ticker, every date falls into one bucket."
        )
    if "universe_point_in_time" in snapshot and not bool(snapshot["universe_point_in_time"].iloc[0]):
        bias = snapshot.get("universe_survivorship_bias", pd.Series(["unknown"])).iloc[0]
        notes = snapshot.get("universe_notes", pd.Series([""])).iloc[0]
        st.warning(
            f"This universe is not point-in-time. Historical daily alpha tests may have survivorship bias. "
            f"Bias label: {bias}. {notes}"
        )

    st.dataframe(format_daily_snapshot(snapshot), width="stretch", hide_index=True)

    with st.expander("How the daily score is calculated"):
        weights = pd.DataFrame(
            [{"Feature": feature, "Weight": weight} for feature, weight in FEATURE_WEIGHTS.items()]
        )
        st.markdown(
            """
            Each feature is ranked across the ticker universe for the same date. Higher rank is better except ATR%,
            where lower volatility receives a better contribution. The weighted feature ranks are averaged into
            `composite_score`.
            """
        )
        st.dataframe(weights, width="stretch", hide_index=True)


def render_alpha_tests() -> None:
    st.header("Alpha Tests")
    st.markdown(
        """
        These tables test whether the score had predictive value. A useful signal should show better future returns
        in the highest bucket than the lowest bucket, across enough observations and multiple horizons.
        """
    )

    buckets, bucket_path = load_latest(DATA_DIR / "backtests", "forward_return_buckets_*.parquet")
    if buckets is not None:
        st.subheader("Forward Return Buckets")
        st.caption(f"File: {bucket_path}")
        bucket_count = buckets["score_bucket"].nunique() if "score_bucket" in buckets else 0
        if bucket_count <= 1:
            st.warning(
                "Only one bucket is present in this file. That usually means the run used only one ticker, "
                "so there was no cross-sectional universe to divide into buckets. Rerun daily mode with at "
                "least 5 tickers, preferably 20+ for useful alpha testing."
            )
        st.dataframe(format_bucket_summary(buckets), width="stretch", hide_index=True)
    else:
        st.info("No forward-return bucket file found yet.")

    benchmark, benchmark_path = load_latest(DATA_DIR / "backtests", "benchmark_comparison_*.parquet")
    if benchmark is not None:
        st.subheader("Benchmark Comparison")
        st.caption(f"File: {benchmark_path}")
        st.dataframe(benchmark, width="stretch", hide_index=True)

    basket, basket_path = load_latest(DATA_DIR / "backtests", "top_ranked_basket_*.parquet")
    if basket is not None:
        st.subheader("Simple Top-Ranked Basket")
        st.caption(f"File: {basket_path}")
        if "equity_curve" in basket and "date" in basket:
            st.line_chart(basket.set_index("date")["equity_curve"])
        st.dataframe(basket, width="stretch", hide_index=True)

    setup_eval, setup_eval_path = load_latest(DATA_DIR / "backtests", "daily_setup_forward_returns_*.parquet")
    if setup_eval is not None:
        st.subheader("Daily Setup Forward Returns")
        st.caption(f"File: {setup_eval_path}")
        st.dataframe(format_bucket_summary(setup_eval), width="stretch", hide_index=True)


def render_daily_setups() -> None:
    st.header("Daily Playbook Setups")
    st.markdown(
        """
        This tab looks for multi-day daily-chart versions of your playbook. It is still rule-based and preliminary,
        but it is closer to your actual process than the generic composite score.
        """
    )
    setups, path = load_latest(DATA_DIR / "signals", "daily_setup_candidates_*.parquet")
    if setups is None:
        st.info(
            "No daily setup candidates found. Run daily mode, for example: "
            "`findingalpha --provider yfinance --universe sp500_current --start 2024-01-01`."
        )
        return

    st.caption(f"File: {path}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Candidates", len(setups))
    col2.metric("Tickers", setups["ticker"].nunique() if "ticker" in setups else 0)
    col3.metric("Max Setup Score", f"{setups['best_daily_setup_score'].max():.2f}")

    forward_columns = [column for column in setups.columns if column.startswith("fwd_return_")]
    if forward_columns:
        coverage = pd.DataFrame(
            [
                {
                    "Forward Horizon": column.replace("fwd_return_", "").upper(),
                    "Rows With Result": int(setups[column].notna().sum()),
                    "Total Candidates": int(len(setups)),
                    "Coverage": setups[column].notna().mean(),
                }
                for column in forward_columns
            ]
        )
        coverage["Coverage"] = coverage["Coverage"].map(pct)
        with st.expander("Why some forward returns are blank", expanded=False):
            st.markdown(
                """
                Forward returns need future bars. A setup from the most recent trading day can have no 1-day
                forward return yet. A setup from last week may have 1-day and 5-day returns but not 20-day or
                60-day returns. Blanks usually mean the dataset does not extend far enough into the future.
                """
            )
            st.dataframe(coverage, width="stretch", hide_index=True)

    setups = setups.copy()
    setups["date"] = pd.to_datetime(setups["date"]).dt.date
    min_date = setups["date"].min()
    max_date = setups["date"].max()
    controls = st.columns(5)
    setup_filter = controls[0].multiselect(
        "Setup filter",
        options=sorted(setups["best_daily_setup"].dropna().unique()),
        format_func=lambda value: DAILY_SETUP_LABELS.get(value, value),
        key="daily_setup_filter",
    )
    required_horizon = controls[1].selectbox(
        "Require completed forward return",
        options=["None", "1d", "5d", "10d", "20d", "60d"],
        index=2,
        help="Recent candidates do not have longer forward returns yet. Default shows rows with completed 5d outcomes.",
    )
    min_setup_score = controls[2].slider(
        "Minimum setup score",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
        step=0.05,
        help="Higher values make the setup scanner more selective.",
    )
    quick_range = controls[3].selectbox(
        "Quick range",
        options=["All", "Last 1 month", "Last 3 months", "Last 6 months", "Last 1 year", "Custom"],
        index=0,
        key="daily_setup_quick_range",
    )
    default_ranges = {
        "All": (min_date, max_date),
        "Last 1 month": (date_months_back(max_date, 1, min_date), max_date),
        "Last 3 months": (date_months_back(max_date, 3, min_date), max_date),
        "Last 6 months": (date_months_back(max_date, 6, min_date), max_date),
        "Last 1 year": (date_months_back(max_date, 12, min_date), max_date),
        "Custom": (min_date, max_date),
    }
    selected_default_start, selected_default_end = default_ranges[quick_range]
    date_range = controls[4].date_input(
        "Date range",
        value=(selected_default_start, selected_default_end),
        min_value=min_date,
        max_value=max_date,
        key=f"daily_setup_date_range_{quick_range}",
    )
    start_date, end_date = normalize_date_range(date_range, min_date, max_date)
    shown = setups
    if setup_filter:
        shown = shown[shown["best_daily_setup"].isin(setup_filter)]
    shown = shown[shown["best_daily_setup_score"] >= min_setup_score]
    shown = shown[(shown["date"] >= start_date) & (shown["date"] <= end_date)]
    if required_horizon != "None":
        column = f"fwd_return_{required_horizon}"
        if column in shown:
            shown = shown[shown[column].notna()]
    st.caption(
        f"Showing {len(shown):,} candidates from {start_date} to {end_date} after filters. "
        "Table displays the first 500 newest rows."
    )
    st.dataframe(format_daily_setups(shown.head(500)), width="stretch", hide_index=True)

    st.subheader("Setup B Candidate Chart")
    setup_b = shown[shown["best_daily_setup"] == "setup_b_trend_pullback"].copy()
    if setup_b.empty:
        st.info("No Setup B candidates after the current filters. Lower the threshold or widen the date range.")
    else:
        st.markdown("**Setup B Outcomes In Current Filter**")
        outcome_rows = []
        for column, label in [
            ("fwd_return_5d", "5D"),
            ("fwd_return_10d", "10D"),
            ("fwd_return_20d", "20D"),
        ]:
            valid = setup_b[column].dropna() if column in setup_b else pd.Series(dtype=float)
            if valid.empty:
                continue
            outcome_rows.append(
                {
                    "Horizon": label,
                    "Count": int(valid.count()),
                    "Average": pct(valid.mean()),
                    "Median": pct(valid.median()),
                    "Win Rate": pct((valid > 0).mean()),
                }
            )
        if outcome_rows:
            st.dataframe(pd.DataFrame(outcome_rows), width="stretch", hide_index=True)

        chart_controls = st.columns([2, 1])
        setup_b["candidate_label"] = setup_b.apply(
            lambda row: (
                f"{row['date']} | {row['ticker']} | score {row['best_daily_setup_score']:.2f} | "
                f"5d {pct(row.get('fwd_return_5d'))}"
            ),
            axis=1,
        )
        selected_label = chart_controls[0].selectbox(
            "Select Setup B candidate",
            options=setup_b["candidate_label"].head(1000).tolist(),
            key="setup_b_candidate_chart_select",
        )
        window_days = chart_controls[1].slider("Chart window days", 5, 90, 20, 5)
        selected = setup_b[setup_b["candidate_label"] == selected_label].iloc[0]
        st.caption(
            f"{selected['ticker']} on {selected['date']} - {selected.get('daily_setup_explanation', '')}. "
            "Blue dashed line marks the candidate date."
        )
        st.dataframe(format_setup_b_gate_panel(selected), width="stretch", hide_index=True)
        history = load_scored_history()
        if history is None:
            st.info("No scored history file found at `data/features/scored_history.parquet`. Rerun daily mode first.")
        else:
            render_candlestick_with_volume(history, str(selected["ticker"]), selected["date"], window_days)

    setup_b_buckets, setup_b_bucket_path = load_latest(DATA_DIR / "backtests", "setup_b_score_buckets_*.parquet")
    if setup_b_buckets is not None:
        with st.expander("Setup B Score Buckets"):
            st.caption(f"File: {setup_b_bucket_path}")
            st.markdown(
                "This checks whether higher-quality Setup B scores had better forward returns than lower-quality Setup B scores."
            )
            st.dataframe(format_bucket_summary(setup_b_buckets), width="stretch", hide_index=True)

    with st.expander("How daily setup scores work"):
        st.markdown(
            """
            **Setup B - Trend Pullback Continuation**

            Strong 60-day trend, above 50/200 SMA, controlled pullback from recent high, holds 20/50 SMA area,
            volume dries up, and momentum resets without full breakdown.

            **Setup A - Exhaustion Pullback**

            Extended 5-day or 20-day run, stretched above 20 SMA, high relative volume, failed gap/strength,
            and downside reversal.

            **Setup C - Failed Bounce Reversal**

            Weak structure below 20/50 SMA, recent bounce attempt, failed reclaim, downside volume, and not near
            52-week highs.
            """
        )


def render_intraday() -> None:
    st.header("Intraday Setup Candidates")
    st.markdown(
        """
        This table is your playbook scanner. Each row is a 1-minute moment that scored highly for Setup A, B, or C.
        The forward returns are shown for research only: they answer what happened after the candidate appeared.
        """
    )
    intraday, path = load_latest(DATA_DIR / "signals", "intraday_setup_candidates_*.parquet", recursive=True)
    if intraday is None:
        st.info(
            "No intraday candidates found. Run an intraday pull, for example: "
            "`findingalpha --provider massive --tickers SPY QQQ --intraday-only --intraday --intraday-start 2026-05-01 --intraday-timeframe 1Min`."
        )
        return

    provider = path.parent.name if path is not None and path.parent.name != "signals" else "unknown"
    st.caption(f"File: {path}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Candidates", len(intraday))
    col2.metric("Provider", provider)
    col3.metric("Max Setup Score", f"{intraday['best_intraday_setup_score'].max():.2f}")

    setup_filter = st.multiselect(
        "Setup filter",
        options=sorted(intraday["best_intraday_setup"].dropna().unique()),
        format_func=lambda value: SETUP_LABELS.get(value, value),
    )
    shown = intraday
    if setup_filter:
        shown = shown[shown["best_intraday_setup"].isin(setup_filter)]
    st.dataframe(format_intraday(shown.head(500)), width="stretch", hide_index=True)

    with st.expander("How setup scores are calculated"):
        st.markdown(
            """
            **Setup B - Trend Pullback Continuation**

            Price above VWAP, price above 20 EMA, VWAP reclaim, volume spike, and price near VWAP/EMA.

            **Setup A - Exhaustion Pullback**

            Large recent intraday range, volume spike, VWAP loss, and sharp 1-minute downside move.

            **Setup C - Failed Bounce Reversal**

            Price below VWAP, price below 20 EMA, VWAP loss, volume spike, and negative 1-minute return.

            Current setup scores are rule-based prototypes. They are meant to generate research candidates, not trades.
            """
        )


st.set_page_config(page_title="Finding Alpha", layout="wide")
render_sidebar()
st.title("Finding Alpha Research Dashboard")
st.caption("Research-only screener and alpha-testing dashboard. No broker connection, no order placement.")

overview_tab, daily_tab, daily_setup_tab, alpha_tab, intraday_tab = st.tabs(
    ["Overview", "Daily Screener", "Daily Setups", "Alpha Tests", "Intraday Setups"]
)
with overview_tab:
    render_overview()
with daily_tab:
    render_daily()
with daily_setup_tab:
    render_daily_setups()
with alpha_tab:
    render_alpha_tests()
with intraday_tab:
    render_intraday()
