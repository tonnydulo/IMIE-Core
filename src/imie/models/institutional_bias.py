
from __future__ import annotations

from dataclasses import dataclass, field

from imie.models.institutional_direction import (
    InstitutionalDirection,
)


@dataclass(frozen=True, slots=True)
class InstitutionalBias:
    """
    Immutable summary of the broader institutional market bias.

    InstitutionalBias records:

    - the dominant institutional direction;
    - directional strength;
    - confidence in the bias;
    - bullish and bearish weighted scores;
    - agreement and conflict counts;
    - domains that support, oppose, remain neutral, or are unknown;
    - supporting evidence;
    - warnings.

    The model does not:

    - calculate analyst direction;
    - assign analyst weights;
    - authorize trades;
    - create or modify a TradePlan;
    - replace InstitutionalConfluence.

    Strength represents directional separation between bullish
    and bearish weighted scores.

    Confidence represents the engine's confidence in the resulting
    institutional bias and is calculated externally by the
    InstitutionalBiasEngine.
    """

    direction: InstitutionalDirection

    strength: float
    confidence: float

    bullish_score: float
    bearish_score: float

    agreement_count: int
    conflict_count: int

    supporting_domains: tuple[str, ...] = field(
        default_factory=tuple
    )

    opposing_domains: tuple[str, ...] = field(
        default_factory=tuple
    )

    neutral_domains: tuple[str, ...] = field(
        default_factory=tuple
    )

    unknown_domains: tuple[str, ...] = field(
        default_factory=tuple
    )

    evidence: tuple[str, ...] = field(
        default_factory=tuple
    )

    warnings: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        direction = self._normalize_direction(
            self.direction
        )

        strength = self._normalize_percentage(
            value=self.strength,
            name="strength",
        )

        confidence = self._normalize_percentage(
            value=self.confidence,
            name="confidence",
        )

        bullish_score = self._normalize_score(
            value=self.bullish_score,
            name="bullish_score",
        )

        bearish_score = self._normalize_score(
            value=self.bearish_score,
            name="bearish_score",
        )

        agreement_count = self._normalize_count(
            value=self.agreement_count,
            name="agreement_count",
        )

        conflict_count = self._normalize_count(
            value=self.conflict_count,
            name="conflict_count",
        )

        supporting_domains = self._clean_domains(
            self.supporting_domains,
            name="supporting_domains",
        )

        opposing_domains = self._clean_domains(
            self.opposing_domains,
            name="opposing_domains",
        )

        neutral_domains = self._clean_domains(
            self.neutral_domains,
            name="neutral_domains",
        )

        unknown_domains = self._clean_domains(
            self.unknown_domains,
            name="unknown_domains",
        )

        evidence = self._clean_text_items(
            self.evidence,
            name="evidence",
        )

        warnings = self._clean_text_items(
            self.warnings,
            name="warnings",
        )

        object.__setattr__(
            self,
            "direction",
            direction,
        )

        object.__setattr__(
            self,
            "strength",
            strength,
        )

        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

        object.__setattr__(
            self,
            "bullish_score",
            bullish_score,
        )

        object.__setattr__(
            self,
            "bearish_score",
            bearish_score,
        )

        object.__setattr__(
            self,
            "agreement_count",
            agreement_count,
        )

        object.__setattr__(
            self,
            "conflict_count",
            conflict_count,
        )

        object.__setattr__(
            self,
            "supporting_domains",
            supporting_domains,
        )

        object.__setattr__(
            self,
            "opposing_domains",
            opposing_domains,
        )

        object.__setattr__(
            self,
            "neutral_domains",
            neutral_domains,
        )

        object.__setattr__(
            self,
            "unknown_domains",
            unknown_domains,
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

        self._validate_directional_contract()
        self._validate_domain_contract()

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

        if direction is InstitutionalDirection.UNKNOWN:
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
    def _normalize_score(
        *,
        value: object,
        name: str,
    ) -> float:
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
    def _normalize_count(
        *,
        value: object,
        name: str,
    ) -> int:
        if isinstance(
            value,
            bool,
        ):
            raise TypeError(
                f"{name} must be an int."
            )

        try:
            normalized = int(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TypeError(
                f"{name} must be an int."
            ) from exc

        if normalized != value:
            raise TypeError(
                f"{name} must be an int."
            )

        if normalized < 0:
            raise ValueError(
                f"{name} cannot be negative."
            )

        return normalized

    @staticmethod
    def _clean_domains(
        domains: tuple[str, ...],
        *,
        name: str,
    ) -> tuple[str, ...]:
        if not isinstance(
            domains,
            tuple,
        ):
            raise TypeError(
                f"{name} must be a tuple."
            )

        cleaned: list[str] = []
        seen: set[str] = set()

        for domain in domains:
            if not isinstance(
                domain,
                str,
            ):
                raise TypeError(
                    f"{name} must contain strings."
                )

            text = domain.strip().upper()

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

    @staticmethod
    def _clean_text_items(
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

    def _validate_directional_contract(
        self,
    ) -> None:
        expected_strength = round(
            abs(
                self.bullish_score
                - self.bearish_score
            ),
            2,
        )

        if self.strength != expected_strength:
            raise ValueError(
                "strength must equal the absolute difference "
                "between bullish_score and bearish_score."
            )

        if (
            self.direction
            is InstitutionalDirection.BULLISH
            and self.bullish_score <= self.bearish_score
        ):
            raise ValueError(
                "Bullish direction requires bullish_score to "
                "exceed bearish_score."
            )

        if (
            self.direction
            is InstitutionalDirection.BEARISH
            and self.bearish_score <= self.bullish_score
        ):
            raise ValueError(
                "Bearish direction requires bearish_score to "
                "exceed bullish_score."
            )

        if (
            self.direction
            is InstitutionalDirection.NEUTRAL
            and self.bullish_score != self.bearish_score
        ):
            raise ValueError(
                "Neutral direction requires equal bullish and "
                "bearish scores."
            )

        if (
            self.direction
            is InstitutionalDirection.UNKNOWN
            and (
                self.bullish_score > 0.0
                or self.bearish_score > 0.0
            )
        ):
            raise ValueError(
                "Unknown direction requires zero bullish and "
                "bearish scores."
            )

    def _validate_domain_contract(
        self,
    ) -> None:
        domain_groups = (
            self.supporting_domains,
            self.opposing_domains,
            self.neutral_domains,
            self.unknown_domains,
        )

        all_domains = tuple(
            domain
            for group in domain_groups
            for domain in group
        )

        if len(
            all_domains
        ) != len(
            set(
                all_domains
            )
        ):
            raise ValueError(
                "A domain cannot appear in more than one bias "
                "classification."
            )

        if (
            self.agreement_count
            != len(
                self.supporting_domains
            )
        ):
            raise ValueError(
                "agreement_count must match supporting_domains."
            )

        if (
            self.conflict_count
            != len(
                self.opposing_domains
            )
        ):
            raise ValueError(
                "conflict_count must match opposing_domains."
            )

        if (
            self.direction
            in {
                InstitutionalDirection.NEUTRAL,
                InstitutionalDirection.UNKNOWN,
            }
            and self.agreement_count > 0
        ):
            raise ValueError(
                "Neutral or unknown bias cannot report supporting "
                "directional domains."
            )

    @property
    def is_bullish(self) -> bool:
        return (
            self.direction
            is InstitutionalDirection.BULLISH
        )

    @property
    def is_bearish(self) -> bool:
        return (
            self.direction
            is InstitutionalDirection.BEARISH
        )

    @property
    def is_neutral(self) -> bool:
        return (
            self.direction
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
        return self.direction.is_directional

    @property
    def has_agreement(self) -> bool:
        return self.agreement_count > 0

    @property
    def has_conflict(self) -> bool:
        return self.conflict_count > 0

    @property
    def is_mixed(self) -> bool:
        return (
            self.has_agreement
            and self.has_conflict
        )

    @property
    def classified_domain_count(self) -> int:
        return (
            len(
                self.supporting_domains
            )
            + len(
                self.opposing_domains
            )
            + len(
                self.neutral_domains
            )
            + len(
                self.unknown_domains
            )
        )

    @property
    def directional_domain_count(self) -> int:
        return (
            len(
                self.supporting_domains
            )
            + len(
                self.opposing_domains
            )
        )

    @property
    def unresolved_domain_count(self) -> int:
        return (
            len(
                self.neutral_domains
            )
            + len(
                self.unknown_domains
            )
        )

    @property
    def score_spread(self) -> float:
        return self.strength

    @classmethod
    def empty(
        cls,
        *,
        domains: tuple[str, ...] = (),
        evidence: tuple[str, ...] = (),
        warnings: tuple[str, ...] = (),
    ) -> InstitutionalBias:
        """
        Build an unknown, zero-score institutional bias.

        Supplied domains are classified as unknown.
        """
        normalized_domains = tuple(
            domain.strip().upper()
            for domain in domains
            if domain.strip()
        )

        return cls(
            direction=InstitutionalDirection.UNKNOWN,
            strength=0.0,
            confidence=0.0,
            bullish_score=0.0,
            bearish_score=0.0,
            agreement_count=0,
            conflict_count=0,
            supporting_domains=(),
            opposing_domains=(),
            neutral_domains=(),
            unknown_domains=normalized_domains,
            evidence=evidence,
            warnings=warnings,
        )