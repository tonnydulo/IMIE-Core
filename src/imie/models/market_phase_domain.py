from __future__ import annotations

from dataclasses import dataclass

from imie.models.market_phase_type import MarketPhaseType


@dataclass(frozen=True, slots=True)
class MarketPhaseDomain:
    """
    A single institutional domain's contribution toward
    the current market phase.
    """

    domain: str
    phase: MarketPhaseType
    weight: float
    confidence: float
    enabled: bool
    evidence: tuple[str, ...]
    warnings: tuple[str, ...]

    def __post_init__(self) -> None:
        domain = self.domain.strip()

        if not domain:
            raise ValueError(
                "domain must not be empty."
            )

        if not isinstance(
            self.phase,
            MarketPhaseType,
        ):
            raise TypeError(
                "phase must be a MarketPhaseType."
            )

        if self.weight < 0.0:
            raise ValueError(
                "weight must be greater than or equal to 0."
            )

        if not 0.0 <= self.confidence <= 100.0:
            raise ValueError(
                "confidence must be between 0 and 100."
            )

        object.__setattr__(
            self,
            "domain",
            domain.upper(),
        )

        object.__setattr__(
            self,
            "evidence",
            self._clean_items(
                self.evidence
            ),
        )

        object.__setattr__(
            self,
            "warnings",
            self._clean_items(
                self.warnings
            ),
        )

    @property
    def is_unknown(self) -> bool:
        return self.phase is MarketPhaseType.UNKNOWN

    @property
    def is_known(self) -> bool:
        return not self.is_unknown

    @property
    def weighted_score(self) -> float:
        if self.is_disabled or self.is_unknown:
            return 0.0

        return round(
            self.weight
            * self.confidence
            / 100.0,
            2,
        )

    @property
    def is_disabled(self) -> bool:
        return not self.enabled

    @classmethod
    def unknown(
        cls,
        *,
        domain: str,
        weight: float,
        evidence: tuple[str, ...] = (),
        warnings: tuple[str, ...] = (),
    ) -> MarketPhaseDomain:
        """
        Create an enabled domain whose phase is unresolved.
        """
        return cls(
            domain=domain,
            phase=MarketPhaseType.UNKNOWN,
            weight=weight,
            confidence=0.0,
            enabled=True,
            evidence=evidence,
            warnings=warnings,
        )

    @classmethod
    def disabled(
        cls,
        *,
        domain: str,
        weight: float,
        evidence: tuple[str, ...] = (),
        warnings: tuple[str, ...] = (),
    ) -> MarketPhaseDomain:
        """
        Create a disabled domain contribution.
        """
        return cls(
            domain=domain,
            phase=MarketPhaseType.UNKNOWN,
            weight=weight,
            confidence=0.0,
            enabled=False,
            evidence=evidence,
            warnings=warnings,
        )

    @classmethod
    def create(
        cls,
        *,
        domain: str,
        phase: MarketPhaseType,
        weight: float,
        confidence: float,
        enabled: bool = True,
        evidence: tuple[str, ...] = (),
        warnings: tuple[str, ...] = (),
    ) -> MarketPhaseDomain:
        """
        Create a resolved market-phase domain contribution.
        """
        return cls(
            domain=domain,
            phase=phase,
            weight=weight,
            confidence=confidence,
            enabled=enabled,
            evidence=evidence,
            warnings=warnings,
        )

    @staticmethod
    def _clean_items(
        items: tuple[str, ...],
    ) -> tuple[str, ...]:
        cleaned: list[str] = []
        seen: set[str] = set()

        for item in items:
            text = str(
                item
            ).strip()

            if not text:
                continue

            key = text.casefold()

            if key in seen:
                continue

            seen.add(
                key
            )

            cleaned.append(
                text
            )

        return tuple(
            cleaned
        )