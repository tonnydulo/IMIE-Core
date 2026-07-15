from __future__ import annotations

from dataclasses import dataclass, field

from imie.directors.liquidity_direction_resolver import (
    LiquidityDirectionResolver,
)
from imie.directors.order_block_direction_resolver import (
    OrderBlockDirectionResolver,
)
from imie.directors.structure_direction_resolver import (
    StructureDirectionResolver,
)
from imie.models import (
    AnalystResult,
    InstitutionalConfluence,
    InstitutionalDirection,
)


@dataclass(frozen=True, slots=True)
class InstitutionalConfluenceEngine:
    """
    Measures directional institutional agreement.

    The engine consumes optional completed analyst results from:

    - Structure
    - Liquidity
    - Order Blocks

    Each result is converted into InstitutionalDirection by its
    dedicated resolver.

    The engine then determines:

    - bullish votes;
    - bearish votes;
    - neutral votes;
    - unknown votes;
    - dominant institutional direction;
    - directional agreement;
    - directional conflict;
    - weighted confluence score;
    - bounded confidence adjustment;
    - evidence and warnings.

    Domain weights:

    - Structure: 40
    - Liquidity: 30
    - Order Blocks: 30

    Confidence adjustments:

    - 0 aligned domains: +0
    - 1 aligned domain: +2
    - 2 aligned domains: +5
    - 3 aligned domains: +8

    The engine does not authorize trades or modify TradePlan.
    """

    structure_weight: float = 40.0
    liquidity_weight: float = 30.0
    order_block_weight: float = 30.0

    structure_resolver: StructureDirectionResolver = field(
        default_factory=StructureDirectionResolver,
    )

    liquidity_resolver: LiquidityDirectionResolver = field(
        default_factory=LiquidityDirectionResolver,
    )

    order_block_resolver: OrderBlockDirectionResolver = field(
        default_factory=OrderBlockDirectionResolver,
    )

    def __post_init__(self) -> None:
        self._validate_weights()
        self._validate_resolvers()

    def evaluate(
        self,
        *,
        structure: AnalystResult | None,
        liquidity: AnalystResult | None,
        order_block: AnalystResult | None,
    ) -> InstitutionalConfluence:
        """
        Evaluate directional institutional confluence.

        Missing and disabled results resolve to UNKNOWN through
        the individual direction resolvers.
        """
        self._validate_optional_result(
            result=structure,
            name="structure",
        )

        self._validate_optional_result(
            result=liquidity,
            name="liquidity",
        )

        self._validate_optional_result(
            result=order_block,
            name="order_block",
        )

        structure_direction = (
            self.structure_resolver.resolve(
                structure
            )
        )

        liquidity_direction = (
            self.liquidity_resolver.resolve(
                liquidity
            )
        )

        order_block_direction = (
            self.order_block_resolver.resolve(
                order_block
            )
        )

        directions = (
            structure_direction,
            liquidity_direction,
            order_block_direction,
        )

        bullish_count = directions.count(
            InstitutionalDirection.BULLISH
        )

        bearish_count = directions.count(
            InstitutionalDirection.BEARISH
        )

        neutral_count = directions.count(
            InstitutionalDirection.NEUTRAL
        )

        unknown_count = directions.count(
            InstitutionalDirection.UNKNOWN
        )

        dominant_direction = (
            self._resolve_dominant_direction(
                bullish_count=bullish_count,
                bearish_count=bearish_count,
                neutral_count=neutral_count,
                unknown_count=unknown_count,
            )
        )

        structure_support = self._aligns(
            direction=structure_direction,
            dominant_direction=dominant_direction,
        )

        liquidity_support = self._aligns(
            direction=liquidity_direction,
            dominant_direction=dominant_direction,
        )

        order_block_support = self._aligns(
            direction=order_block_direction,
            dominant_direction=dominant_direction,
        )

        agreement_count = sum(
            (
                structure_support,
                liquidity_support,
                order_block_support,
            )
        )

        conflict_count = self._calculate_conflict_count(
            dominant_direction=dominant_direction,
            bullish_count=bullish_count,
            bearish_count=bearish_count,
        )

        score = self._calculate_score(
            structure_support=structure_support,
            liquidity_support=liquidity_support,
            order_block_support=order_block_support,
        )

        confidence_adjustment = (
            self._confidence_adjustment(
                agreement_count
            )
        )

        evidence = self._build_evidence(
            structure_direction=structure_direction,
            liquidity_direction=liquidity_direction,
            order_block_direction=order_block_direction,
            dominant_direction=dominant_direction,
            structure_support=structure_support,
            liquidity_support=liquidity_support,
            order_block_support=order_block_support,
            agreement_count=agreement_count,
            conflict_count=conflict_count,
        )

        warnings = self._build_warnings(
            dominant_direction=dominant_direction,
            bullish_count=bullish_count,
            bearish_count=bearish_count,
            agreement_count=agreement_count,
            conflict_count=conflict_count,
        )

        return InstitutionalConfluence(
            score=score,
            structure_support=structure_support,
            liquidity_support=liquidity_support,
            order_block_support=order_block_support,
            agreement_count=agreement_count,
            confidence_adjustment=confidence_adjustment,
            dominant_direction=dominant_direction,
            bullish_count=bullish_count,
            bearish_count=bearish_count,
            neutral_count=neutral_count,
            unknown_count=unknown_count,
            conflict_count=conflict_count,
            evidence=evidence,
            warnings=warnings,
        )

    def _validate_weights(self) -> None:
        weights = (
            (
                "structure_weight",
                self.structure_weight,
            ),
            (
                "liquidity_weight",
                self.liquidity_weight,
            ),
            (
                "order_block_weight",
                self.order_block_weight,
            ),
        )

        for name, value in weights:
            if not isinstance(
                value,
                (
                    int,
                    float,
                ),
            ):
                raise TypeError(
                    f"{name} must be numeric."
                )

            if value < 0.0:
                raise ValueError(
                    f"{name} cannot be negative."
                )

        total_weight = sum(
            float(value)
            for _, value in weights
        )

        if total_weight != 100.0:
            raise ValueError(
                "Institutional confluence weights must total 100."
            )

    def _validate_resolvers(self) -> None:
        if not isinstance(
            self.structure_resolver,
            StructureDirectionResolver,
        ):
            raise TypeError(
                "structure_resolver must be a "
                "StructureDirectionResolver."
            )

        if not isinstance(
            self.liquidity_resolver,
            LiquidityDirectionResolver,
        ):
            raise TypeError(
                "liquidity_resolver must be a "
                "LiquidityDirectionResolver."
            )

        if not isinstance(
            self.order_block_resolver,
            OrderBlockDirectionResolver,
        ):
            raise TypeError(
                "order_block_resolver must be an "
                "OrderBlockDirectionResolver."
            )

    @staticmethod
    def _validate_optional_result(
        *,
        result: AnalystResult | None,
        name: str,
    ) -> None:
        if result is None:
            return

        if not isinstance(
            result,
            AnalystResult,
        ):
            raise TypeError(
                f"{name} must be an AnalystResult or None."
            )

    @staticmethod
    def _resolve_dominant_direction(
        *,
        bullish_count: int,
        bearish_count: int,
        neutral_count: int,
        unknown_count: int,
    ) -> InstitutionalDirection:
        if bullish_count > bearish_count:
            return InstitutionalDirection.BULLISH

        if bearish_count > bullish_count:
            return InstitutionalDirection.BEARISH

        if (
            bullish_count == 0
            and bearish_count == 0
            and neutral_count > 0
            and unknown_count == 0
        ):
            return InstitutionalDirection.NEUTRAL

        return InstitutionalDirection.UNKNOWN

    @staticmethod
    def _aligns(
        *,
        direction: InstitutionalDirection,
        dominant_direction: InstitutionalDirection,
    ) -> bool:
        return direction.aligns_with(
            dominant_direction
        )

    @staticmethod
    def _calculate_conflict_count(
        *,
        dominant_direction: InstitutionalDirection,
        bullish_count: int,
        bearish_count: int,
    ) -> int:
        if (
            dominant_direction
            is InstitutionalDirection.BULLISH
        ):
            return bearish_count

        if (
            dominant_direction
            is InstitutionalDirection.BEARISH
        ):
            return bullish_count

        if (
            dominant_direction
            is InstitutionalDirection.UNKNOWN
            and bullish_count == bearish_count
            and bullish_count > 0
        ):
            return (
                bullish_count
                + bearish_count
            )

        return 0

    def _calculate_score(
        self,
        *,
        structure_support: bool,
        liquidity_support: bool,
        order_block_support: bool,
    ) -> float:
        score = 0.0

        if structure_support:
            score += self.structure_weight

        if liquidity_support:
            score += self.liquidity_weight

        if order_block_support:
            score += self.order_block_weight

        return round(
            float(score),
            2,
        )

    @staticmethod
    def _confidence_adjustment(
        agreement_count: int,
    ) -> float:
        adjustments = {
            0: 0.0,
            1: 2.0,
            2: 5.0,
            3: 8.0,
        }

        return adjustments[
            agreement_count
        ]

    @classmethod
    def _build_evidence(
        cls,
        *,
        structure_direction: InstitutionalDirection,
        liquidity_direction: InstitutionalDirection,
        order_block_direction: InstitutionalDirection,
        dominant_direction: InstitutionalDirection,
        structure_support: bool,
        liquidity_support: bool,
        order_block_support: bool,
        agreement_count: int,
        conflict_count: int,
    ) -> tuple[str, ...]:
        evidence: list[str] = []

        evidence.extend(
            cls._domain_evidence(
                domain="Structure",
                direction=structure_direction,
                dominant_direction=dominant_direction,
                supports=structure_support,
            )
        )

        evidence.extend(
            cls._domain_evidence(
                domain="Liquidity",
                direction=liquidity_direction,
                dominant_direction=dominant_direction,
                supports=liquidity_support,
            )
        )

        evidence.extend(
            cls._domain_evidence(
                domain="Order Blocks",
                direction=order_block_direction,
                dominant_direction=dominant_direction,
                supports=order_block_support,
            )
        )

        if (
            dominant_direction
            is InstitutionalDirection.BULLISH
        ):
            evidence.append(
                "Dominant institutional direction is bullish."
            )

        elif (
            dominant_direction
            is InstitutionalDirection.BEARISH
        ):
            evidence.append(
                "Dominant institutional direction is bearish."
            )

        elif (
            dominant_direction
            is InstitutionalDirection.NEUTRAL
        ):
            evidence.append(
                "Institutional direction is neutral."
            )

        agreement_text = {
            1: (
                "One institutional domain supports the setup."
            ),
            2: (
                "Two institutional domains support the setup."
            ),
            3: (
                "Three institutional domains support the setup."
            ),
        }

        if agreement_count in agreement_text:
            evidence.append(
                agreement_text[
                    agreement_count
                ]
            )

        if conflict_count == 1:
            evidence.append(
                "One institutional domain conflicts with the "
                "dominant direction."
            )

        elif conflict_count > 1:
            evidence.append(
                f"{conflict_count} institutional domains conflict "
                "with directional consensus."
            )

        return cls._clean_items(
            evidence
        )

    @staticmethod
    def _domain_evidence(
        *,
        domain: str,
        direction: InstitutionalDirection,
        dominant_direction: InstitutionalDirection,
        supports: bool,
    ) -> list[str]:
        evidence: list[str] = []

        if (
            direction
            is InstitutionalDirection.BULLISH
        ):
            evidence.append(
                f"{domain} resolves bullish."
            )

        elif (
            direction
            is InstitutionalDirection.BEARISH
        ):
            evidence.append(
                f"{domain} resolves bearish."
            )

        elif (
            direction
            is InstitutionalDirection.NEUTRAL
        ):
            evidence.append(
                f"{domain} is neutral."
            )

        else:
            evidence.append(
                f"{domain} direction is unavailable."
            )

        if supports:
            if domain == "Structure":
                evidence.append(
                    "Structure confirms institutional continuation."
                )

            elif domain == "Liquidity":
                evidence.append(
                    "Liquidity supports institutional continuation."
                )

            elif domain == "Order Blocks":
                evidence.append(
                    "Order Blocks support institutional continuation."
                )

            if (
                dominant_direction
                is InstitutionalDirection.BULLISH
            ):
                evidence.append(
                    f"{domain} supports bullish continuation."
                )

            elif (
                dominant_direction
                is InstitutionalDirection.BEARISH
            ):
                evidence.append(
                    f"{domain} supports bearish continuation."
                )

        elif (
            direction.is_directional
            and dominant_direction.is_directional
        ):
            evidence.append(
                f"{domain} opposes "
                f"{dominant_direction.value.lower()} continuation."
            )

        return evidence

    @classmethod
    def _build_warnings(
        cls,
        *,
        dominant_direction: InstitutionalDirection,
        bullish_count: int,
        bearish_count: int,
        agreement_count: int,
        conflict_count: int,
    ) -> tuple[str, ...]:
        warnings: list[str] = []

        if agreement_count == 0:
            warnings.append(
                "No institutional agreement detected."
            )

        elif agreement_count == 1:
            warnings.append(
                "Only one institutional domain supports the setup."
            )

        if conflict_count > 0:
            warnings.append(
                "Institutional disagreement detected."
            )

        if (
            dominant_direction
            is InstitutionalDirection.UNKNOWN
            and bullish_count > 0
            and bearish_count > 0
        ):
            warnings.append(
                "Bullish and bearish institutional votes are tied."
            )

        return cls._clean_items(
            warnings
        )

    @staticmethod
    def _clean_items(
        items: list[str],
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