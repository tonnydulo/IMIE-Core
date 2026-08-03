from __future__ import annotations

from dataclasses import dataclass, field

from imie.models.analyst_result import AnalystResult


@dataclass(slots=True)
class AnalystRegistry:
    """
    Stores the latest result produced by each analyst.

    The registry performs no analysis.

    It simply provides a single location where the
    Decision Director can retrieve analyst opinions.
    """

    _results: dict[str, AnalystResult] = field(
        default_factory=dict
    )

    def register(
        self,
        result: AnalystResult,
    ) -> None:
        """
        Register or replace an analyst result.
        """

        self._results[result.analyst_id] = result

    def get(
        self,
        analyst_id: str,
    ) -> AnalystResult | None:
        """
        Retrieve an analyst result.

        Returns None if unavailable.
        """

        return self._results.get(
            analyst_id.upper()
        )

    def all(
        self,
    ) -> list[AnalystResult]:
        """
        Return every registered analyst.
        """

        return list(
            self._results.values()
        )

    def enabled(
        self,
    ) -> list[AnalystResult]:
        """
        Return only enabled analysts.
        """

        return [
            result
            for result in self._results.values()
            if result.enabled
        ]

    def evidence(
        self,
    ) -> list[str]:
        """
        Collect evidence from every enabled analyst.
        """

        evidence: list[str] = []

        for result in self.enabled():
            evidence.extend(result.evidence)

        return evidence

    def warnings(
        self,
    ) -> list[str]:
        """
        Collect warnings from every enabled analyst.
        """

        warnings: list[str] = []

        for result in self.enabled():
            warnings.extend(result.warnings)

        return warnings

    def confidence(
        self,
    ) -> float:
        """
        Average confidence of enabled analysts.
        """

        enabled = self.enabled()

        if not enabled:
            return 0.0

        return (
            sum(
                r.confidence
                for r in enabled
            )
            / len(enabled)
        )

    def contains(
        self,
        analyst_id: str,
    ) -> bool:
        return analyst_id.upper() in self._results

    def clear(
        self,
    ) -> None:
        self._results.clear()

    def __len__(
        self,
    ) -> int:
        return len(self._results)