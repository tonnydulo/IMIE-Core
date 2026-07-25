import pytest

from imie.runtime import RuntimeConfig


def test_defaults() -> None:
    config = RuntimeConfig()

    assert config.symbol == "NVDA"
    assert config.timeframe == "2m"
    assert config.timeframe_minutes == 2
    assert config.bar_limit == 500
    assert config.polling_interval_seconds == 5.0
    assert config.completion_delay_seconds == 3.0
    assert config.require_new_completed_bar is True
    assert (
        config.closed_session_polling_interval_seconds
        == 300.0
    )
    assert config.heartbeat_interval_seconds == 60.0


def test_symbol_and_timeframe_are_normalized() -> None:
    config = RuntimeConfig(
        symbol=" spy ",
        timeframe="5M",
    )

    assert config.symbol == "SPY"
    assert config.timeframe == "5m"
    assert config.timeframe_minutes == 5


@pytest.mark.parametrize(
    "timeframe",
    [
        "",
        "3m",
        "1h",
        "daily",
    ],
)
def test_invalid_timeframe_raises(
    timeframe: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="timeframe",
    ):
        RuntimeConfig(
            timeframe=timeframe,
        )


def test_invalid_symbol_raises() -> None:
    with pytest.raises(
        ValueError,
        match="symbol",
    ):
        RuntimeConfig(
            symbol=" ",
        )


def test_bar_limit_must_be_positive() -> None:
    with pytest.raises(
        ValueError,
        match="bar_limit",
    ):
        RuntimeConfig(
            bar_limit=0,
        )


def test_polling_interval_must_be_positive() -> None:
    with pytest.raises(
        ValueError,
        match="polling_interval_seconds",
    ):
        RuntimeConfig(
            polling_interval_seconds=0.0,
        )


def test_completion_delay_can_be_zero() -> None:
    config = RuntimeConfig(
        completion_delay_seconds=0.0,
    )

    assert config.completion_delay_seconds == 0.0


def test_completion_delay_cannot_be_negative() -> None:
    with pytest.raises(
        ValueError,
        match="completion_delay_seconds",
    ):
        RuntimeConfig(
            completion_delay_seconds=-1.0,
        )

def test_closed_session_polling_interval_is_normalized() -> None:
    config = RuntimeConfig(
        closed_session_polling_interval_seconds=120,
    )

    assert (
        config.closed_session_polling_interval_seconds
        == 120.0
    )
    assert isinstance(
        config.closed_session_polling_interval_seconds,
        float,
    )


@pytest.mark.parametrize(
    "value",
    [
        0.0,
        -1.0,
    ],
)
def test_closed_session_polling_interval_must_be_positive(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "closed_session_polling_interval_seconds"
        ),
    ):
        RuntimeConfig(
            closed_session_polling_interval_seconds=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        True,
        "300",
        None,
    ],
)
def test_closed_session_polling_interval_must_be_numeric(
    value,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "closed_session_polling_interval_seconds"
        ),
    ):
        RuntimeConfig(
            closed_session_polling_interval_seconds=value,
        )

def test_default_heartbeat_interval() -> None:
    config = RuntimeConfig()

    assert (
        config.heartbeat_interval_seconds
        == 60.0
    )

def test_heartbeat_interval_is_normalized() -> None:
    config = RuntimeConfig(
        heartbeat_interval_seconds=30,
    )

    assert (
        config.heartbeat_interval_seconds
        == 30.0
    )

@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
        "60",
        None,
    ],
)
def test_heartbeat_interval_must_be_number(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="heartbeat_interval_seconds",
    ):
        RuntimeConfig(
            heartbeat_interval_seconds=value,  # type: ignore[arg-type]
        )

@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        -60.0,
    ],
)
def test_heartbeat_interval_must_be_positive(
    value: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        RuntimeConfig(
            heartbeat_interval_seconds=value,
        )


