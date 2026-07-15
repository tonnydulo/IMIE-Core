from __future__ import annotations

from dataclasses import dataclass, field

from imie.models.institutional_direction import (
    InstitutionalDirection,
)


@dataclass(frozen=True, slots=True)
class InstitutionalBiasDomain:
    """
    Immutable normalized contribution from one institutional domain.

    Examples of domains:

    - TREND
    - STRUCTURE
    - LIQUIDITY
    - ORDER_BLOCK
    - AUCTION
    - PRESSURE
    - PARTICIPATION
    - VALUE

    Each domain records:

    - its stable domain identifier;
    - resolved institutional direction;
    - configured weight;
    - source confidence;
    - weighted contribution;
    - whether the domain is enabled;
    - evidence and warnings.

    Weighted contribution is calculated as:

        weight * confidence / 100

    A disabled, neutral, or unknown domain must contribute zero.

    This model does not resolve analyst direction, retrieve analyst
    results, calculate overall bias, or authorize trades.
    """

    domain: str
    direction: InstitutionalDirection

    weight: float
    confidence: float
    weighted_score: float

    enabled: bool = True

    evidence: tuple[str, ...] = field(
        default_factory=tuple
    )

    warnings: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        domain = self._normalize_domain(
            self.domain
        )

        direction = self._normalize_direction(
            self.direction
        )

        weight = self._normalize_percentage(
            value=self.weight,
            name="weight",
        )

        confidence = self._normalize_percentage(
            value=self.confidence,
            name="confidence",
        )

        weighted_score = self._normalize_percentage(
            value=self.weighted_score,
            name="weighted_score",
        )

        if not isinstance(
            self.enabled,
            bool,
        ):
            raise TypeError(
                "enabled must be a bool."
            )

        evidence = self._clean_items(
            self.evidence,
            name="evidence",
        )

        warnings = self._clean_items(
            self.warnings,
            name="warnings",
        )

        object.__setattr__(
            self,
            "domain",
            domain,
        )

        object.__setattr__(
            self,
            "direction",
            direction,
        )

        object.__setattr__(
            self,
            "weight",
            weight,
        )

        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

        object.__setattr__(
            self,
            "weighted_score",
            weighted_score,
        )

        object.__setattr__(
            self,
            "evidence",
            evidence,
        )

        object.__setattr__(
            self,
            "warnings",
            warnings,
        )

        self._validate_weighted_score()

    @staticmethod
    def _normalize_domain(
        value: object,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "domain must be a string."
            )

        domain = value.strip().upper()

        if not domain:
            raise ValueError(
                "domain cannot be empty."
            )

        return domain

    @staticmethod
    def _normalize_direction(
        value: object,
    ) -> InstitutionalDirection:
        if isinstance(
            value,
            InstitutionalDirection,
        ):
            return value

        direction = (
            InstitutionalDirection.from_value(
                value
            )
        )

        if (
            direction
            is InstitutionalDirection.UNKNOWN
        ):
            normalized = str(
                getattr(
                    value,
                    "value",
                    value,
                )
            ).strip().upper()

            if normalized not in {
                "",
                "UNKNOWN",
                "NONE",
                "UNAVAILABLE",
                "UNRESOLVED",
            }:
                raise ValueError(
                    "direction must be an InstitutionalDirection "
                    "or recognized alias."
                )

        return direction

    @staticmethod
    def _normalize_percentage(
        *,
        value: object,
        name: str,
    ) -> float:
        if isinstance(
            value,
            bool,
        ):
            raise TypeError(
                f"{name} must be numeric."
            )

        try:
            normalized = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TypeError(
                f"{name} must be numeric."
            ) from exc

        if not 0.0 <= normalized <= 100.0:
            raise ValueError(
                f"{name} must be between 0 and 100."
            )

        return round(
            normalized,
            2,
        )

    @staticmethod
    def _clean_items(
        items: tuple[str, ...],
        *,
        name: str,
    ) -> tuple[str, ...]:
        if not isinstance(
            items,
            tuple,
        ):
            raise TypeError(
                f"{name} must be a tuple."
            )

        cleaned: list[str] = []
        seen: set[str] = set()

        for item in items:
            if not isinstance(
                item,
                str,
            ):
                raise TypeError(
                    f"{name} must contain strings."
                )

            text = item.strip()

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

    def _validate_weighted_score(
        self,
    ) -> None:
        expected_score = self._expected_weighted_score()

        if self.weighted_score != expected_score:
            raise ValueError(
                "weighted_score must equal weight multiplied by "
                "confidence divided by 100 for an enabled "
                "directional domain, otherwise zero."
            )

    def _expected_weighted_score(
        self,
    ) -> float:
        if not self.enabled:
            return 0.0

        if not self.direction.is_directional:
            return 0.0

        return round(
            (
                self.weight
                * self.confidence
                / 100.0
            ),
            2,
        )

    @property
    def is_bullish(self) -> bool:
        return (
            self.enabled
            and self.direction
            is InstitutionalDirection.BULLISH
        )

    @property
    def is_bearish(self) -> bool:
        return (
            self.enabled
            and self.direction
            is InstitutionalDirection.BEARISH
        )

    @property
    def is_neutral(self) -> bool:
        return (
            self.enabled
            and self.direction
            is InstitutionalDirection.NEUTRAL
        )

    @property
    def is_unknown(self) -> bool:
        return (
            self.direction
            is InstitutionalDirection.UNKNOWN
        )

    @property
    def is_directional(self) -> bool:
        return (
            self.enabled
            and self.direction.is_directional
        )

    @property
    def contributes(self) -> bool:
        return (
            self.is_directional
            and self.weighted_score > 0.0
        )

    @property
    def bullish_contribution(self) -> float:
        if self.is_bullish:
            return self.weighted_score

        return 0.0

    @property
    def bearish_contribution(self) -> float:
        if self.is_bearish:
            return self.weighted_score

        return 0.0

    @property
    def is_disabled(self) -> bool:
        return not self.enabled

    @property
    def has_evidence(self) -> bool:
        return bool(
            self.evidence
        )

    @property
    def has_warnings(self) -> bool:
        return bool(
            self.warnings
        )

    @classmethod
    def create(
        cls,
        *,
        domain: str,
        direction: InstitutionalDirection,
        weight: float,
        confidence: float,
        enabled: bool = True,
        evidence: tuple[str, ...] = (),
        warnings: tuple[str, ...] = (),
    ) -> InstitutionalBiasDomain:
        """
        Create a domain contribution and calculate its weighted score.
        """
        normalized_direction = (
            InstitutionalDirection.from_value(
                direction
            )
        )

        weighted_score = 0.0

        if (
            enabled
            and normalized_direction.is_directional
        ):
            weighted_score = round(
                (
                    float(
                        weight
                    )
                    * float(
                        confidence
                    )
                    / 100.0
                ),
                2,
            )

        return cls(
            domain=domain,
            direction=normalized_direction,
            weight=weight,
            confidence=confidence,
            weighted_score=weighted_score,
            enabled=enabled,
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
    ) -> InstitutionalBiasDomain:
        """
        Build a disabled domain contribution.
        """
        return cls(
            domain=domain,
            direction=InstitutionalDirection.UNKNOWN,
            weight=weight,
            confidence=0.0,
            weighted_score=0.0,
            enabled=False,
            evidence=evidence,
            warnings=warnings,
        )

    @classmethod
    def unknown(
        cls,
        *,
        domain: str,
        weight: float,
        confidence: float = 0.0,
        evidence: tuple[str, ...] = (),
        warnings: tuple[str, ...] = (),
    ) -> InstitutionalBiasDomain:
        """
        Build an enabled but unresolved domain contribution.
        """
        return cls(
            domain=domain,
            direction=InstitutionalDirection.UNKNOWN,
            weight=weight,
            confidence=confidence,
            weighted_score=0.0,
            enabled=True,
            evidence=evidence,
            warnings=warnings,
        )
    