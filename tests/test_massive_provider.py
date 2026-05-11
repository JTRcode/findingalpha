from __future__ import annotations

from trading_screener.data.providers.massive_provider import MassiveMarketDataProvider, _parse_timeframe


def test_massive_provider_parses_aggregate_bars() -> None:
    provider = MassiveMarketDataProvider(api_key="key")

    def fake_get_json(url: str) -> dict[str, object]:
        assert "apiKey=key" in url
        return {
            "results": [
                {
                    "t": 1_714_565_400_000,
                    "o": 100,
                    "h": 101,
                    "l": 99,
                    "c": 100.5,
                    "v": 123456,
                    "n": 1200,
                    "vw": 100.25,
                }
            ]
        }

    provider._get_json = fake_get_json  # type: ignore[method-assign]
    bars = provider.fetch_intraday_bars(["SPY"], start="2024-05-01", end="2024-05-02", timeframe="1Min")

    assert len(bars) == 1
    assert bars.iloc[0]["ticker"] == "SPY"
    assert bars.iloc[0]["provider"] == "massive"
    assert bars.iloc[0]["feed"] == "consolidated"


def test_parse_timeframe() -> None:
    assert _parse_timeframe("1Min") == (1, "minute")
    assert _parse_timeframe("5Min") == (5, "minute")
    assert _parse_timeframe("1Day") == (1, "day")
