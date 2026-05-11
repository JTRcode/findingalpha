from __future__ import annotations

import pytest
import pandas as pd

from tests.test_features import sample_bars
from tests.test_intraday import sample_intraday_bars
from trading_screener.data.validation import validate_daily_bars, validate_intraday_bars


def test_validate_daily_bars_accepts_clean_data() -> None:
    validate_daily_bars(sample_bars())


def test_validate_daily_bars_rejects_duplicates() -> None:
    bars = sample_bars()
    duplicated = bars.iloc[[0]]
    bad = pd.concat([bars, duplicated], ignore_index=True)

    with pytest.raises(ValueError, match="Duplicate"):
        validate_daily_bars(bad)


def test_validate_intraday_bars_accepts_clean_data() -> None:
    validate_intraday_bars(sample_intraday_bars())
