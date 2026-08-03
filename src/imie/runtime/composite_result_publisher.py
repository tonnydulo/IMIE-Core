from __future__ import annotations

from collections.abc import Callable, Iterable

from imie.runtime.analysis_cycle_result import (
    AnalysisCycleResult,
)


class CompositeResultPublisher:
    """
    Publishes one AnalysisCycleResult to multiple publishers.

    Each publisher must be callable and accept one AnalysisCycleResult.
    Publishers are invoked in the order they were provided.
    """

    def __init__(
        self,
        *,
        publishers: Iterable[
            Callable[
                [AnalysisCycleResult],
                None,
            ]
        ],
        continue_on_error: bool = False,
    ) -> None:
        try:
            normalized_publishers = tuple(
                publishers
            )
        except TypeError as exc:
            raise TypeError(
                "publishers must be an iterable of callables."
            ) from exc

        if not normalized_publishers:
            raise ValueError(
                "publishers must contain at least one publisher."
            )

        for publisher in normalized_publishers:
            if not callable(
                publisher
            ):
                raise TypeError(
                    "Every publisher must be callable."
                )

        if not isinstance(
            continue_on_error,
            bool,
        ):
            raise TypeError(
                "continue_on_error must be a bool."
            )

        self.publishers = normalized_publishers
        self.continue_on_error = continue_on_error

    def __call__(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        self.publish(
            result
        )

    def publish(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        if not isinstance(
            result,
            AnalysisCycleResult,
        ):
            raise TypeError(
                "result must be an AnalysisCycleResult."
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
                publisher(
                    result
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
                "One or more publishers failed: "
                f"{descriptions}"
            )