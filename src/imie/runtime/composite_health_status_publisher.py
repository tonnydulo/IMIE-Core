from __future__ import annotations

from collections.abc import Iterable

from imie.runtime.health_status_publisher import (
    HealthStatusPublisher,
)
from imie.runtime.runtime_health_summary import (
    RuntimeHealthSummary,
)


class CompositeHealthStatusPublisher:
    def __init__(
        self,
        publishers: Iterable[
            HealthStatusPublisher
        ],
    ) -> None:
        if isinstance(
            publishers,
            str | bytes,
        ):
            raise TypeError(
                "publishers must be an iterable of "
                "health-status publishers."
            )

        try:
            resolved_publishers = tuple(
                publishers
            )
        except TypeError as error:
            raise TypeError(
                "publishers must be iterable."
            ) from error

        if not resolved_publishers:
            raise ValueError(
                "publishers cannot be empty."
            )

        for publisher in resolved_publishers:
            publish_method = getattr(
                publisher,
                "publish",
                None,
            )

            if not callable(
                publish_method
            ):
                raise TypeError(
                    "Each health-status publisher must "
                    "provide a callable publish method."
                )

        self.publishers = (
            resolved_publishers
        )

    def publish(
        self,
        summary: RuntimeHealthSummary,
    ) -> None:
        if not isinstance(
            summary,
            RuntimeHealthSummary,
        ):
            raise TypeError(
                "summary must be a RuntimeHealthSummary."
            )

        for publisher in self.publishers:
            publisher.publish(
                summary
            )