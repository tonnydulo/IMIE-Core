from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstitutionalBiasConfig:
    """
    Configuration for InstitutionalBiasEngine domain weighting.

    Default weights:

    - Trend: 25
    - Structure: 20
    - Liquidity: 15
    - Order Blocks: 15
    - Auction: 10
    - Pressure: 5
    - Participation: 5
    - Value: 5

    Total configured weight must equal 100.

    The configuration also defines the minimum weighted score
    separation required to classify the final bias as directional.

    If the bullish and bearish score difference is smaller than
    minimum_directional_spread, the Bias Engine should classify
    the result as neutral rather than directional.
    """

    trend_weight: float = 25.0
    structure_weight: float = 20.0
    liquidity_weight: float = 15.0
    order_block_weight: float = 15.0

    auction_weight: float = 10.0
    pressure_weight: float = 5.0
    participation_weight: float = 5.0
    value_weight: float = 5.0

    minimum_directional_spread: float = 5.0
    minimum_bias_confidence: float = 40.0

    def __post_init__(self) -> None:
        normalized_weights = {
            name: self._normalize_percentage(
                value=value,
                name=name,
            )
            for name, value in self._weight_items()
        }

        minimum_directional_spread = (
            self._normalize_percentage(
                value=self.minimum_directional_spread,
                name="minimum_directional_spread",
            )
        )

        minimum_bias_confidence = (
            self._normalize_percentage(
                value=self.minimum_bias_confidence,
                name="minimum_bias_confidence",
            )
        )

        for name, value in normalized_weights.items():
            object.__setattr__(
                self,
                name,
                value,
            )

        object.__setattr__(
            self,
            "minimum_directional_spread",
            minimum_directional_spread,
        )

        object.__setattr__(
            self,
            "minimum_bias_confidence",
            minimum_bias_confidence,
        )

        self._validate_total_weight()

    def _weight_items(
        self,
    ) -> tuple[
        tuple[str, float],
        ...,
    ]:
        return (
            (
                "trend_weight",
                self.trend_weight,
            ),
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
            (
                "auction_weight",
                self.auction_weight,
            ),
            (
                "pressure_weight",
                self.pressure_weight,
            ),
            (
                "participation_weight",
                self.participation_weight,
            ),
            (
                "value_weight",
                self.value_weight,
            ),
        )

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

    def _validate_total_weight(
        self,
    ) -> None:
        total = self.total_weight

        if total != 100.0:
            raise ValueError(
                "Institutional bias weights must total 100."
            )

    @property
    def total_weight(self) -> float:
        return round(
            sum(
                value
                for _, value in self._weight_items()
            ),
            2,
        )

    @property
    def core_weight(self) -> float:
        """
        Total weight assigned to existing core directional domains.
        """
        return round(
            (
                self.trend_weight
                + self.structure_weight
                + self.liquidity_weight
                + self.order_block_weight
            ),
            2,
        )

    @property
    def extended_weight(self) -> float:
        """
        Total weight assigned to extended institutional domains.
        """
        return round(
            (
                self.auction_weight
                + self.pressure_weight
                + self.participation_weight
                + self.value_weight
            ),
            2,
        )

    @property
    def weights(
        self,
    ) -> dict[str, float]:
        """
        Return a new mapping of stable domain identifiers to weights.
        """
        return {
            "TREND": self.trend_weight,
            "STRUCTURE": self.structure_weight,
            "LIQUIDITY": self.liquidity_weight,
            "ORDER_BLOCK": self.order_block_weight,
            "AUCTION": self.auction_weight,
            "PRESSURE": self.pressure_weight,
            "PARTICIPATION": self.participation_weight,
            "VALUE": self.value_weight,
        }

    @property
    def domains(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            self.weights
        )

    def weight_for(
        self,
        domain: str,
    ) -> float:
        """
        Return the configured weight for a stable domain identifier.
        """
        if not isinstance(
            domain,
            str,
        ):
            raise TypeError(
                "domain must be a string."
            )

        normalized = domain.strip().upper()

        if not normalized:
            raise ValueError(
                "domain cannot be empty."
            )

        weights = self.weights

        if normalized not in weights:
            raise KeyError(
                f"Unknown institutional bias domain: {normalized}."
            )

        return weights[
            normalized
        ]

    def is_core_domain(
        self,
        domain: str,
    ) -> bool:
        normalized = self._normalize_domain(
            domain
        )

        return normalized in {
            "TREND",
            "STRUCTURE",
            "LIQUIDITY",
            "ORDER_BLOCK",
        }

    def is_extended_domain(
        self,
        domain: str,
    ) -> bool:
        normalized = self._normalize_domain(
            domain
        )

        return normalized in {
            "AUCTION",
            "PRESSURE",
            "PARTICIPATION",
            "VALUE",
        }

    def has_weight(
        self,
        domain: str,
    ) -> bool:
        normalized = self._normalize_domain(
            domain
        )

        return (
            normalized in self.weights
            and self.weights[
                normalized
            ] > 0.0
        )

    @staticmethod
    def _normalize_domain(
        domain: object,
    ) -> str:
        if not isinstance(
            domain,
            str,
        ):
            raise TypeError(
                "domain must be a string."
            )

        normalized = domain.strip().upper()

        if not normalized:
            raise ValueError(
                "domain cannot be empty."
            )

        return normalized