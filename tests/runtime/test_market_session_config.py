from datetime import time

import pytest

from imie.runtime import (
    MarketSessionConfig,
)


def test_default_configuration() -> None:
    config = MarketSessionConfig()

    assert (
        config.market_timezone
        == "America/New_York"
    )
    assert config.premarket_start == time(
        4,
        0,
    )
    assert config.regular_start == time(
        9,
        30,
    )
    assert config.regular_end == time(
        16,
        0,
    )
    assert config.after_hours_end == time(
        20,
        0,
    )
    assert config.weekdays == (
        0,
        1,
        2,
        3,
        4,
    )


def test_timezone_is_available() -> None:
    config = MarketSessionConfig()

    assert (
        config.timezone.key
        == "America/New_York"
    )


def test_timezone_is_trimmed() -> None:
    config = MarketSessionConfig(
        market_timezone=" America/New_York ",
    )

    assert (
        config.market_timezone
        == "America/New_York"
    )


def test_invalid_timezone_raises() -> None:
    with pytest.raises(
        ValueError,
        match="market_timezone",
    ):
        MarketSessionConfig(
            market_timezone="Invalid/Timezone",
        )


def test_session_boundaries_must_be_ordered() -> None:
    with pytest.raises(
        ValueError,
        match="boundaries",
    ):
        MarketSessionConfig(
            regular_start=time(
                16,
                0,
            ),
            regular_end=time(
                9,
                30,
            ),
        )


def test_weekdays_are_deduplicated() -> None:
    config = MarketSessionConfig(
        weekdays=(
            0,
            1,
            1,
            2,
        ),
    )

    assert config.weekdays == (
        0,
        1,
        2,
    )


def test_weekdays_cannot_be_empty() -> None:
    with pytest.raises(
        ValueError,
        match="weekdays",
    ):
        MarketSessionConfig(
            weekdays=(),
        )


@pytest.mark.parametrize(
    "weekday",
    [
        -1,
        7,
    ],
)
def test_weekday_must_be_valid(
    weekday: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="weekday",
    ):
        MarketSessionConfig(
            weekdays=(
                weekday,
            ),
        )