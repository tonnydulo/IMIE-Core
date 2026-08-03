from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketPhaseConfig:
    """
    Configuration for the Market Phase Engine.
    """

    structure_weight: float = 25.0
    auction_weight: float = 20.0
    liquidity_weight: float = 15.0
    pressure_weight: float = 10.0
    participation_weight: float = 10.0
    order_block_weight: float = 10.0
    trend_weight: float = 5.0
    value_weight: float = 5.0

    minimum_phase_confidence: float = 60.0
    minimum_phase_agreement: int = 3

    def __post_init__(self) -> None:
        weights = (
            self.structure_weight,
            self.auction_weight,
            self.liquidity_weight,
            self.pressure_weight,
            self.participation_weight,
            self.order_block_weight,
            self.trend_weight,
            self.value_weight,
        )

        if any(weight < 0.0 for weight in weights):
            raise ValueError(
                "Market phase weights must be non-negative."
            )

        total = round(sum(weights), 2)

        if total != 100.0:
            raise ValueError(
                "Market phase weights must total 100."
            )

        if not (
            0.0
            <= self.minimum_phase_confidence
            <= 100.0
        ):
            raise ValueError(
                "minimum_phase_confidence must be between "
                "0 and 100."
            )

        if self.minimum_phase_agreement < 1:
            raise ValueError(
                "minimum_phase_agreement must be at least 1."
            )

    def weight_for(
        self,
        domain: str,
    ) -> float:
        weights = {
            "STRUCTURE": self.structure_weight,
            "AUCTION": self.auction_weight,
            "LIQUIDITY": self.liquidity_weight,
            "PRESSURE": self.pressure_weight,
            "PARTICIPATION": self.participation_weight,
            "ORDER_BLOCK": self.order_block_weight,
            "TREND": self.trend_weight,
            "VALUE": self.value_weight,
        }

        try:
            return weights[
                domain.upper()
            ]

        except KeyError as exc:
            raise ValueError(
                f"Unknown market phase domain: {domain}"
            ) from exc