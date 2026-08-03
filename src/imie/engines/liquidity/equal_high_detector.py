from __future__ import annotations

from dataclasses import dataclass

from imie.models.liquidity_finding import LiquidityFinding
from imie.models.liquidity_point import LiquidityPoint
from imie.models.liquidity_types import (
    LiquidityImportance,
    LiquidityLocation,
    LiquiditySide,
    LiquidityState,
    LiquidityType,
)
from imie.models.swing import Swing


@dataclass(frozen=True, slots=True)
class EqualHighDetector:
    """
    Detects confirmed equal-high liquidity from swing highs.

    The detector compares every eligible pair of confirmed swing
    highs rather than only adjacent highs.

    Responsibilities:
    - identify swing-high pairs within the configured tolerance;
    - enforce a minimum bar separation;
    - derive liquidity strength from the contributing swings;
    - calculate an explainable confidence score;
    - emit immutable LiquidityFinding objects.

    The detector does not:
    - detect swings;
    - build liquidity pools;
    - detect sweeps;
    - rank targets;
    - make trading decisions.
    """

    tolerance: float = 0.05
    min_separation: int = 2
    ideal_separation: int = 10

    def __post_init__(self) -> None:
        if self.tolerance < 0.0:
            raise ValueError(
                "EqualHighDetector tolerance cannot be negative."
            )

        if self.min_separation < 1:
            raise ValueError(
                "EqualHighDetector min_separation must be at least 1."
            )

        if self.ideal_separation < self.min_separation:
            raise ValueError(
                "EqualHighDetector ideal_separation cannot be less "
                "than min_separation."
            )

    def detect(
        self,
        swings: tuple[Swing, ...],
    ) -> tuple[LiquidityFinding, ...]:
        """
        Detect equal-high liquidity from confirmed swings.

        All confirmed HIGH swings are compared with later HIGH swings.
        Each valid pair produces one LiquidityFinding. Consolidation
        of overlapping findings belongs to LiquidityPoolBuilder.
        """
        high_swings = tuple(
            sorted(
                (
                    swing
                    for swing in swings
                    if swing.kind == "HIGH"
                ),
                key=lambda swing: swing.index,
            )
        )

        if len(high_swings) < 2:
            return ()

        findings: list[LiquidityFinding] = []

        for first_position in range(len(high_swings) - 1):
            first = high_swings[first_position]

            for second_position in range(
                first_position + 1,
                len(high_swings),
            ):
                second = high_swings[second_position]

                if not self._is_equal_high_pair(
                    first=first,
                    second=second,
                ):
                    continue

                findings.append(
                    self._build_finding(
                        first=first,
                        second=second,
                    )
                )

        return tuple(findings)

    def _is_equal_high_pair(
        self,
        *,
        first: Swing,
        second: Swing,
    ) -> bool:
        separation = second.index - first.index

        if separation < self.min_separation:
            return False

        price_difference = abs(
            second.price - first.price
        )

        return price_difference <= self.tolerance

    def _build_finding(
        self,
        *,
        first: Swing,
        second: Swing,
    ) -> LiquidityFinding:
        price_difference = abs(
            second.price - first.price
        )

        separation = second.index - first.index

        midpoint = (
            first.price + second.price
        ) / 2.0

        strength = self._calculate_strength(
            first=first,
            second=second,
        )

        confidence = self._calculate_confidence(
            price_difference=price_difference,
            first_strength=first.strength,
            second_strength=second.strength,
            separation=separation,
        )

        point = LiquidityPoint(
            price=midpoint,
            side=LiquiditySide.BUY_SIDE,
            first_index=first.index,
            second_index=second.index,
            strength=strength,
        )

        return LiquidityFinding(
            point=point,
            liquidity_type=LiquidityType.EQUAL_HIGH,
            importance=LiquidityImportance.MINOR,
            location=LiquidityLocation.UNCLASSIFIED,
            confidence=confidence,
            state=LiquidityState.ACTIVE,
            reason=(
                "Two confirmed swing highs formed within "
                f"{price_difference:.4f} of one another across "
                f"{separation} bars, creating resting buy-side "
                "liquidity."
            ),
            evidence=(
                (
                    "First confirmed swing high occurred at "
                    f"{first.price:.4f} on index {first.index} "
                    f"with strength {first.strength}."
                ),
                (
                    "Second confirmed swing high occurred at "
                    f"{second.price:.4f} on index {second.index} "
                    f"with strength {second.strength}."
                ),
                (
                    "The price difference was "
                    f"{price_difference:.4f}, within the configured "
                    f"tolerance of {self.tolerance:.4f}."
                ),
                (
                    "The swing highs were separated by "
                    f"{separation} bars."
                ),
            ),
            source=self.__class__.__name__,
        )

    @staticmethod
    def _calculate_strength(
        *,
        first: Swing,
        second: Swing,
    ) -> int:
        """
        Derive liquidity strength from both contributing swings.

        The rounded average preserves the original integer model while
        allowing stronger structural swings to create stronger points.
        """
        average_strength = (
            first.strength + second.strength
        ) / 2.0

        return max(
            1,
            round(average_strength),
        )

    def _calculate_confidence(
        self,
        *,
        price_difference: float,
        first_strength: int,
        second_strength: int,
        separation: int,
    ) -> float:
        """
        Calculate confidence from three independent dimensions:

        - price precision: how closely the highs match;
        - swing quality: strength of both confirmed swings;
        - separation quality: sufficient spacing between observations.

        Confidence is normalized to the range 0 through 100.
        """
        precision_score = self._precision_score(
            price_difference=price_difference,
        )

        strength_score = self._strength_score(
            first_strength=first_strength,
            second_strength=second_strength,
        )

        separation_score = self._separation_score(
            separation=separation,
        )

        confidence = (
            precision_score * 0.55
            + strength_score * 0.30
            + separation_score * 0.15
        )

        return round(
            max(0.0, min(100.0, confidence)),
            2,
        )

    def _precision_score(
        self,
        *,
        price_difference: float,
    ) -> float:
        if self.tolerance == 0.0:
            return (
                100.0
                if price_difference == 0.0
                else 0.0
            )

        precision_ratio = 1.0 - (
            price_difference / self.tolerance
        )

        return max(
            0.0,
            min(100.0, precision_ratio * 100.0),
        )

    @staticmethod
    def _strength_score(
        *,
        first_strength: int,
        second_strength: int,
    ) -> float:
        """
        Normalize swing strength using 5 as the current full-strength
        reference point.

        Strengths above 5 remain capped at 100.
        """
        average_strength = (
            first_strength + second_strength
        ) / 2.0

        return min(
            100.0,
            average_strength / 5.0 * 100.0,
        )

    def _separation_score(
        self,
        *,
        separation: int,
    ) -> float:
        if separation >= self.ideal_separation:
            return 100.0

        usable_range = (
            self.ideal_separation
            - self.min_separation
        )

        if usable_range == 0:
            return 100.0

        progress = (
            separation - self.min_separation
        ) / usable_range

        return max(
            50.0,
            min(100.0, 50.0 + progress * 50.0),
        )