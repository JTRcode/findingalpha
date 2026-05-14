from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from trading_screener.research.setup_eval import add_setup_b_slice_columns_for_dashboard
from trading_screener.signals.daily_playbook import setup_b_condition_audit, setup_b_gate_audit
from trading_screener.signals.scoring import FEATURE_WEIGHTS


DATA_DIR = Path("data")
EARNINGS_PATHS = [
    DATA_DIR / "events" / "earnings.parquet",
    DATA_DIR / "events" / "earnings.csv",
]
SETUP_LABELS = {
    "setup_b_trend_pullback": "Setup B - Trend Pullback Continuation",
    "setup_a_exhaustion": "Prototype A - Exhaustion Pullback",
    "setup_c_failed_bounce": "Prototype C - Failed Bounce Reversal",
}
DAILY_SETUP_LABELS = SETUP_LABELS
PRIMARY_DAILY_SETUP = "setup_b_trend_pullback"


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
    return read_parquet_cached(str(path), path.stat().st_mtime_ns), path


@st.cache_data(show_spinner=False)
def read_parquet_cached(path: str, mtime_ns: int) -> pd.DataFrame:
    return pd.read_parquet(path)


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
            "win_rate_spread": "Win Rate Spread",
            "horizon_days": "Horizon Days",
            "mean_spread": "Mean Spread",
            "median_spread": "Median Spread",
            "top_bucket_mean": "Top Bucket Avg Return",
            "benchmark_mean": "Benchmark Avg Return",
            "spread_t_stat": "Spread T-Stat",
            "t_stat_vs_zero": "T-Stat vs Zero",
            "stderr": "Std Error",
            "std": "Std Dev",
            "interpretation": "Interpretation",
            "slice": "Slice",
            "value": "Value",
            "variant": "Variant",
            "indicator": "Indicator",
            "relative_count": "Benchmark-Relative Observations",
            "relative_mean": "Avg Return vs Benchmark",
            "relative_median": "Median Return vs Benchmark",
            "relative_win_rate": "Win Rate vs Benchmark",
            "benchmark": "Benchmark",
            "absolute_mean": "Avg Forward Return",
            "relative_count": "Benchmark-Relative Observations",
            "date_count": "Dates",
            "candidate_count": "Candidates",
            "avg_candidates_per_date": "Avg Candidates/Date",
            "diagnostic_type": "Diagnostic Type",
            "rule_set": "Rule Set",
            "gate": "Gate",
            "condition": "Condition",
            "rule": "Rule",
            "total_count": "Total Rows",
            "available_count": "Starting Rows",
            "pass_count": "Passing Rows",
            "filtered_out_count": "Filtered Out",
            "unavailable_count": "Unavailable Rows",
            "pass_rate_of_available": "Pass Rate From Prior Step",
            "pass_rate_of_total": "Pass Rate Of Total",
            "step": "Step",
            "gate_order": "Gate Order",
            "condition_order": "Condition Order",
            "date_declustered_absolute_mean": "Date-Declustered Avg Return",
            "date_declustered_relative_mean": "Date-Declustered Avg vs Benchmark",
            "date_declustered_relative_median": "Date-Declustered Median vs Benchmark",
            "date_declustered_relative_win_rate": "Date-Declustered Win Rate vs Benchmark",
            "avg_strict_rate": "Avg Strict Match Rate",
            "trimmed_mean_5_95": "Trimmed Avg Return 5-95%",
            "top_1pct_mean": "Top 1% Avg Return",
            "bottom_1pct_mean": "Bottom 1% Avg Return",
            "top_1pct_return_share": "Top 1% Return Share",
            "bottom_1pct_return_share": "Bottom 1% Return Share",
            "yearly_absolute_mean": "Avg Yearly Return",
            "yearly_relative_mean": "Avg Yearly Return vs Benchmark",
            "yearly_relative_median": "Median Yearly Return vs Benchmark",
            "positive_year_rate": "Positive Year Rate",
            "best_year_relative_mean": "Best Year vs Benchmark",
            "worst_year_relative_mean": "Worst Year vs Benchmark",
        }
    )
    for column in [
        "Avg Forward Return",
        "Median Forward Return",
        "Win Rate",
        "Win Rate Spread",
        "Mean Spread",
        "Median Spread",
        "Top Bucket Avg Return",
        "Benchmark Avg Return",
        "Std Error",
        "Std Dev",
        "Avg Return vs Benchmark",
        "Median Return vs Benchmark",
        "Win Rate vs Benchmark",
        "Date-Declustered Avg Return",
        "Date-Declustered Avg vs Benchmark",
        "Date-Declustered Median vs Benchmark",
        "Date-Declustered Win Rate vs Benchmark",
        "Avg Strict Match Rate",
        "Pass Rate From Prior Step",
        "Pass Rate Of Total",
        "Trimmed Avg Return 5-95%",
        "Top 1% Avg Return",
        "Bottom 1% Avg Return",
        "Top 1% Return Share",
        "Bottom 1% Return Share",
        "Avg Yearly Return",
        "Avg Yearly Return vs Benchmark",
        "Median Yearly Return vs Benchmark",
        "Positive Year Rate",
        "Best Year vs Benchmark",
        "Worst Year vs Benchmark",
    ]:
        if column in out:
            out[column] = out[column].map(pct)
    return out


def summarize_monthly_benchmark_relative(df: pd.DataFrame) -> pd.DataFrame:
    required = {"benchmark", "horizon_days", "group_type", "group_value", "count", "absolute_mean", "relative_mean"}
    if df.empty or not required.issubset(df.columns):
        return pd.DataFrame()

    view = df[(df["group_type"] == "all_setup_b") & (df["group_value"] == "all")].copy()
    if view.empty:
        return pd.DataFrame()

    rows: list[dict[str, object]] = []
    for (benchmark, horizon), group in view.groupby(["benchmark", "horizon_days"], dropna=False):
        observations = float(group["count"].sum())
        if observations <= 0:
            continue
        rows.append(
            {
                "benchmark": benchmark,
                "horizon_days": horizon,
                "count": int(observations),
                "absolute_mean": float((group["absolute_mean"] * group["count"]).sum() / observations),
                "relative_mean": float((group["relative_mean"] * group["count"]).sum() / observations),
                "relative_win_rate": float((group["relative_mean"] > 0).mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["benchmark", "horizon_days"])


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
        "setup_a_exhaustion_score": "Prototype A Score",
        "setup_c_failed_bounce_score": "Prototype C Score",
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
        "momentum_60d": "60D Momentum",
        "pullback_from_10d_high": "Pullback From 10D High",
        "relative_volume": "Rel Volume",
        "rsi_14": "RSI 14",
        "macd_hist": "MACD Hist",
        "adx_14": "ADX 14",
        "accel_5_20": "ROC Accel 5/20",
        "sma20_slope_5d": "20 SMA Slope 5D",
        "linreg_slope_20d": "LinReg Slope 20D",
        "daily_setup_explanation": "Why It Matched",
        "setup_b_variant": "Setup B Variant",
        "setup_b_variant_reason": "Variant Reason",
        "setup_b_scanner_gate": "B Broad Scanner",
        "setup_b_strict_gate": "B Strict Match",
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
    for column in [
        "60D Momentum",
        "Pullback From 10D High",
        "ROC Accel 5/20",
        "20 SMA Slope 5D",
        "LinReg Slope 20D",
        "5D Fwd Return",
        "10D Fwd Return",
        "20D Fwd Return",
    ]:
        if column in out:
            out[column] = out[column].map(pct)
    for column in ["RSI 14", "MACD Hist", "ADX 14"]:
        if column in out:
            out[column] = out[column].map(num)
    if "Close" in out:
        out["Close"] = out["Close"].map(num)
    for column in [
        "B Trend Gate",
        "B Pullback Gate",
        "B Volume Gate",
        "B Structure Gate",
        "B Confirmation Gate",
        "B Broad Scanner",
        "B Strict Match",
    ]:
        if column in out:
            out[column] = out[column].map(lambda value: "PASS" if bool(value) else "FAIL")
    return out


def format_setup_b_gate_panel(row: pd.Series) -> pd.DataFrame:
    return setup_b_gate_audit(row)


def format_setup_b_indicator_panel(row: pd.Series) -> pd.DataFrame:
    indicators = [
        ("RSI 14", "Pullback reset", row.get("rsi_14"), "Neutral/reset zone is often 40-60 after prior strength.", num),
        ("RSI 3D Change", "Momentum turn", row.get("rsi_14_change_3d"), "Positive means RSI is turning up over the last 3 sessions.", num),
        ("RSI Reset Zone", "Pullback reset", row.get("rsi_reset_zone"), "True means RSI is 40-60 after being overbought recently.", lambda value: "YES" if bool(value) else "NO"),
        ("MACD Hist", "Momentum state", row.get("macd_hist"), "Positive is bullish; negative but rising can indicate reset/reversal.", num),
        ("MACD Hist 3D Change", "Momentum turn", row.get("macd_hist_change_3d"), "Positive means MACD histogram is improving.", num),
        ("ADX 14", "Trend strength", row.get("adx_14"), "Above 20-25 suggests stronger trend conditions.", num),
        ("ROC Accel 5/20", "Acceleration", row.get("accel_5_20"), "5D ROC minus 20D ROC scaled to a 5D pace.", pct),
        ("20 SMA Slope 5D", "Trend slope", row.get("sma20_slope_5d"), "Positive means the 20 SMA is rising over 5 sessions.", pct),
        ("LinReg Slope 20D", "Trend slope", row.get("linreg_slope_20d"), "Daily regression slope as a percent of price over 20 sessions.", pct),
    ]
    return pd.DataFrame(
        {
            "Indicator": [name for name, _, _, _, _ in indicators],
            "Role": [role for _, role, _, _, _ in indicators],
            "Value": [formatter(value) for _, _, value, _, formatter in indicators],
            "How To Read": [description for _, _, _, description, _ in indicators],
        }
    )


def load_scored_history() -> pd.DataFrame | None:
    path = DATA_DIR / "features" / "scored_history.parquet"
    if not path.exists():
        return None
    history = read_parquet_cached(str(path), path.stat().st_mtime_ns)
    history["date"] = pd.to_datetime(history["date"]).dt.date
    return history


@st.cache_data(show_spinner=False)
def load_setup_b_context(path: str, mtime_ns: int) -> pd.DataFrame:
    history = pd.read_parquet(path)
    history["date"] = pd.to_datetime(history["date"]).dt.date
    return add_setup_b_slice_columns_for_dashboard(history)


def load_earnings_events() -> pd.DataFrame:
    for path in EARNINGS_PATHS:
        if path.exists():
            raw = read_parquet_cached(str(path), path.stat().st_mtime_ns) if path.suffix == ".parquet" else read_csv_cached(str(path), path.stat().st_mtime_ns)
            return normalize_earnings_events(raw)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def read_csv_cached(path: str, mtime_ns: int) -> pd.DataFrame:
    return pd.read_csv(path)


def normalize_earnings_events(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return raw
    out = raw.copy()
    out.columns = [str(column).strip().lower() for column in out.columns]
    rename = {
        "symbol": "ticker",
        "report_date": "date",
        "earnings_date": "date",
        "epsestimate": "eps_estimate",
        "eps_est": "eps_estimate",
        "epsactual": "eps_actual",
        "eps": "eps_actual",
        "when": "time",
        "session": "time",
    }
    out = out.rename(columns={column: rename[column] for column in rename if column in out.columns})
    if "ticker" not in out or "date" not in out:
        return pd.DataFrame()
    out["ticker"] = out["ticker"].astype(str).str.upper()
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.date
    out = out.dropna(subset=["ticker", "date"])
    if "time" not in out:
        out["time"] = "unknown"
    out["time"] = out["time"].fillna("unknown").astype(str).str.lower()
    return out


def earnings_events_for_chart(earnings: pd.DataFrame, chart_data: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if earnings.empty or chart_data.empty:
        return pd.DataFrame()
    ticker_events = earnings[earnings["ticker"] == ticker.upper()].copy()
    if ticker_events.empty:
        return ticker_events
    min_date = chart_data["date"].min()
    max_date = chart_data["date"].max()
    ticker_events = ticker_events[(ticker_events["date"] >= min_date - timedelta(days=3)) & (ticker_events["date"] <= max_date)]
    if ticker_events.empty:
        return ticker_events

    sessions = chart_data[["date", "session_index", "high"]].sort_values("date").reset_index(drop=True)
    mapped_rows = []
    for _, event in ticker_events.iterrows():
        effective_date = event["date"] + timedelta(days=1) if is_after_close_earnings(event.get("time", "")) else event["date"]
        session = sessions[sessions["date"] >= effective_date].head(1)
        if session.empty:
            continue
        row = event.to_dict()
        row["effective_date"] = effective_date
        row["session_index"] = int(session["session_index"].iloc[0])
        row["marker_y"] = float(session["high"].iloc[0])
        mapped_rows.append(row)
    return pd.DataFrame(mapped_rows)


def is_after_close_earnings(value: object) -> bool:
    text = str(value).lower()
    return any(token in text for token in ["after", "post", "pm", "amc", "close"])


def earnings_hover_text(events: pd.DataFrame) -> list[str]:
    labels = []
    for _, event in events.iterrows():
        parts = [f"Earnings: {event.get('date')}", f"Time: {event.get('time', 'unknown')}"]
        if pd.notna(event.get("eps_actual")):
            parts.append(f"EPS actual: {event.get('eps_actual')}")
        if pd.notna(event.get("eps_estimate")):
            parts.append(f"EPS estimate: {event.get('eps_estimate')}")
        labels.append("<br>".join(parts))
    return labels


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
    earnings = earnings_events_for_chart(load_earnings_events(), chart_data, ticker)

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
    if not earnings.empty:
        fig.add_trace(
            go.Scatter(
                x=earnings["session_index"],
                y=earnings["marker_y"] * 1.015,
                mode="markers",
                marker={
                    "symbol": "triangle-down",
                    "size": 12,
                    "color": "#F59E0B",
                    "line": {"color": "#FDE68A", "width": 1},
                },
                name="Earnings",
                text=earnings_hover_text(earnings),
                hovertemplate="%{text}<extra></extra>",
            ),
            row=1,
            col=1,
        )
        for event_index in earnings["session_index"].dropna().unique():
            fig.add_vline(
                x=int(event_index),
                line_color="#F59E0B",
                line_dash="dot",
                line_width=1,
                opacity=0.8,
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
    st.plotly_chart(fig, width="stretch")
    if earnings.empty:
        st.caption("No earnings events found for this chart window. Add `data/events/earnings.csv` to show markers.")
    else:
        st.dataframe(format_earnings_events(earnings), width="stretch", hide_index=True)


def format_earnings_events(events: pd.DataFrame) -> pd.DataFrame:
    columns = ["date", "effective_date", "time", "eps_actual", "eps_estimate", "revenue_actual", "revenue_estimate"]
    available = [column for column in columns if column in events.columns]
    return events[available].rename(
        columns={
            "date": "Reported Date",
            "effective_date": "Chart Marker Date",
            "time": "Timing",
            "eps_actual": "EPS Actual",
            "eps_estimate": "EPS Estimate",
            "revenue_actual": "Revenue Actual",
            "revenue_estimate": "Revenue Estimate",
        }
    )


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
        st.subheader("Generic Composite Score Benchmark Comparison")
        st.caption(f"File: {benchmark_path}")
        st.markdown(
            """
            This is the older generic alpha test. It takes the highest bucket from the general composite score,
            averages those tickers by date, and compares that daily basket return against SPY or QQQ over the
            same forward window. It is not the Setup B-specific benchmark test.
            """
        )
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Column": "Benchmark",
                        "Meaning": "The comparison asset: SPY or QQQ.",
                    },
                    {
                        "Column": "Horizon Days",
                        "Meaning": "How many trading days forward the test looks.",
                    },
                    {
                        "Column": "Observations",
                        "Meaning": "Number of dates where both the top-score basket and benchmark had forward returns.",
                    },
                    {
                        "Column": "Top Bucket Avg Return",
                        "Meaning": "Average forward return of the highest generic composite-score bucket.",
                    },
                    {
                        "Column": "Benchmark Avg Return",
                        "Meaning": "Average forward return of SPY or QQQ over the same dates.",
                    },
                    {
                        "Column": "Mean Spread",
                        "Meaning": "Top Bucket Avg Return minus Benchmark Avg Return.",
                    },
                    {
                        "Column": "Win Rate vs Benchmark",
                        "Meaning": "Percent of dates where the top bucket beat the benchmark.",
                    },
                ]
            ),
            width="stretch",
            hide_index=True,
        )
        st.dataframe(format_bucket_summary(benchmark), width="stretch", hide_index=True)

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
    st.header("Setup B Research")
    st.markdown(
        """
        This is the main daily playbook workflow: trend pullback continuation candidates, chart review,
        and forward-return diagnostics. Setup A and Setup C are kept as prototypes and hidden by default.
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
    setup_b_total = int((setups["best_daily_setup"] == PRIMARY_DAILY_SETUP).sum()) if "best_daily_setup" in setups else 0
    prototype_total = int((setups["best_daily_setup"] != PRIMARY_DAILY_SETUP).sum()) if "best_daily_setup" in setups else 0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Setup B Candidates", f"{setup_b_total:,}")
    col2.metric("Prototype A/C Rows", f"{prototype_total:,}")
    col3.metric("Tickers", setups["ticker"].nunique() if "ticker" in setups else 0)
    setup_b_scores = setups.loc[setups["best_daily_setup"] == PRIMARY_DAILY_SETUP, "best_daily_setup_score"]
    col4.metric("Max Setup B Score", f"{setup_b_scores.max():.2f}" if not setup_b_scores.empty else "n/a")

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
    show_prototypes = controls[0].checkbox(
        "Show prototype A/C",
        value=False,
        help="Setup A and Setup C are experimental labels. Keep this off for the main Setup B workflow.",
        key="daily_setup_show_prototypes",
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
        value=0.60,
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
    shown = setups if show_prototypes else setups[setups["best_daily_setup"] == PRIMARY_DAILY_SETUP]
    shown = shown[shown["best_daily_setup_score"] >= min_setup_score]
    shown = shown[(shown["date"] >= start_date) & (shown["date"] <= end_date)]
    if required_horizon != "None":
        column = f"fwd_return_{required_horizon}"
        if column in shown:
            shown = shown[shown[column].notna()]
    st.caption(
        f"Showing {len(shown):,} {'daily setup' if show_prototypes else 'Setup B'} candidates "
        f"from {start_date} to {end_date} after filters. "
        "Table displays the first 500 newest rows."
    )
    if show_prototypes:
        st.info("Prototype A/C rows are shown for research context only. The active daily research setup is still Setup B.")
    st.dataframe(format_daily_setups(shown.head(500)), width="stretch", hide_index=True)

    st.subheader("Setup B Candidate Chart")
    setup_b = shown[shown["best_daily_setup"] == PRIMARY_DAILY_SETUP].copy()
    if setup_b.empty:
        st.info("No Setup B candidates after the current filters. Lower the threshold or widen the date range.")
    else:
        scored_history_path = DATA_DIR / "features" / "scored_history.parquet"
        if scored_history_path.exists():
            slice_columns = [
                "ticker",
                "date",
                "market_regime",
                "pullback_depth_slice",
                "pullback_duration_slice",
                "volume_dryup_slice",
                "trend_strength_slice",
                "confirmation_quality_slice",
                "atr_slice",
                "setup_b_variant",
                "setup_b_variant_reason",
            ]
            slice_frame = load_setup_b_context(str(scored_history_path), scored_history_path.stat().st_mtime_ns)
            available_slice_columns = [column for column in slice_columns if column in slice_frame.columns]
            setup_b = setup_b.merge(
                slice_frame[available_slice_columns],
                on=["ticker", "date"],
                how="left",
                suffixes=("", "_slice_context"),
            )
            filter_columns = st.columns(4)
            atr_options = sorted(setup_b["atr_slice"].dropna().astype(str).unique()) if "atr_slice" in setup_b else []
            confirmation_options = (
                sorted(setup_b["confirmation_quality_slice"].dropna().astype(str).unique())
                if "confirmation_quality_slice" in setup_b
                else []
            )
            regime_options = sorted(setup_b["market_regime"].dropna().astype(str).unique()) if "market_regime" in setup_b else []
            variant_options = sorted(setup_b["setup_b_variant"].dropna().astype(str).unique()) if "setup_b_variant" in setup_b else []
            selected_atr = filter_columns[0].multiselect("ATR slice", atr_options, key="setup_b_atr_filter")
            selected_confirmation = filter_columns[1].multiselect(
                "Confirmation slice", confirmation_options, key="setup_b_confirmation_filter"
            )
            selected_regime = filter_columns[2].multiselect("Market regime", regime_options, key="setup_b_regime_filter")
            selected_variant = filter_columns[3].multiselect("Setup B variant", variant_options, key="setup_b_variant_filter")
            if selected_atr:
                setup_b = setup_b[setup_b["atr_slice"].astype(str).isin(selected_atr)]
            if selected_confirmation:
                setup_b = setup_b[setup_b["confirmation_quality_slice"].astype(str).isin(selected_confirmation)]
            if selected_regime:
                setup_b = setup_b[setup_b["market_regime"].astype(str).isin(selected_regime)]
            if selected_variant:
                setup_b = setup_b[setup_b["setup_b_variant"].astype(str).isin(selected_variant)]

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

        if setup_b.empty:
            st.info("No Setup B candidates after applying slice filters.")
        else:
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
            if selected.get("setup_b_variant"):
                st.caption(f"Variant: {selected.get('setup_b_variant')} - {selected.get('setup_b_variant_reason', '')}")
            st.markdown("**Setup B Gate Summary**")
            st.dataframe(format_setup_b_gate_panel(selected), width="stretch", hide_index=True)
            with st.expander("Momentum / Reset Indicator Diagnostics", expanded=True):
                st.markdown(
                    """
                    These indicators are diagnostic only. They do not admit, reject, or score Setup B v1 candidates.
                    Use them to judge whether a candidate has trend acceleration, momentum reset, or improving momentum.
                    """
                )
                st.dataframe(format_setup_b_indicator_panel(selected), width="stretch", hide_index=True)
            with st.expander("Debug Setup B Conditions", expanded=True):
                st.markdown(
                    """
                    This audit shows the raw feature values beside the broad and strict thresholds. Use it to find
                    which condition is too loose, too strict, or not measuring the chart behavior you expected.
                    """
                )
                st.dataframe(setup_b_condition_audit(selected), width="stretch", hide_index=True)
            history = load_scored_history()
            if history is None:
                st.info("No scored history file found at `data/features/scored_history.parquet`. Rerun daily mode first.")
            else:
                render_candlestick_with_volume(history, str(selected["ticker"]), selected["date"], window_days)

    setup_b_buckets, setup_b_bucket_path = load_latest(DATA_DIR / "backtests", "setup_b_score_buckets_*.parquet")
    if setup_b_buckets is not None:
        with st.expander("Setup B Score Buckets", expanded=True):
            st.caption(f"File: {setup_b_bucket_path}")
            st.markdown(
                "This checks whether higher-quality Setup B scores had better forward returns than lower-quality Setup B scores."
            )
            st.dataframe(format_bucket_summary(setup_b_buckets), width="stretch", hide_index=True)

    setup_b_filter_diag, setup_b_filter_diag_path = load_latest(
        DATA_DIR / "backtests", "setup_b_filter_diagnostics_*.parquet"
    )
    if setup_b_filter_diag is not None:
        with st.expander("Setup B Filter Diagnostics", expanded=True):
            st.caption(f"File: {setup_b_filter_diag_path}")
            st.markdown(
                """
                Independent condition counts show how many rows pass each rule by itself. The cumulative funnel
                applies gate groups in order, so overlaps are counted only after earlier gates have already passed.
                """
            )
            diag_type = st.selectbox(
                "Diagnostic view",
                options=["cumulative_funnel", "independent_condition", "final_gate"],
                format_func=lambda value: {
                    "cumulative_funnel": "Cumulative funnel",
                    "independent_condition": "Independent condition counts",
                    "final_gate": "Final broad/strict totals",
                }.get(value, value),
                key="setup_b_filter_diag_type",
            )
            rule_set = st.selectbox(
                "Rule set",
                options=sorted(setup_b_filter_diag["rule_set"].dropna().unique()),
                key="setup_b_filter_diag_rule_set",
            )
            filter_view = setup_b_filter_diag[
                (setup_b_filter_diag["diagnostic_type"] == diag_type)
                & (setup_b_filter_diag["rule_set"] == rule_set)
            ].copy()
            sort_columns = (
                ["step"]
                if diag_type == "cumulative_funnel" and "step" in filter_view
                else [column for column in ["gate_order", "condition_order", "gate", "condition"] if column in filter_view]
            )
            filter_view = filter_view.sort_values(sort_columns)
            hidden_order_columns = [column for column in ["gate_order", "condition_order"] if column in filter_view]
            st.dataframe(
                format_bucket_summary(filter_view.drop(columns=hidden_order_columns)),
                width="stretch",
                hide_index=True,
            )

    setup_b_indicator_diag, setup_b_indicator_diag_path = load_latest(
        DATA_DIR / "backtests", "setup_b_indicator_diagnostics_*.parquet"
    )
    if setup_b_indicator_diag is not None:
        with st.expander("Setup B Indicator Diagnostics", expanded=False):
            st.caption(f"File: {setup_b_indicator_diag_path}")
            st.markdown(
                """
                These diagnostics test RSI, MACD, ADX, ROC acceleration, and slope features inside existing Setup B
                candidates. They are not Setup B filters yet.
                """
            )
            indicator = st.selectbox(
                "Indicator",
                options=sorted(setup_b_indicator_diag["indicator"].dropna().unique()),
                key="setup_b_indicator_diag_indicator",
            )
            indicator_horizon = st.selectbox(
                "Indicator horizon",
                options=sorted(setup_b_indicator_diag["horizon_days"].dropna().unique()),
                index=1 if len(setup_b_indicator_diag["horizon_days"].dropna().unique()) > 1 else 0,
                key="setup_b_indicator_diag_horizon",
            )
            indicator_view = setup_b_indicator_diag[
                (setup_b_indicator_diag["indicator"] == indicator)
                & (setup_b_indicator_diag["horizon_days"] == indicator_horizon)
            ].sort_values("mean", ascending=False)
            st.dataframe(format_bucket_summary(indicator_view), width="stretch", hide_index=True)

    setup_b_diag, setup_b_diag_path = load_latest(DATA_DIR / "backtests", "setup_b_bucket_diagnostics_*.parquet")
    setup_b_spreads, setup_b_spreads_path = load_latest(DATA_DIR / "backtests", "setup_b_top_bottom_spreads_*.parquet")
    if setup_b_diag is not None or setup_b_spreads is not None:
        with st.expander("Setup B Bucket Diagnostics", expanded=True):
            st.markdown(
                """
                Diagnostics help judge whether score improvements are meaningful. Look for rising mean/median returns,
                rising win rates, positive top-bottom spreads, and spread t-stats around 2 or higher.
                """
            )
            if setup_b_spreads is not None:
                st.caption(f"Top-bottom spreads: {setup_b_spreads_path}")
                st.dataframe(format_bucket_summary(setup_b_spreads), width="stretch", hide_index=True)
            if setup_b_diag is not None:
                st.caption(f"Bucket diagnostics: {setup_b_diag_path}")
                st.dataframe(format_bucket_summary(setup_b_diag), width="stretch", hide_index=True)

    setup_b_slices, setup_b_slices_path = load_latest(DATA_DIR / "backtests", "setup_b_slices_*.parquet")
    if setup_b_slices is not None:
        with st.expander("Setup B Slice Results", expanded=False):
            st.caption(f"File: {setup_b_slices_path}")
            st.markdown(
                """
                Slices split Setup B candidates into conditions such as market regime, pullback depth, volume dry-up,
                trend strength, confirmation quality, and volatility. Use this to find where the setup works or fails.
                """
            )
            slice_names = sorted(setup_b_slices["slice"].dropna().unique())
            selected_slice = st.selectbox("Slice", options=slice_names, key="setup_b_slice_select")
            selected_horizon = st.selectbox(
                "Horizon",
                options=sorted(setup_b_slices["horizon_days"].dropna().unique()),
                index=1 if len(setup_b_slices["horizon_days"].dropna().unique()) > 1 else 0,
                key="setup_b_slice_horizon",
            )
            slice_view = setup_b_slices[
                (setup_b_slices["slice"] == selected_slice)
                & (setup_b_slices["horizon_days"] == selected_horizon)
            ].sort_values("mean", ascending=False)
            st.dataframe(format_bucket_summary(slice_view), width="stretch", hide_index=True)

    setup_b_interactions, setup_b_interactions_path = load_latest(
        DATA_DIR / "backtests", "setup_b_interaction_slices_*.parquet"
    )
    if setup_b_interactions is not None:
        with st.expander("Setup B Interaction Slices", expanded=False):
            st.caption(f"File: {setup_b_interactions_path}")
            st.markdown("Interaction slices test two conditions at once, such as market regime plus confirmation quality.")
            interaction_pairs = sorted(setup_b_interactions["interaction_pair"].dropna().unique())
            selected_pair = st.selectbox("Interaction pair", options=interaction_pairs, key="setup_b_interaction_pair")
            selected_interaction_horizon = st.selectbox(
                "Interaction horizon",
                options=sorted(setup_b_interactions["horizon_days"].dropna().unique()),
                index=1 if len(setup_b_interactions["horizon_days"].dropna().unique()) > 1 else 0,
                key="setup_b_interaction_horizon",
            )
            interaction_view = setup_b_interactions[
                (setup_b_interactions["interaction_pair"] == selected_pair)
                & (setup_b_interactions["horizon_days"] == selected_interaction_horizon)
            ].sort_values("mean", ascending=False)
            st.dataframe(format_bucket_summary(interaction_view), width="stretch", hide_index=True)

    setup_b_variants, setup_b_variants_path = load_latest(DATA_DIR / "backtests", "setup_b_variants_*.parquet")
    if setup_b_variants is not None:
        with st.expander("Setup B Variants", expanded=False):
            st.caption(f"File: {setup_b_variants_path}")
            st.markdown(
                """
                Variants are stricter research labels layered on top of Setup B. They test whether cleaner subsets
                behave better than the broad Setup B scanner. Benchmark-relative columns subtract SPY forward returns
                on the same dates when SPY is available.
                """
            )
            variant_horizon = st.selectbox(
                "Variant horizon",
                options=sorted(setup_b_variants["horizon_days"].dropna().unique()),
                index=1 if len(setup_b_variants["horizon_days"].dropna().unique()) > 1 else 0,
                key="setup_b_variant_horizon",
            )
            variant_view = setup_b_variants[setup_b_variants["horizon_days"] == variant_horizon]
            sort_columns = [column for column in ["relative_mean", "mean"] if column in variant_view.columns]
            if sort_columns:
                variant_view = variant_view.sort_values(sort_columns, ascending=False, na_position="last")
            st.dataframe(format_bucket_summary(variant_view), width="stretch", hide_index=True)

    setup_b_regime, setup_b_regime_path = load_latest(DATA_DIR / "backtests", "setup_b_market_regime_*.parquet")
    setup_b_regime_monthly, setup_b_regime_monthly_path = load_latest(
        DATA_DIR / "backtests", "setup_b_market_regime_monthly_*.parquet"
    )
    if setup_b_regime is not None or setup_b_regime_monthly is not None:
        with st.expander("Setup B Market Regime Diagnostics", expanded=False):
            st.markdown(
                """
                Market regime diagnostics compare Setup B candidates in positive SPY/QQQ conditions versus weak or
                choppy benchmark conditions. Absolute returns can look good in weak regimes if the market rebounds;
                benchmark-relative returns show whether candidates beat SPY on the same dates.
                """
            )
            if setup_b_regime is not None:
                st.caption(f"Summary file: {setup_b_regime_path}")
                regime_horizon = st.selectbox(
                    "Regime horizon",
                    options=sorted(setup_b_regime["horizon_days"].dropna().unique()),
                    index=1 if len(setup_b_regime["horizon_days"].dropna().unique()) > 1 else 0,
                    key="setup_b_regime_horizon",
                )
                regime_view = setup_b_regime[setup_b_regime["horizon_days"] == regime_horizon].sort_values(
                    "relative_mean" if "relative_mean" in setup_b_regime.columns else "mean",
                    ascending=False,
                    na_position="last",
                )
                st.dataframe(format_bucket_summary(regime_view), width="stretch", hide_index=True)
            if setup_b_regime_monthly is not None:
                st.caption(f"Monthly file: {setup_b_regime_monthly_path}")
                monthly_horizon = st.selectbox(
                    "Monthly horizon",
                    options=sorted(setup_b_regime_monthly["horizon_days"].dropna().unique()),
                    index=1 if len(setup_b_regime_monthly["horizon_days"].dropna().unique()) > 1 else 0,
                    key="setup_b_regime_monthly_horizon",
                )
                monthly_view = setup_b_regime_monthly[
                    setup_b_regime_monthly["horizon_days"] == monthly_horizon
                ].sort_values(["month", "market_regime"], ascending=[False, True])
                st.dataframe(format_bucket_summary(monthly_view.head(36)), width="stretch", hide_index=True)

    setup_b_relative_monthly, setup_b_relative_monthly_path = load_latest(
        DATA_DIR / "backtests", "setup_b_benchmark_relative_monthly_*.parquet"
    )
    setup_b_date_declustered, setup_b_date_declustered_path = load_latest(
        DATA_DIR / "backtests", "setup_b_date_declustered_*.parquet"
    )
    setup_b_sector_declustered, setup_b_sector_declustered_path = load_latest(
        DATA_DIR / "backtests", "setup_b_sector_declustered_*.parquet"
    )
    setup_b_outliers, setup_b_outliers_path = load_latest(
        DATA_DIR / "backtests", "setup_b_outlier_diagnostics_*.parquet"
    )
    setup_b_consistency, setup_b_consistency_path = load_latest(
        DATA_DIR / "backtests", "setup_b_time_consistency_*.parquet"
    )
    if setup_b_relative_monthly is not None or setup_b_date_declustered is not None:
        with st.expander("Setup B Benchmark/Declustering Diagnostics", expanded=False):
            st.markdown(
                """
                These diagnostics test whether Setup B groups still look useful after comparing to SPY/QQQ and
                after giving each trading date equal weight. This helps separate potential alpha from rebound beta
                and candidate clustering on a few busy dates.
                """
            )
            if setup_b_date_declustered is not None:
                st.caption(f"Date-declustered file: {setup_b_date_declustered_path}")
                decluster_cols = st.columns(3)
                decluster_benchmark = decluster_cols[0].selectbox(
                    "Decluster benchmark",
                    options=sorted(setup_b_date_declustered["benchmark"].dropna().unique()),
                    key="setup_b_decluster_benchmark",
                )
                decluster_horizon = decluster_cols[1].selectbox(
                    "Decluster horizon",
                    options=sorted(setup_b_date_declustered["horizon_days"].dropna().unique()),
                    index=1 if len(setup_b_date_declustered["horizon_days"].dropna().unique()) > 1 else 0,
                    key="setup_b_decluster_horizon",
                )
                decluster_group = decluster_cols[2].selectbox(
                    "Decluster group",
                    options=sorted(setup_b_date_declustered["group_type"].dropna().unique()),
                    key="setup_b_decluster_group",
                )
                decluster_view = setup_b_date_declustered[
                    (setup_b_date_declustered["benchmark"] == decluster_benchmark)
                    & (setup_b_date_declustered["horizon_days"] == decluster_horizon)
                    & (setup_b_date_declustered["group_type"] == decluster_group)
                ].sort_values("date_declustered_relative_mean", ascending=False)
                st.dataframe(format_bucket_summary(decluster_view), width="stretch", hide_index=True)
            if setup_b_relative_monthly is not None:
                st.caption(f"Monthly benchmark-relative file: {setup_b_relative_monthly_path}")
                st.markdown("**How to read benchmark-relative columns**")
                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "Column": "Benchmark",
                                "Meaning": "The comparison asset, usually SPY or QQQ.",
                            },
                            {
                                "Column": "Horizon Days",
                                "Meaning": "How many trading days forward the test looks.",
                            },
                            {
                                "Column": "Avg Forward Return",
                                "Meaning": "Average raw return after the Setup B signal.",
                            },
                            {
                                "Column": "Avg Return vs Benchmark",
                                "Meaning": "Average Setup B return minus benchmark return over the same dates.",
                            },
                            {
                                "Column": "Win Rate vs Benchmark",
                                "Meaning": "Percent of rows or months where Setup B beat the benchmark.",
                            },
                        ]
                    ),
                    width="stretch",
                    hide_index=True,
                )
                monthly_summary = summarize_monthly_benchmark_relative(setup_b_relative_monthly)
                if not monthly_summary.empty:
                    st.markdown("**Aggregate benchmark-relative summary: all Setup B candidates**")
                    st.dataframe(format_bucket_summary(monthly_summary), width="stretch", hide_index=True)
                monthly_cols = st.columns(4)
                monthly_benchmark = monthly_cols[0].selectbox(
                    "Monthly benchmark",
                    options=sorted(setup_b_relative_monthly["benchmark"].dropna().unique()),
                    key="setup_b_relative_monthly_benchmark",
                )
                monthly_relative_horizon = monthly_cols[1].selectbox(
                    "Monthly relative horizon",
                    options=sorted(setup_b_relative_monthly["horizon_days"].dropna().unique()),
                    index=1 if len(setup_b_relative_monthly["horizon_days"].dropna().unique()) > 1 else 0,
                    key="setup_b_relative_monthly_horizon",
                )
                monthly_group = monthly_cols[2].selectbox(
                    "Monthly group",
                    options=sorted(setup_b_relative_monthly["group_type"].dropna().unique()),
                    key="setup_b_relative_monthly_group",
                )
                monthly_value_options = sorted(
                    setup_b_relative_monthly[setup_b_relative_monthly["group_type"] == monthly_group]["group_value"]
                    .dropna()
                    .unique()
                )
                monthly_value = monthly_cols[3].selectbox(
                    "Monthly value",
                    options=monthly_value_options,
                    key="setup_b_relative_monthly_value",
                )
                relative_monthly_view = setup_b_relative_monthly[
                    (setup_b_relative_monthly["benchmark"] == monthly_benchmark)
                    & (setup_b_relative_monthly["horizon_days"] == monthly_relative_horizon)
                    & (setup_b_relative_monthly["group_type"] == monthly_group)
                    & (setup_b_relative_monthly["group_value"] == monthly_value)
                ].sort_values("month", ascending=False)
                st.dataframe(format_bucket_summary(relative_monthly_view.head(36)), width="stretch", hide_index=True)
            if setup_b_sector_declustered is not None:
                st.caption(f"Sector de-clustered file: {setup_b_sector_declustered_path}")
                st.dataframe(setup_b_sector_declustered, width="stretch", hide_index=True)
            if setup_b_outliers is not None:
                st.caption(f"Outlier diagnostics file: {setup_b_outliers_path}")
                st.markdown(
                    """
                    Outlier diagnostics check whether a slice's mean return is driven by a few very large winners
                    or losers. Compare the raw average with the 5-95% trimmed average and the top 1% return share.
                    """
                )
                outlier_cols = st.columns(3)
                outlier_group = outlier_cols[0].selectbox(
                    "Outlier group",
                    options=sorted(setup_b_outliers["group_type"].dropna().unique()),
                    key="setup_b_outlier_group",
                )
                outlier_horizon = outlier_cols[1].selectbox(
                    "Outlier horizon",
                    options=sorted(setup_b_outliers["horizon_days"].dropna().unique()),
                    index=3 if len(setup_b_outliers["horizon_days"].dropna().unique()) > 3 else 0,
                    key="setup_b_outlier_horizon",
                )
                min_outlier_count = outlier_cols[2].number_input(
                    "Min observations",
                    min_value=0,
                    max_value=1000000,
                    value=1000,
                    step=500,
                    key="setup_b_outlier_min_count",
                )
                outlier_view = setup_b_outliers[
                    (setup_b_outliers["group_type"] == outlier_group)
                    & (setup_b_outliers["horizon_days"] == outlier_horizon)
                    & (setup_b_outliers["count"] >= min_outlier_count)
                ].sort_values("mean", ascending=False)
                st.dataframe(format_bucket_summary(outlier_view), width="stretch", hide_index=True)
            if setup_b_consistency is not None:
                st.caption(f"Time consistency file: {setup_b_consistency_path}")
                st.markdown(
                    """
                    Time consistency checks whether a slice beats SPY/QQQ across years, rather than only in one
                    strong period. Higher positive-year rate is more robust than one high average.
                    """
                )
                consistency_cols = st.columns(4)
                consistency_benchmark = consistency_cols[0].selectbox(
                    "Consistency benchmark",
                    options=sorted(setup_b_consistency["benchmark"].dropna().unique()),
                    key="setup_b_consistency_benchmark",
                )
                consistency_horizon = consistency_cols[1].selectbox(
                    "Consistency horizon",
                    options=sorted(setup_b_consistency["horizon_days"].dropna().unique()),
                    index=3 if len(setup_b_consistency["horizon_days"].dropna().unique()) > 3 else 0,
                    key="setup_b_consistency_horizon",
                )
                consistency_group = consistency_cols[2].selectbox(
                    "Consistency group",
                    options=sorted(setup_b_consistency["group_type"].dropna().unique()),
                    key="setup_b_consistency_group",
                )
                min_years = consistency_cols[3].number_input(
                    "Min years",
                    min_value=1,
                    max_value=100,
                    value=5,
                    step=1,
                    key="setup_b_consistency_min_years",
                )
                consistency_view = setup_b_consistency[
                    (setup_b_consistency["benchmark"] == consistency_benchmark)
                    & (setup_b_consistency["horizon_days"] == consistency_horizon)
                    & (setup_b_consistency["group_type"] == consistency_group)
                    & (setup_b_consistency["years"] >= min_years)
                ].sort_values(["positive_year_rate", "yearly_relative_mean"], ascending=False)
                st.dataframe(format_bucket_summary(consistency_view), width="stretch", hide_index=True)

    with st.expander("How Setup B v1 works"):
        st.markdown(
            """
            **Setup B - Trend Pullback Continuation**

            Strong 60-day trend, above 50/200 SMA, controlled pullback from recent high, holds 20/50 SMA area,
            volume dries up, and momentum resets without full breakdown.

            The broad scanner creates the research sample. The strict match and gate table show whether the cleaner
            discretionary version passed. The Setup B score ranks broad candidates for bucket testing.
            """
        )

    with st.expander("Prototype setup labels"):
        st.markdown(
            """
            Setup A and Setup C are retained as prototype labels only. They are hidden by default so the daily
            dashboard stays focused on Setup B.

            **Prototype A - Exhaustion Pullback**

            Extended 5-day or 20-day run, stretched above 20 SMA, high relative volume, failed gap/strength,
            and downside reversal.

            **Prototype C - Failed Bounce Reversal**

            Weak structure below 20/50 SMA, recent bounce attempt, failed reclaim, downside volume, and not near
            52-week highs.
            """
        )


def render_intraday() -> None:
    st.header("Intraday Prototypes")
    st.markdown(
        """
        This is an experimental intraday research layer. Each row is a 1-minute prototype candidate. Keep this
        separate from the main daily Setup B workflow until intraday data coverage and rules are stable.
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

            **Prototype A - Exhaustion Pullback**

            Large recent intraday range, volume spike, VWAP loss, and sharp 1-minute downside move.

            **Prototype C - Failed Bounce Reversal**

            Price below VWAP, price below 20 EMA, VWAP loss, volume spike, and negative 1-minute return.

            Current setup scores are rule-based prototypes. They are meant to generate research candidates, not trades.
            """
        )


st.set_page_config(page_title="Finding Alpha", layout="wide")
render_sidebar()
st.title("Finding Alpha Research Dashboard")
st.caption("Research-only screener and alpha-testing dashboard. No broker connection, no order placement.")

overview_tab, daily_tab, daily_setup_tab, alpha_tab, intraday_tab = st.tabs(
    ["Overview", "Daily Screener", "Setup B Research", "Alpha Tests", "Intraday Prototypes"]
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
