
from __future__ import annotations

from dataclasses import dataclass, field

from imie.directors.institutional_bias_config import (
    InstitutionalBiasConfig,
)
from imie.directors.liquidity_direction_resolver import (
    LiquidityDirectionResolver,
)
from imie.directors.order_block_direction_resolver import (
    OrderBlockDirectionResolver,
)
from imie.directors.structure_direction_resolver import (
    StructureDirectionResolver,
)
from imie.directors.trend_direction_resolver import (
    TrendDirectionResolver,
)
from imie.directors.extended_bias_direction_resolver import (
    ExtendedBiasDirectionResolver,
)
from imie.models import (
    AnalystResult,
    InstitutionalBias,
    InstitutionalBiasDomain,
    InstitutionalDirection,
)


@dataclass(frozen=True, slots=True)
class InstitutionalBiasEngine:
    """
    Produces the broader institutional market bias.

    Core directional domains:

    - Trend
    - Structure
    - Liquidity
    - Order Blocks

    Extended domains remain unresolved in this version:

    - Auction
    - Pressure
    - Participation
    - Value

    Each completed analyst result is normalized by its dedicated
    direction resolver and converted into an
    InstitutionalBiasDomain contribution.

    Directional scores are calculated as:

        domain weight * analyst confidence / 100

    Bullish and bearish contributions are accumulated separately.

    The final direction is:

    - BULLISH when bullish score exceeds bearish score;
    - BEARISH when bearish score exceeds bullish score;
    - NEUTRAL when non-zero scores are exactly equal;
    - UNKNOWN when no directional score is available.

    The configured minimum directional spread is used as a bias
    quality threshold. A directional result below the threshold is
    retained, but a warning is issued and confidence is reduced.

    The engine does not authorize trades, modify TradePlan, or
    replace InstitutionalConfluence.
    """

    config: InstitutionalBiasConfig = field(
        default_factory=InstitutionalBiasConfig
    )

    trend_resolver: TrendDirectionResolver = field(
        default_factory=TrendDirectionResolver
    )

    structure_resolver: StructureDirectionResolver = field(
        default_factory=StructureDirectionResolver
    )

    liquidity_resolver: LiquidityDirectionResolver = field(
        default_factory=LiquidityDirectionResolver
    )

    order_block_resolver: OrderBlockDirectionResolver = field(
        default_factory=OrderBlockDirectionResolver
    )
    extended_resolver: ExtendedBiasDirectionResolver = field(
        default_factory=ExtendedBiasDirectionResolver
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.config,
            InstitutionalBiasConfig,
        ):
            raise TypeError(
                "config must be an InstitutionalBiasConfig."
            )

        if not isinstance(
            self.trend_resolver,
            TrendDirectionResolver,
        ):
            raise TypeError(
                "trend_resolver must be a "
                "TrendDirectionResolver."
            )

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
        if not isinstance(
            self.extended_resolver,
            ExtendedBiasDirectionResolver,
        ):
            raise TypeError(
                "extended_resolver must be an "
                "ExtendedBiasDirectionResolver."
    )

    def evaluate(
        self,
        *,
        trend: AnalystResult | None,
        structure: AnalystResult | None,
        liquidity: AnalystResult | None,
        order_block: AnalystResult | None,
        auction: AnalystResult | None = None,
        pressure: AnalystResult | None = None,
        participation: AnalystResult | None = None,
        value: AnalystResult | None = None,
    ) -> InstitutionalBias:
        
        """
        Evaluate the current core institutional bias.
        """
        self._validate_optional_result(
            result=trend,
            name="trend",
        )

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
        self._validate_optional_result(
            result=auction,
            name="auction",
        )

        self._validate_optional_result(
            result=pressure,
            name="pressure",
        )

        self._validate_optional_result(
            result=participation,
            name="participation",
        )

        self._validate_optional_result(
            result=value,
            name="value",
        )

        domains = (
            self._build_domain(
                domain="TREND",
                result=trend,
                direction=(
                    self.trend_resolver.resolve(
                        trend
                    )
                ),
            ),
            self._build_domain(
                domain="STRUCTURE",
                result=structure,
                direction=(
                    self.structure_resolver.resolve(
                        structure
                    )
                ),
            ),
            self._build_domain(
                domain="LIQUIDITY",
                result=liquidity,
                direction=(
                    self.liquidity_resolver.resolve(
                        liquidity
                    )
                ),
            ),
            self._build_domain(
                domain="ORDER_BLOCK",
                result=order_block,
                direction=(
                    self.order_block_resolver.resolve(
                        order_block
                    )
                ),
            ),
            self._build_domain(
                domain="AUCTION",
                result=auction,
                direction=self.extended_resolver.resolve(
                    domain="AUCTION",
                    result=auction,
                ),
            ),
            self._build_domain(
                domain="PRESSURE",
                result=pressure,
                direction=self.extended_resolver.resolve(
                    domain="PRESSURE",
                    result=pressure,
                ),
            ),
            self._build_domain(
                domain="PARTICIPATION",
                result=participation,
                direction=self.extended_resolver.resolve(
                    domain="PARTICIPATION",
                    result=participation,
                ),
            ),
            self._build_domain(
                domain="VALUE",
                result=value,
                direction=self.extended_resolver.resolve(
                    domain="VALUE",
                    result=value,
                ),
            ),
        )

        bullish_score = round(
            sum(
                domain.bullish_contribution
                for domain in domains
            ),
            2,
        )

        bearish_score = round(
            sum(
                domain.bearish_contribution
                for domain in domains
            ),
            2,
        )

        direction = self._resolve_direction(
            bullish_score=bullish_score,
            bearish_score=bearish_score,
        )

        (
            supporting_domains,
            opposing_domains,
            neutral_domains,
            unknown_domains,
        ) = self._classify_domains(
            domains=domains,
            direction=direction,
        )

        agreement_count = len(
            supporting_domains
        )

        conflict_count = len(
            opposing_domains
        )

        strength = round(
            abs(
                bullish_score
                - bearish_score
            ),
            2,
        )

        confidence = self._calculate_confidence(
            domains=domains,
            direction=direction,
            agreement_count=agreement_count,
            conflict_count=conflict_count,
            strength=strength,
        )

        evidence = self._build_evidence(
            domains=domains,
            direction=direction,
            bullish_score=bullish_score,
            bearish_score=bearish_score,
            strength=strength,
            agreement_count=agreement_count,
            conflict_count=conflict_count,
        )

        warnings = self._build_warnings(
            domains=domains,
            direction=direction,
            strength=strength,
            confidence=confidence,
            conflict_count=conflict_count,
        )

        return InstitutionalBias(
            direction=direction,
            strength=strength,
            confidence=confidence,
            bullish_score=bullish_score,
            bearish_score=bearish_score,
            agreement_count=agreement_count,
            conflict_count=conflict_count,
            supporting_domains=supporting_domains,
            opposing_domains=opposing_domains,
            neutral_domains=neutral_domains,
            unknown_domains=unknown_domains,
            evidence=evidence,
            warnings=warnings,
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

    def _build_domain(
        self,
        *,
        domain: str,
        result: AnalystResult | None,
        direction: InstitutionalDirection,
    ) -> InstitutionalBiasDomain:
        weight = self.config.weight_for(
            domain
        )

        if result is None:
            return InstitutionalBiasDomain.unknown(
                domain=domain,
                weight=weight,
                warnings=(
                    f"{self._display_name(domain)} result is missing.",
                ),
            )

        if not result.enabled:
            return InstitutionalBiasDomain.disabled(
                domain=domain,
                weight=weight,
                warnings=(
                    f"{self._display_name(domain)} is disabled.",
                ),
            )

        evidence = self._domain_evidence(
            domain=domain,
            result=result,
            direction=direction,
        )

        warnings = self._domain_warnings(
            domain=domain,
            result=result,
            direction=direction,
        )

        return InstitutionalBiasDomain.create(
            domain=domain,
            direction=direction,
            weight=weight,
            confidence=result.confidence,
            enabled=True,
            evidence=evidence,
            warnings=warnings,
        )

    def _extended_unknown_domain(
        self,
        domain: str,
    ) -> InstitutionalBiasDomain:
        return InstitutionalBiasDomain.unknown(
            domain=domain,
            weight=self.config.weight_for(
                domain
            ),
            warnings=(
                (
                    f"{self._display_name(domain)} bias integration "
                    "is not active in the core engine."
                ),
            ),
        )

    @staticmethod
    def _resolve_direction(
        *,
        bullish_score: float,
        bearish_score: float,
    ) -> InstitutionalDirection:
        if (
            bullish_score == 0.0
            and bearish_score == 0.0
        ):
            return InstitutionalDirection.UNKNOWN

        if bullish_score > bearish_score:
            return InstitutionalDirection.BULLISH

        if bearish_score > bullish_score:
            return InstitutionalDirection.BEARISH

        return InstitutionalDirection.NEUTRAL

    @staticmethod
    def _classify_domains(
        *,
        domains: tuple[
            InstitutionalBiasDomain,
            ...,
        ],
        direction: InstitutionalDirection,
    ) -> tuple[
        tuple[str, ...],
        tuple[str, ...],
        tuple[str, ...],
        tuple[str, ...],
    ]:
        supporting: list[str] = []
        opposing: list[str] = []
        neutral: list[str] = []
        unknown: list[str] = []

        for domain in domains:
            if (
                domain.is_disabled
                or domain.is_unknown
            ):
                unknown.append(
                    domain.domain
                )
                continue

            if domain.is_neutral:
                neutral.append(
                    domain.domain
                )
                continue

            if not direction.is_directional:
                neutral.append(
                    domain.domain
                )
                continue

            if domain.direction.aligns_with(
                direction
            ):
                supporting.append(
                    domain.domain
                )

            elif domain.direction.opposes(
                direction
            ):
                opposing.append(
                    domain.domain
                )

        return (
            tuple(
                supporting
            ),
            tuple(
                opposing
            ),
            tuple(
                neutral
            ),
            tuple(
                unknown
            ),
        )

    def _calculate_confidence(
        self,
        *,
        domains: tuple[
            InstitutionalBiasDomain,
            ...,
        ],
        direction: InstitutionalDirection,
        agreement_count: int,
        conflict_count: int,
        strength: float,
    ) -> float:
        if not direction.is_directional:
            return 0.0

        directional_domains = tuple(
            domain
            for domain in domains
            if domain.is_directional
        )

        if not directional_domains:
            return 0.0

        directional_weight = sum(
            domain.weight
            for domain in directional_domains
        )

        if directional_weight <= 0.0:
            return 0.0

        weighted_confidence = (
            sum(
                domain.weighted_score
                for domain in directional_domains
            )
            / directional_weight
            * 100.0
        )

        directional_count = (
            agreement_count
            + conflict_count
        )

        if directional_count <= 0:
            return 0.0

        agreement_ratio = (
            agreement_count
            / directional_count
        )

        confidence = (
            weighted_confidence
            * agreement_ratio
        )

        if (
            strength
            < self.config.minimum_directional_spread
        ):
            spread_ratio = (
                strength
                / self.config.minimum_directional_spread
            )

            confidence *= spread_ratio

        return round(
            max(
                0.0,
                min(
                    100.0,
                    confidence,
                ),
            ),
            2,
        )

    def _build_evidence(
        self,
        *,
        domains: tuple[
            InstitutionalBiasDomain,
            ...,
        ],
        direction: InstitutionalDirection,
        bullish_score: float,
        bearish_score: float,
        strength: float,
        agreement_count: int,
        conflict_count: int,
    ) -> tuple[str, ...]:
        evidence: list[str] = []

        for domain in domains:
            evidence.extend(
                domain.evidence
            )

        if direction.is_directional:
            evidence.append(
                "Dominant institutional bias is "
                f"{direction.value.lower()}."
            )

        elif (
            direction
            is InstitutionalDirection.NEUTRAL
        ):
            evidence.append(
                "Institutional bias is neutral."
            )

        else:
            evidence.append(
                "Institutional bias is unresolved."
            )

        evidence.extend(
            (
                (
                    "Bullish institutional score is "
                    f"{bullish_score:.2f}."
                ),
                (
                    "Bearish institutional score is "
                    f"{bearish_score:.2f}."
                ),
                (
                    "Institutional score spread is "
                    f"{strength:.2f}."
                ),
                (
                    "Institutional agreement count is "
                    f"{agreement_count}."
                ),
                (
                    "Institutional conflict count is "
                    f"{conflict_count}."
                ),
            )
        )

        return self._clean_items(
            evidence
        )

    def _build_warnings(
        self,
        *,
        domains: tuple[
            InstitutionalBiasDomain,
            ...,
        ],
        direction: InstitutionalDirection,
        strength: float,
        confidence: float,
        conflict_count: int,
    ) -> tuple[str, ...]:
        warnings: list[str] = []

        for domain in domains:
            warnings.extend(
                domain.warnings
            )

        if (
            direction
            is InstitutionalDirection.UNKNOWN
        ):
            warnings.append(
                "No directional institutional bias is available."
            )

        elif (
            direction
            is InstitutionalDirection.NEUTRAL
        ):
            warnings.append(
                "Bullish and bearish institutional scores are tied."
            )

        if (
            direction.is_directional
            and strength
            < self.config.minimum_directional_spread
        ):
            warnings.append(
                "Institutional score spread is below the configured "
                "directional quality threshold."
            )

        if conflict_count > 0:
            warnings.append(
                "Institutional domains conflict with the dominant "
                "bias."
            )

        if (
            direction.is_directional
            and confidence
            < self.config.minimum_bias_confidence
        ):
            warnings.append(
                "Institutional bias confidence is below the "
                "configured minimum."
            )

        return self._clean_items(
            warnings
        )

    @staticmethod
    def _domain_evidence(
        *,
        domain: str,
        result: AnalystResult,
        direction: InstitutionalDirection,
    ) -> tuple[str, ...]:
        evidence: list[str] = list(
            result.evidence
        )

        display_name = (
            InstitutionalBiasEngine._display_name(
                domain
            )
        )

        if direction.is_directional:
            evidence.append(
                f"{display_name} resolves "
                f"{direction.value.lower()}."
            )

        elif (
            direction
            is InstitutionalDirection.NEUTRAL
        ):
            evidence.append(
                f"{display_name} is neutral."
            )

        else:
            evidence.append(
                f"{display_name} direction is unresolved."
            )

        return InstitutionalBiasEngine._clean_items(
            evidence
        )

    @staticmethod
    def _domain_warnings(
        *,
        domain: str,
        result: AnalystResult,
        direction: InstitutionalDirection,
    ) -> tuple[str, ...]:
        warnings: list[str] = list(
            result.warnings
        )

        if (
            direction
            is InstitutionalDirection.UNKNOWN
        ):
            warnings.append(
                (
                    f"{InstitutionalBiasEngine._display_name(domain)} "
                    "did not provide a resolved direction."
                )
            )

        return InstitutionalBiasEngine._clean_items(
            warnings
        )

    @staticmethod
    def _display_name(
        domain: str,
    ) -> str:
        names = {
            "TREND": "Trend",
            "STRUCTURE": "Structure",
            "LIQUIDITY": "Liquidity",
            "ORDER_BLOCK": "Order Blocks",
            "AUCTION": "Auction",
            "PRESSURE": "Pressure",
            "PARTICIPATION": "Participation",
            "VALUE": "Value",
        }

        return names.get(
            domain,
            domain.replace(
                "_",
                " ",
            ).title(),
        )

    @staticmethod
    def _clean_items(
        items,
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