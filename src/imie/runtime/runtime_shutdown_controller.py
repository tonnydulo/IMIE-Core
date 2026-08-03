from __future__ import annotations

import signal
from types import FrameType
from typing import Callable

from imie.runtime.continuous_runtime_runner import (
    ContinuousRuntimeRunner,
)


SignalHandler = (
    Callable[[int, FrameType | None], None]
    | int
    | None
)


class RuntimeShutdownController:
    """
    Converts operating-system termination signals into a graceful
    stop request for ContinuousRuntimeRunner.

    The controller restores all original signal handlers when
    uninstalled.
    """

    def __init__(
        self,
        *,
        runner: ContinuousRuntimeRunner,
    ) -> None:
        if not isinstance(
            runner,
            ContinuousRuntimeRunner,
        ):
            raise TypeError(
                "runner must be a ContinuousRuntimeRunner."
            )

        self.runner = runner

        self._installed = False
        self._received_signal: int | None = None

        self._previous_handlers: dict[
            signal.Signals,
            SignalHandler,
        ] = {}

    @property
    def installed(self) -> bool:
        return self._installed

    @property
    def received_signal(self) -> int | None:
        return self._received_signal

    @property
    def shutdown_requested(self) -> bool:
        return self._received_signal is not None

    @property
    def supported_signals(
        self,
    ) -> tuple[signal.Signals, ...]:
        configured: list[signal.Signals] = [
            signal.SIGINT,
        ]

        sigterm = getattr(
            signal,
            "SIGTERM",
            None,
        )

        if (
            sigterm is not None
            and sigterm not in configured
        ):
            configured.append(
                sigterm
            )

        return tuple(
            configured
        )

    def install(
        self,
    ) -> None:
        if self._installed:
            return

        installed_signals: list[
            signal.Signals
        ] = []

        try:
            for signal_number in self.supported_signals:
                previous_handler = signal.getsignal(
                    signal_number
                )

                self._previous_handlers[
                    signal_number
                ] = previous_handler

                signal.signal(
                    signal_number,
                    self._handle_signal,
                )

                installed_signals.append(
                    signal_number
                )

        except BaseException:
            self._restore_signals(
                tuple(
                    installed_signals
                )
            )

            self._previous_handlers.clear()
            raise

        self._installed = True

    def uninstall(
        self,
    ) -> None:
        if not self._installed:
            return

        self._restore_signals(
            tuple(
                self._previous_handlers
            )
        )

        self._previous_handlers.clear()
        self._installed = False

    def request_shutdown(
        self,
        signal_number: int | None = None,
    ) -> None:
        if (
            signal_number is not None
            and (
                isinstance(
                    signal_number,
                    bool,
                )
                or not isinstance(
                    signal_number,
                    int,
                )
            )
        ):
            raise TypeError(
                "signal_number must be an int or None."
            )

        if signal_number is not None:
            self._received_signal = signal_number

        self.runner.request_stop()

    def _handle_signal(
        self,
        signal_number: int,
        frame: FrameType | None,
    ) -> None:
        del frame

        self.request_shutdown(
            signal_number
        )

    def _restore_signals(
        self,
        signals_to_restore: tuple[
            signal.Signals,
            ...,
        ],
    ) -> None:
        for signal_number in reversed(
            signals_to_restore
        ):
            previous_handler = (
                self._previous_handlers.get(
                    signal_number
                )
            )

            if previous_handler is None:
                continue

            signal.signal(
                signal_number,
                previous_handler,
            )

    def __enter__(
        self,
    ) -> RuntimeShutdownController:
        self.install()
        return self

    def __exit__(
        self,
        exception_type,
        exception,
        traceback,
    ) -> bool:
        del exception_type
        del exception
        del traceback

        self.uninstall()
        return False