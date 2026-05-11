from __future__ import annotations

from trading_screener.data.providers.alpaca_provider import AlpacaMarketDataProvider


def test_alpaca_provider_parses_intraday_bars() -> None:
    provider = AlpacaMarketDataProvider(key_id="key", secret_key="secret")

    def fake_get_json(url: str) -> dict[str, object]:
        assert "timeframe=1Min" in url
        return {
            "bars": {
                "SPY": [
                    {
                        "t": "2026-05-01T13:30:00Z",
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
        }

    provider._get_json = fake_get_json  # type: ignore[method-assign]
    bars = provider.fetch_intraday_bars(["SPY"], start="2026-05-01", timeframe="1Min", feed="iex")

    assert len(bars) == 1
    assert bars.iloc[0]["ticker"] == "SPY"
    assert bars.iloc[0]["volume"] == 123456
