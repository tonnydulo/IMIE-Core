from imie.providers.mock_provider import (
    MockProvider,
)
from datetime import (
    UTC,
    datetime,
    timedelta,
)


def test_mock_provider_timestamps_are_timezone_aware() -> None:
    provider = MockProvider()

    connected = provider.connect()
    quote = provider.get_quote(
        "NVDA"
    )
    bars = provider.get_bars(
        "NVDA",
        "2m",
        limit=3,
    )
    disconnected = provider.disconnect()

    assert connected.timestamp.tzinfo is not None
    assert quote.timestamp.tzinfo is not None
    assert disconnected.timestamp.tzinfo is not None

    assert bars

    for bar in bars:
        assert bar.timestamp.tzinfo is not None

def test_mock_provider_bars_are_aligned_to_timeframe() -> None:
    provider = MockProvider()

    bars = provider.get_bars(
        "NVDA",
        "2m",
        limit=3,
    )

    assert len(
        bars
    ) == 3

    for bar in bars:
        assert bar.timestamp.second == 0
        assert bar.timestamp.microsecond == 0
        assert bar.timestamp.minute % 2 == 0

def test_mock_provider_latest_bar_is_safely_historical() -> None:
    provider = MockProvider()

    bars = provider.get_bars(
        "NVDA",
        "2m",
        limit=3,
    )

    now = datetime.now(
        UTC
    )

    assert (
        bars[-1].timestamp
        + timedelta(
            minutes=2,
        )
        < now
    )
