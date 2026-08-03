from __future__ import annotations

from threading import Thread
from time import monotonic, sleep

import pytest

from imie.runtime import (
    InterruptibleSleeper,
)


def test_sleeper_can_be_created() -> None:
    sleeper = InterruptibleSleeper()

    assert sleeper.interrupted is False


def test_interrupt_sets_interrupted_state() -> None:
    sleeper = InterruptibleSleeper()

    sleeper.interrupt()

    assert sleeper.interrupted is True


def test_reset_clears_interrupted_state() -> None:
    sleeper = InterruptibleSleeper()

    sleeper.interrupt()
    sleeper.reset()

    assert sleeper.interrupted is False


def test_wait_returns_false_after_normal_timeout() -> None:
    sleeper = InterruptibleSleeper()

    interrupted = sleeper.wait(
        0.001
    )

    assert interrupted is False


def test_wait_returns_true_when_already_interrupted() -> None:
    sleeper = InterruptibleSleeper()

    sleeper.interrupt()

    interrupted = sleeper.wait(
        60.0
    )

    assert interrupted is True


def test_interrupt_wakes_active_wait() -> None:
    sleeper = InterruptibleSleeper()

    results: list[bool] = []

    def wait_for_interrupt() -> None:
        results.append(
            sleeper.wait(
                10.0
            )
        )

    worker = Thread(
        target=wait_for_interrupt,
    )

    started_at = monotonic()

    worker.start()

    sleep(
        0.02
    )

    sleeper.interrupt()

    worker.join(
        timeout=1.0
    )

    elapsed = monotonic() - started_at

    assert worker.is_alive() is False
    assert results == [
        True,
    ]
    assert elapsed < 1.0


@pytest.mark.parametrize(
    "value",
    [
        True,
        "5",
        None,
    ],
)
def test_wait_requires_numeric_seconds(
    value: object,
) -> None:
    sleeper = InterruptibleSleeper()

    with pytest.raises(
        TypeError,
        match="seconds",
    ):
        sleeper.wait(
            value,  # type: ignore[arg-type]
        )


def test_wait_rejects_negative_seconds() -> None:
    sleeper = InterruptibleSleeper()

    with pytest.raises(
        ValueError,
        match="negative",
    ):
        sleeper.wait(
            -1.0
        )