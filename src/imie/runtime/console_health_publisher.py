from __future__ import annotations

from collections.abc import Callable

from imie.runtime.runtime_health_snapshot import (
    RuntimeHealthSnapshot,
)


class ConsoleHealthPublisher:
    """
    Publishes runtime lifecycle transitions in a compact,
    human-readable console format.
    """

    def __init__(
        self,
        *,
        output: Callable[[str], None] = print,
    ) -> None:
        if not callable(
            output
        ):
            raise TypeError(
                "output must be callable."
            )

        self.output = output

    def publish(
        self,
        snapshot: RuntimeHealthSnapshot,
    ) -> None:
        if not isinstance(
            snapshot,
            RuntimeHealthSnapshot,
        ):
            raise TypeError(
                "snapshot must be a "
                "RuntimeHealthSnapshot."
            )

        parts = [
            "[IMIE Runtime]",
            snapshot.state.value,
            f"cycles={snapshot.cycle_count}",
            snapshot.changed_at.isoformat(),
            snapshot.message,
        ]

        if snapshot.error_type is not None:
            parts.append(
                f"error={snapshot.error_type}"
            )

        self.output(
            " | ".join(
                parts
            )
        )