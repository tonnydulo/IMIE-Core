from __future__ import annotations

from dataclasses import dataclass, field

from imie.models.institutional_direction import (
    InstitutionalDirection,
)


@dataclass(frozen=True, slots=True)
class InstitutionalConfluence:
    """
    Immutable summary of institutional agreement and conflict.

    The model supports two compatible contracts.

    Legacy support contract
    -----------------------
    The original confluence engine supplies:

    - structure_support
    - liquidity_support
    - order_block_support
    - agreement_count
    - confidence_adjustment
    - score

    Directional contract
    --------------------
    The directional confluence engine additionally supplies:

    - dominant_direction
    - bullish_count
    - bearish_count
    - neutral_count
    - unknown_count
    - conflict_count

    InstitutionalConfluence does not authorize trades and does
    not alter a TradePlan. It only records the result of completed
    institutional reasoning.
    """

    score: float

    structure_support: bool
    liquidity_support: bool
    order_block_support: bool

    agreement_count: int
    confidence_adjustment: float

    auction_support: bool = False
    pressure_support: bool = False
    participation_support: bool = False
    value_support: bool = False

    domain_count: int = 3

    dominant_direction: InstitutionalDirection = (
        InstitutionalDirection.UNKNOWN
    )

    bullish_count: int = 0
    bearish_count: int = 0
    neutral_count: int = 0
    unknown_count: int = 0

    conflict_count: int = 0

    evidence: tuple[str, ...] = field(
        default_factory=tuple
    )

    warnings: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        self._validate_support_flags()

        score = self._normalize_score(
            self.score
        )

        domain_count = self._normalize_domain_count(
            self.domain_count
        )

        agreement_count = self._normalize_count(
            value=self.agreement_count,
            name="agreement_count",
            maximum=domain_count,
        )

        conflict_count = self._normalize_count(
            value=self.conflict_count,
            name="conflict_count",
            maximum=domain_count,
        )

        confidence_adjustment = (
            self._normalize_confidence_adjustment(
                self.confidence_adjustment
            )
        )

        dominant_direction = (
            self._normalize_direction(
                self.dominant_direction
            )
        )

        bullish_count = self._normalize_count(
            value=self.bullish_count,
            name="bullish_count",
            maximum=domain_count,
        )

        bearish_count = self._normalize_count(
            value=self.bearish_count,
            name="bearish_count",
            maximum=domain_count,
        )

        neutral_count = self._normalize_count(
            value=self.neutral_count,
            name="neutral_count",
            maximum=domain_count,
        )

        unknown_count = self._normalize_count(
            value=self.unknown_count,
            name="unknown_count",
            maximum=domain_count,
        )

        object.__setattr__(
            self,
            "score",
            score,
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
            "confidence_adjustment",
            confidence_adjustment,
        )

        object.__setattr__(
            self,
            "dominant_direction",
            dominant_direction,
        )

        object.__setattr__(
            self,
            "bullish_count",
            bullish_count,
        )

        object.__setattr__(
            self,
            "bearish_count",
            bearish_count,
        )

        object.__setattr__(
            self,
            "neutral_count",
            neutral_count,
        )

        object.__setattr__(
            self,
            "unknown_count",
            unknown_count,
        )

        object.__setattr__(
            self,
            "evidence",
            self._clean_items(
                self.evidence,
                name="evidence",
            ),
        )

        object.__setattr__(
            self,
            "warnings",
            self._clean_items(
                self.warnings,
                name="warnings",
            ),
        )

        object.__setattr__(
            self,
            "domain_count",
            domain_count,
        )

        self._validate_legacy_support_contract()
        self._validate_adjustment_contract()

        if self.has_directional_counts:
            self._validate_directional_contract()

    def _validate_support_flags(self) -> None:
        support_flags = (
            (
                "structure_support",
                self.structure_support,
            ),
            (
                "liquidity_support",
                self.liquidity_support,
            ),
            (
                "order_block_support",
                self.order_block_support,
            ),
            (
                "auction_support",
                self.auction_support,
            ),
            (
                "pressure_support",
                self.pressure_support,
            ),
            (
                "participation_support",
                self.participation_support,
            ),
            (
                "value_support",
                self.value_support,
            ),
        )

        for name, value in support_flags:
            if not isinstance(
                value,
                bool,
            ):
                raise TypeError(
                    f"{name} must be a bool."
                )

    @staticmethod
    def _normalize_score(
        value: object,
    ) -> float:
        score = float(
            value
        )

        if not 0.0 <= score <= 100.0:
            raise ValueError(
                "score must be between 0 and 100."
            )

        return score
    
    @staticmethod
    def _normalize_domain_count(
        value: object,
    ) -> int:
        if isinstance(
            value,
            bool,
        ):
            raise TypeError(
                "domain_count must be an int."
            )

        try:
            domain_count = int(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TypeError(
                "domain_count must be an int."
            ) from exc

        if domain_count != value:
            raise TypeError(
                "domain_count must be an int."
            )

        if domain_count not in (
            3,
            7,
        ):
            raise ValueError(
                "domain_count must be either 3 or 7."
            )

        return domain_count

    @staticmethod
    def _normalize_confidence_adjustment(
        value: object,
    ) -> float:
        adjustment = float(
            value
        )

        if not 0.0 <= adjustment <= 8.0:
            raise ValueError(
                "confidence_adjustment must be between 0 and 8."
            )

        return adjustment

    @staticmethod
    def _normalize_count(
        *,
        value: object,
        name: str,
        maximum: int,
    ) -> int:
        if isinstance(
            value,
            bool,
        ):
            raise TypeError(
                f"{name} must be an int."
            )

        try:
            count = int(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TypeError(
                f"{name} must be an int."
            ) from exc

        if count != value:
            raise TypeError(
                f"{name} must be an int."
            )

        if not 0 <= count <= maximum:
            raise ValueError(
                f"{name} must be between 0 and {maximum}."
            )

        return count

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
                    "dominant_direction must be an "
                    "InstitutionalDirection or recognized alias."
                )

        return direction

    def _validate_legacy_support_contract(
        self,
    ) -> None:
        support_count = sum(
            (
                self.structure_support,
                self.liquidity_support,
                self.order_block_support,
                self.auction_support,
                self.pressure_support,
                self.participation_support,
                self.value_support,
            )
        )

        if self.agreement_count != support_count:
            raise ValueError(
                "agreement_count must match the number of "
                "supporting institutional domains."
            )

        if self.domain_count == 3:
            if any(
                (
                    self.auction_support,
                    self.pressure_support,
                    self.participation_support,
                    self.value_support,
                )
            ):
                raise ValueError(
                    "Extended support flags require "
                    "domain_count=7."
                )

            expected_score = self._expected_score(
                structure_support=(
                    self.structure_support
                ),
                liquidity_support=(
                    self.liquidity_support
                ),
                order_block_support=(
                    self.order_block_support
                ),
            )

            if self.score != expected_score:
                raise ValueError(
                    "score must match the configured "
                    "institutional support weights."
                )

    def _validate_adjustment_contract(
        self,
    ) -> None:
        expected_adjustment = (
            self._expected_adjustment(
                agreement_count=self.agreement_count,
                domain_count=self.domain_count,
            )
        )

        if (
            self.confidence_adjustment
            != expected_adjustment
        ):
            raise ValueError(
                "confidence_adjustment does not match "
                "agreement_count."
            )

    def _validate_directional_contract(
        self,
    ) -> None:
        total = self.directional_count

        if total != self.domain_count:
            raise ValueError(
                "Directional counts must total "
                f"{self.domain_count} institutional domains."
            )

        directional_count = (
            self.bullish_count
            + self.bearish_count
        )

        if self.conflict_count > directional_count:
            raise ValueError(
                "conflict_count cannot exceed the number of "
                "directional institutional domains."
            )

        if (
            self.agreement_count
            + self.conflict_count
            > directional_count
        ):
            raise ValueError(
                "agreement_count plus conflict_count cannot exceed "
                "the number of directional institutional domains."
            )

        if (
            self.dominant_direction
            is InstitutionalDirection.BULLISH
        ):
            if self.agreement_count != self.bullish_count:
                raise ValueError(
                    "Bullish dominant direction requires "
                    "agreement_count to match bullish_count."
                )

            if self.conflict_count != self.bearish_count:
                raise ValueError(
                    "Bullish dominant direction requires "
                    "conflict_count to match bearish_count."
                )

        elif (
            self.dominant_direction
            is InstitutionalDirection.BEARISH
        ):
            if self.agreement_count != self.bearish_count:
                raise ValueError(
                    "Bearish dominant direction requires "
                    "agreement_count to match bearish_count."
                )

            if self.conflict_count != self.bullish_count:
                raise ValueError(
                    "Bearish dominant direction requires "
                    "conflict_count to match bullish_count."
                )

        elif (
            self.dominant_direction
            is InstitutionalDirection.NEUTRAL
        ):
            if (
                self.bullish_count > 0
                or self.bearish_count > 0
            ):
                raise ValueError(
                    "Neutral dominant direction cannot contain "
                    "bullish or bearish directional votes."
                )

            if (
                self.agreement_count != 0
                or self.conflict_count != 0
            ):
                raise ValueError(
                    "Neutral dominant direction requires zero "
                    "agreement and conflict."
                )

        elif (
            self.dominant_direction
            is InstitutionalDirection.UNKNOWN
        ):
            if self.agreement_count > 0:
                raise ValueError(
                    "Unknown dominant direction cannot report "
                    "directional agreement."
                )

    @staticmethod
    def _expected_adjustment(
        *,
        agreement_count: int,
        domain_count: int,
    ) -> float:
        if domain_count == 3:
            adjustments = {
                0: 0.0,
                1: 2.0,
                2: 5.0,
                3: 8.0,
            }

            return adjustments[
                agreement_count
            ]

        adjustments = {
            0: 0.0,
            1: 1.0,
            2: 2.0,
            3: 4.0,
            4: 5.0,
            5: 6.0,
            6: 7.0,
            7: 8.0,
        }

        return adjustments[
            agreement_count
        ]

    @staticmethod
    def _expected_score(
        *,
        structure_support: bool,
        liquidity_support: bool,
        order_block_support: bool,
    ) -> float:
        score = 0.0

        if structure_support:
            score += 40.0

        if liquidity_support:
            score += 30.0

        if order_block_support:
            score += 30.0

        return score

    @staticmethod
    def _clean_items(
        items: tuple[str, ...],
        *,
        name: str,
    ) -> tuple[str, ...]:
        del name

        if not isinstance(
            items,
            tuple,
        ):
            raise TypeError(
                "evidence and warnings must be tuples."
            )

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

    @property
    def confidence_bonus(self) -> float:
        """
        Directional-confluence alias retained alongside the original
        confidence_adjustment field.
        """
        return self.confidence_adjustment

    @property
    def has_support(self) -> bool:
        return self.agreement_count > 0

    @property
    def has_full_agreement(self) -> bool:
        return (
            self.agreement_count
            == self.domain_count
            and self.conflict_count == 0
        )

    @property
    def has_partial_agreement(self) -> bool:
        return (
            0
            < self.agreement_count
            < self.domain_count
        )

    @property
    def has_no_agreement(self) -> bool:
        return self.agreement_count == 0

    @property
    def has_conflict(self) -> bool:
        return self.conflict_count > 0

    @property
    def has_full_conflict(self) -> bool:
        return (
            self.conflict_count
            == self.domain_count
        )

    @property
    def is_mixed(self) -> bool:
        return (
            self.agreement_count > 0
            and self.conflict_count > 0
        )

    @property
    def directional_count(self) -> int:
        return (
            self.bullish_count
            + self.bearish_count
            + self.neutral_count
            + self.unknown_count
        )

    @property
    def resolved_directional_count(self) -> int:
        return (
            self.bullish_count
            + self.bearish_count
        )

    @property
    def unresolved_count(self) -> int:
        return (
            self.neutral_count
            + self.unknown_count
        )

    @property
    def has_directional_counts(self) -> bool:
        return self.directional_count > 0

    @property
    def is_bullish(self) -> bool:
        return (
            self.dominant_direction
            is InstitutionalDirection.BULLISH
        )

    @property
    def is_bearish(self) -> bool:
        return (
            self.dominant_direction
            is InstitutionalDirection.BEARISH
        )

    @property
    def is_neutral(self) -> bool:
        return (
            self.dominant_direction
            is InstitutionalDirection.NEUTRAL
        )

    @property
    def is_unknown(self) -> bool:
        return (
            self.dominant_direction
            is InstitutionalDirection.UNKNOWN
        )

    @property
    def supporting_domains(
        self,
    ) -> tuple[str, ...]:
        domains: list[str] = []

        if self.structure_support:
            domains.append(
                "STRUCTURE"
            )

        if self.liquidity_support:
            domains.append(
                "LIQUIDITY"
            )

        if self.order_block_support:
            domains.append(
                "ORDER_BLOCK"
            )

        if self.auction_support:
            domains.append(
                "AUCTION"
            )

        if self.pressure_support:
            domains.append(
                "PRESSURE"
            )

        if self.participation_support:
            domains.append(
                "PARTICIPATION"
            )

        if self.value_support:
            domains.append(
                "VALUE"
            )

        return tuple(
            domains
        )

    @classmethod
    def empty(
        cls,
        *,
        evidence: tuple[str, ...] = (),
        warnings: tuple[str, ...] = (),
        directional: bool = False,
        domain_count: int = 3,
    ) -> InstitutionalConfluence:
        """
        Build a zero-agreement confluence result.

        When directional is True, every configured institutional
        domain is represented as UNKNOWN.
        """
        return cls(
            score=0.0,
            structure_support=False,
            liquidity_support=False,
            order_block_support=False,
            agreement_count=0,
            confidence_adjustment=0.0,
            auction_support=False,
            pressure_support=False,
            participation_support=False,
            value_support=False,
            domain_count=domain_count,
            dominant_direction=(
                InstitutionalDirection.UNKNOWN
            ),
            bullish_count=0,
            bearish_count=0,
            neutral_count=0,
            unknown_count=(
                domain_count
                if directional
                else 0
            ),
            conflict_count=0,
            evidence=evidence,
            warnings=warnings,
        )