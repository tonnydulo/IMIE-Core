from __future__ import annotations

from collections.abc import Iterable

from imie.runtime.runtime_health_snapshot import (
    RuntimeHealthSnapshot,
)


class CompositeHealthPublisher:
    """
    Publishes one RuntimeHealthSnapshot to multiple
    health publishers.
    """

    def __init__(
        self,
        *,
        publishers: Iterable[object],
        continue_on_error: bool = True,
    ) -> None:
        try:
            normalized_publishers = tuple(
                publishers
            )
        except TypeError as exc:
            raise TypeError(
                "publishers must be an iterable."
            ) from exc

        if not normalized_publishers:
            raise ValueError(
                "publishers must contain at least "
                "one health publisher."
            )

        for publisher in normalized_publishers:
            if not callable(
                getattr(
                    publisher,
                    "publish",
                    None,
                )
            ):
                raise TypeError(
                    "Every health publisher must "
                    "provide publish()."
                )

        if not isinstance(
            continue_on_error,
            bool,
        ):
            raise TypeError(
                "continue_on_error must be a bool."
            )

        self.publishers = (
            normalized_publishers
        )
        self.continue_on_error = (
            continue_on_error
        )

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

        failures: list[
            tuple[
                int,
                Exception,
            ]
        ] = []

        for index, publisher in enumerate(
            self.publishers
        ):
            try:
                publisher.publish(
                    snapshot
                )

            except Exception as exc:
                if not self.continue_on_error:
                    raise

                failures.append(
                    (
                        index,
                        exc,
                    )
                )

        if failures:
            descriptions = "; ".join(
                (
                    f"publisher {index}: "
                    f"{type(exc).__name__}: {exc}"
                )
                for index, exc in failures
            )

            raise RuntimeError(
                "One or more health publishers failed: "
                f"{descriptions}"
            )