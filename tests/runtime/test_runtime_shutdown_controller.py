from __future__ import annotations

import signal

import pytest

from imie.runtime import (
    ContinuousRuntimeRunner,
    RuntimeConfig,
    RuntimeShutdownController,
    SingleAnalysisCycle,
)


class FakeMarketData:
    def connect(
        self,
    ) -> None:
        pass

    def disconnect(
        self,
    ) -> None:
        pass

    def get_quote(
        self,
        symbol: str,
    ):
        del symbol
        raise NotImplementedError

    def get_bars(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ):
        del symbol
        del timeframe
        del limit
        raise NotImplementedError


def make_runner() -> ContinuousRuntimeRunner:
    market_data = FakeMarketData()

    cycle = SingleAnalysisCycle(
        config=RuntimeConfig(),
        market_data=market_data,
    )

    return ContinuousRuntimeRunner(
        config=RuntimeConfig(),
        market_data=market_data,
        cycle=cycle,
    )


def test_controller_can_be_created() -> None:
    runner = make_runner()

    controller = RuntimeShutdownController(
        runner=runner,
    )

    assert controller.runner is runner
    assert controller.installed is False
    assert controller.received_signal is None
    assert controller.shutdown_requested is False


def test_runner_must_be_continuous_runner() -> None:
    with pytest.raises(
        TypeError,
        match="ContinuousRuntimeRunner",
    ):
        RuntimeShutdownController(
            runner=object(),  # type: ignore[arg-type]
        )


def test_supported_signals_include_sigint() -> None:
    controller = RuntimeShutdownController(
        runner=make_runner(),
    )

    assert signal.SIGINT in (
        controller.supported_signals
    )


def test_request_shutdown_requests_runner_stop() -> None:
    runner = make_runner()

    controller = RuntimeShutdownController(
        runner=runner,
    )

    controller.request_shutdown()

    assert runner.stop_requested is True
    assert controller.shutdown_requested is False
    assert controller.received_signal is None


def test_request_shutdown_records_signal() -> None:
    runner = make_runner()

    controller = RuntimeShutdownController(
        runner=runner,
    )

    controller.request_shutdown(
        signal.SIGINT
    )

    assert runner.stop_requested is True
    assert controller.shutdown_requested is True
    assert (
        controller.received_signal
        == signal.SIGINT
    )


@pytest.mark.parametrize(
    "value",
    [
        True,
        2.5,
        "SIGINT",
    ],
)
def test_signal_number_must_be_int_or_none(
    value: object,
) -> None:
    controller = RuntimeShutdownController(
        runner=make_runner(),
    )

    with pytest.raises(
        TypeError,
        match="signal_number",
    ):
        controller.request_shutdown(
            value,  # type: ignore[arg-type]
        )


def test_signal_handler_requests_shutdown() -> None:
    runner = make_runner()

    controller = RuntimeShutdownController(
        runner=runner,
    )

    controller._handle_signal(
        signal.SIGINT,
        None,
    )

    assert runner.stop_requested is True
    assert (
        controller.received_signal
        == signal.SIGINT
    )


def test_install_and_uninstall_restore_handlers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = make_runner()

    controller = RuntimeShutdownController(
        runner=runner,
    )

    previous_handlers = {
        signal_number: object()
        for signal_number
        in controller.supported_signals
    }

    signal_calls: list[
        tuple[
            signal.Signals,
            object,
        ]
    ] = []

    def fake_getsignal(
        signal_number: signal.Signals,
    ):
        return previous_handlers[
            signal_number
        ]

    def fake_signal(
        signal_number: signal.Signals,
        handler,
    ):
        signal_calls.append(
            (
                signal_number,
                handler,
            )
        )

        return previous_handlers[
            signal_number
        ]

    monkeypatch.setattr(
        signal,
        "getsignal",
        fake_getsignal,
    )

    monkeypatch.setattr(
        signal,
        "signal",
        fake_signal,
    )

    controller.install()

    assert controller.installed is True

    installed_count = len(
        controller.supported_signals
    )

    assert len(
        signal_calls
    ) == installed_count

    controller.uninstall()

    assert controller.installed is False
    assert len(
        signal_calls
    ) == installed_count * 2

    restored_calls = signal_calls[
        installed_count:
    ]

    expected_restored = [
        (
            signal_number,
            previous_handlers[
                signal_number
            ],
        )
        for signal_number
        in reversed(
            controller.supported_signals
        )
    ]

    assert restored_calls == expected_restored


def test_install_is_idempotent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = RuntimeShutdownController(
        runner=make_runner(),
    )

    signal_calls: list[object] = []

    monkeypatch.setattr(
        signal,
        "getsignal",
        lambda signal_number: signal.SIG_DFL,
    )

    def fake_signal(
        signal_number,
        handler,
    ):
        signal_calls.append(
            (
                signal_number,
                handler,
            )
        )

        return signal.SIG_DFL

    monkeypatch.setattr(
        signal,
        "signal",
        fake_signal,
    )

    controller.install()

    first_call_count = len(
        signal_calls
    )

    controller.install()

    assert len(
        signal_calls
    ) == first_call_count


def test_uninstall_is_idempotent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = RuntimeShutdownController(
        runner=make_runner(),
    )

    signal_calls: list[object] = []

    monkeypatch.setattr(
        signal,
        "getsignal",
        lambda signal_number: signal.SIG_DFL,
    )

    def fake_signal(
        signal_number,
        handler,
    ):
        signal_calls.append(
            (
                signal_number,
                handler,
            )
        )

        return signal.SIG_DFL

    monkeypatch.setattr(
        signal,
        "signal",
        fake_signal,
    )

    controller.install()
    controller.uninstall()

    first_call_count = len(
        signal_calls
    )

    controller.uninstall()

    assert len(
        signal_calls
    ) == first_call_count


def test_context_manager_installs_and_restores(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = RuntimeShutdownController(
        runner=make_runner(),
    )

    monkeypatch.setattr(
        signal,
        "getsignal",
        lambda signal_number: signal.SIG_DFL,
    )

    monkeypatch.setattr(
        signal,
        "signal",
        lambda signal_number, handler: signal.SIG_DFL,
    )

    with controller as active_controller:
        assert active_controller is controller
        assert controller.installed is True

    assert controller.installed is False


def test_context_manager_does_not_suppress_exceptions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = RuntimeShutdownController(
        runner=make_runner(),
    )

    monkeypatch.setattr(
        signal,
        "getsignal",
        lambda signal_number: signal.SIG_DFL,
    )

    monkeypatch.setattr(
        signal,
        "signal",
        lambda signal_number, handler: signal.SIG_DFL,
    )

    with pytest.raises(
        RuntimeError,
        match="Runtime failed",
    ):
        with controller:
            raise RuntimeError(
                "Runtime failed."
            )

    assert controller.installed is False