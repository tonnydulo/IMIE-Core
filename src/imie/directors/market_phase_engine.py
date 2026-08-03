from __future__ import annotations

from dataclasses import dataclass, field

from imie.directors.market_phase_config import (
    MarketPhaseConfig,
)
from imie.directors.market_phase_resolver import (
    MarketPhaseResolver,
)
from imie.models import (
    AnalystResult,
    MarketPhase,
    MarketPhaseDomain,
    MarketPhaseType,
     MarketPhaseVote,
)


@dataclass(frozen=True)
class MarketPhaseEngine:
    """
    Determines the current institutional market phase.

    This implementation establishes the public API and builds
    normalized domain contributions.

    Phase voting and consensus are introduced in later modules.
    """

    config: MarketPhaseConfig = field(
        default_factory=MarketPhaseConfig
    )

    resolver: MarketPhaseResolver = field(
        default_factory=MarketPhaseResolver
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.config,
            MarketPhaseConfig,
        ):
            raise TypeError(
                "config must be a MarketPhaseConfig."
            )

        if not isinstance(
            self.resolver,
            MarketPhaseResolver,
        ):
            raise TypeError(
                "resolver must be a MarketPhaseResolver."
            )

    def evaluate(
        self,
        *,
        trend: AnalystResult | None = None,
        structure: AnalystResult | None = None,
        liquidity: AnalystResult | None = None,
        order_block: AnalystResult | None = None,
        auction: AnalystResult | None = None,
        pressure: AnalystResult | None = None,
        participation: AnalystResult | None = None,
        value: AnalystResult | None = None,
    ) -> MarketPhase:
        """
        Evaluate the current institutional market phase.

        Builds normalized domain contributions, collects weighted
        phase votes, and resolves the dominant market phase.
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
            ),
            self._build_domain(
                domain="STRUCTURE",
                result=structure,
            ),
            self._build_domain(
                domain="LIQUIDITY",
                result=liquidity,
            ),
            self._build_domain(
                domain="ORDER_BLOCK",
                result=order_block,
            ),
            self._build_domain(
                domain="AUCTION",
                result=auction,
            ),
            self._build_domain(
                domain="PRESSURE",
                result=pressure,
            ),
            self._build_domain(
                domain="PARTICIPATION",
                result=participation,
            ),
            self._build_domain(
                domain="VALUE",
                result=value,
            ),
        )

        phase_scores = self._collect_phase_votes(
            domains=domains,
        )

        phase = self._select_phase(
            phase_scores=phase_scores,
        )

        strength = self._strength(
            phase_scores=phase_scores,
        )

        confidence = self._confidence(
            phase_scores=phase_scores,
        )

        if phase_scores:
            highest_score = phase_scores[0].score

            leading_phases = tuple(
                vote.phase
                for vote in phase_scores
                if vote.score == highest_score
            )
        else:
            leading_phases = ()

        supporting_domains = tuple(
            domain.domain
            for domain in domains
            if (
                domain.is_known
                and not domain.is_disabled
                and domain.phase in leading_phases
            )
        )

        opposing_domains = tuple(
            domain.domain
            for domain in domains
            if (
                domain.is_known
                and not domain.is_disabled
                and domain.phase not in leading_phases
            )
        )

        neutral_domains: tuple[str, ...] = ()

        agreement_count = len(
            supporting_domains
        )

        conflict_count = len(
            opposing_domains
        )

        unknown_domains = tuple(
            domain.domain
            for domain in domains
            if (
                domain.is_unknown
                or domain.is_disabled
            )
        )

        evidence = (
            (
                f"Dominant market phase is "
                f"{phase.value.lower()}."
            ),
            (
                f"Market phase strength is "
                f"{strength:.2f}."
            ),
            (
                f"Market phase confidence is "
                f"{confidence:.2f}."
            ),
            (
                f"Market phase agreement count is "
                f"{agreement_count}."
            ),
            (
                f"Market phase conflict count is "
                f"{conflict_count}."
            ),
        )

        warnings: tuple[str, ...] = ()

        if phase is MarketPhaseType.UNKNOWN:
            warnings = (
                "No resolved market phase votes are available.",
            )

        elif phase is MarketPhaseType.TRANSITION:
            warnings = (
                "Multiple market phases share the highest score.",
            )

        unknown_domains = tuple(
            domain.domain
            for domain in domains
            if (
                domain.is_unknown
                or domain.is_disabled
            )
        )

        return MarketPhase(
            phase=phase,
            confidence=confidence,
            strength=strength,
            phase_scores=phase_scores,
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
    ) -> MarketPhaseDomain:
        """
        Build a normalized MarketPhaseDomain.
        """

        weight = self.config.weight_for(
            domain
        )

        display_name = self._display_name(
            domain
        )

        if result is None:
            return MarketPhaseDomain.unknown(
                domain=domain,
                weight=weight,
                warnings=(
                    f"{display_name} result is missing.",
                ),
            )

        if not result.enabled:
            return MarketPhaseDomain.disabled(
                domain=domain,
                weight=weight,
                warnings=(
                    f"{display_name} is disabled.",
                ),
            )

        phase = self.resolver.resolve(
            result
        )

        warnings = list(
            result.warnings
        )

        if phase is MarketPhaseType.UNKNOWN:
            warnings.append(
                f"{display_name} did not provide a resolved phase."
            )

        return MarketPhaseDomain.create(
            domain=domain,
            phase=phase,
            weight=weight,
            confidence=result.confidence,
            enabled=True,
            evidence=result.evidence,
            warnings=self._clean_items(
                warnings
            ),
        )

    def _collect_phase_votes(
        self,
        *,
        domains: tuple[
            MarketPhaseDomain,
            ...,
        ],
    ) -> tuple[
        MarketPhaseVote,
        ...,
    ]:
        """
        Collect weighted support for each market phase.
        """

        totals: dict[
            MarketPhaseType,
            float,
        ] = {}

        for domain in domains:
            if (
                domain.is_unknown
                or domain.is_disabled
            ):
                continue

            totals.setdefault(
                domain.phase,
                0.0,
            )

            totals[
                domain.phase
            ] += domain.weighted_score

        return tuple(
            sorted(
                (
                    MarketPhaseVote(
                        phase=phase,
                        score=round(
                            score,
                            2,
                        ),
                    )
                    for phase, score
                    in totals.items()
                ),
                key=lambda vote: (
                    vote.score,
                    vote.phase.value,
                ),
                reverse=True,
            )
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
    
    def _select_phase(
        self,
        *,
        phase_scores: tuple[
            MarketPhaseVote,
            ...,
        ],
    ) -> MarketPhaseType:
        """
        Select the dominant market phase.

        Returns TRANSITION when multiple phases share the
        highest weighted score.
        """

        if not phase_scores:
            return MarketPhaseType.UNKNOWN

        highest = phase_scores[0].score

        winners = tuple(
            vote
            for vote in phase_scores
            if vote.score == highest
        )

        if len(winners) > 1:
            return MarketPhaseType.TRANSITION

        return winners[0].phase
    
    def _strength(
        self,
        *,
        phase_scores: tuple[
            MarketPhaseVote,
            ...,
        ],
    ) -> float:
        if not phase_scores:
            return 0.0

        return phase_scores[0].score
    
    def _confidence(
        self,
        *,
        phase_scores: tuple[
            MarketPhaseVote,
            ...,
        ],
    ) -> float:
        if not phase_scores:
            return 0.0

        total = sum(
            vote.score
            for vote in phase_scores
        )

        if total <= 0.0:
            return 0.0

        return round(
            phase_scores[0].score
            / total
            * 100.0,
            2,
        )