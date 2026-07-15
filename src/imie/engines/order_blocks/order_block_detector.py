from __future__ import annotations

from dataclasses import dataclass, field

from imie.engines.order_blocks.displacement_scorer import (
    DisplacementScorer,
)
from imie.engines.order_blocks.order_block_builder import (
    OrderBlockBuilder,
)
from imie.engines.order_blocks.order_block_candidate import (
    OrderBlockCandidate,
)
from imie.models import (
    MarketBar,
    OrderBlockFinding,
    StructureResult,
)


@dataclass(frozen=True, slots=True)
class OrderBlockDetector:
    """
    Detects bullish institutional order-block candidates from
    completed market bars and completed structure intelligence.

    Responsibilities:

    - validate detector inputs;
    - search backward for the latest valid bullish candidate;
    - validate candle-displacement requirements;
    - delegate displacement scoring to DisplacementScorer;
    - delegate finding construction to OrderBlockBuilder;
    - enforce the minimum confidence threshold.

    The detector does not:

    - calculate displacement scores internally;
    - calculate finding confidence;
    - resolve structural origin;
    - construct evidence narratives;
    - manage lifecycle state;
    - authorize trades.
    """

    minimum_body_ratio: float = 0.60
    minimum_displacement_multiple: float = 1.50
    minimum_close_location: float = 0.70
    minimum_confidence: float = 60.0
    search_lookback: int = 20

    scorer: DisplacementScorer = field(
        default_factory=DisplacementScorer,
    )

    builder: OrderBlockBuilder = field(
        default_factory=OrderBlockBuilder,
    )

    def __post_init__(self) -> None:
        if not 0.0 <= self.minimum_body_ratio <= 1.0:
            raise ValueError(
                "minimum_body_ratio must be between 0 and 1."
            )

        if self.minimum_displacement_multiple <= 0.0:
            raise ValueError(
                "minimum_displacement_multiple must be positive."
            )

        if not 0.0 <= self.minimum_close_location <= 1.0:
            raise ValueError(
                "minimum_close_location must be between 0 and 1."
            )

        if not 0.0 <= self.minimum_confidence <= 100.0:
            raise ValueError(
                "minimum_confidence must be between 0 and 100."
            )

        if self.search_lookback < 2:
            raise ValueError(
                "search_lookback must be at least 2."
            )

        if not isinstance(
            self.scorer,
            DisplacementScorer,
        ):
            raise TypeError(
                "scorer must be a DisplacementScorer."
            )

        if not isinstance(
            self.builder,
            OrderBlockBuilder,
        ):
            raise TypeError(
                "builder must be an OrderBlockBuilder."
            )

    def detect(
        self,
        bars: tuple[MarketBar, ...],
        structure: StructureResult,
    ) -> tuple[OrderBlockFinding, ...]:
        """
        Detect the latest qualified bullish order block.

        The detector returns at most one finding: the newest valid
        candidate inside the configured search window.
        """
        self._validate_inputs(
            bars=bars,
            structure=structure,
        )

        if len(bars) < 2:
            return ()

        if not self._has_bullish_structure_confirmation(
            structure
        ):
            return ()

        candidate = self._find_latest_bullish_candidate(
            bars=bars,
        )

        if candidate is None:
            return ()

        finding = self.builder.build_bullish(
            candidate=candidate,
            structure=structure,
        )

        if finding.confidence < self.minimum_confidence:
            return ()

        return (finding,)

    @staticmethod
    def _validate_inputs(
        *,
        bars: tuple[MarketBar, ...],
        structure: StructureResult,
    ) -> None:
        if not isinstance(
            bars,
            tuple,
        ):
            raise TypeError(
                "bars must be a tuple of MarketBar objects."
            )

        for bar in bars:
            if not isinstance(
                bar,
                MarketBar,
            ):
                raise TypeError(
                    "bars must contain MarketBar objects."
                )

        if not isinstance(
            structure,
            StructureResult,
        ):
            raise TypeError(
                "structure must be a StructureResult."
            )

    def _find_latest_bullish_candidate(
        self,
        *,
        bars: tuple[MarketBar, ...],
    ) -> OrderBlockCandidate | None:
        """
        Search backward for the newest qualified pairing of:

        - bearish source candle;
        - bullish displacement candle.
        """
        start_index = max(
            0,
            len(bars) - self.search_lookback,
        )

        for displacement_index in range(
            len(bars) - 1,
            start_index,
            -1,
        ):
            source_index = displacement_index - 1

            source = bars[source_index]
            displacement_bar = bars[displacement_index]

            if not self._is_bearish(
                source
            ):
                continue

            if not self._is_bullish(
                displacement_bar
            ):
                continue

            if not self._is_valid_bullish_displacement(
                source=source,
                displacement_bar=displacement_bar,
            ):
                continue

            displacement_score = self.scorer.score(
                source=source,
                displacement=displacement_bar,
            )

            return OrderBlockCandidate(
                source_index=source_index,
                displacement_index=displacement_index,
                source_bar=source,
                displacement_bar=displacement_bar,
                displacement_score=(
                    displacement_score.overall_score
                ),
            )

        return None

    @staticmethod
    def _is_bearish(
        bar: MarketBar,
    ) -> bool:
        return bar.close < bar.open

    @staticmethod
    def _is_bullish(
        bar: MarketBar,
    ) -> bool:
        return bar.close > bar.open

    def _is_valid_bullish_displacement(
        self,
        *,
        source: MarketBar,
        displacement_bar: MarketBar,
    ) -> bool:
        """
        Validate the minimum price-action requirements for
        bullish displacement.

        The final quality score is produced separately by
        DisplacementScorer.
        """
        displacement_range = self._bar_range(
            displacement_bar
        )

        if displacement_range <= 0.0:
            return False

        displacement_body = self._body_size(
            displacement_bar
        )

        source_body = self._body_size(
            source
        )

        if source_body <= 0.0:
            return False

        body_ratio = (
            displacement_body
            / displacement_range
        )

        if (
            body_ratio
            < self.minimum_body_ratio
        ):
            return False

        displacement_multiple = (
            displacement_body
            / source_body
        )

        if (
            displacement_multiple
            < self.minimum_displacement_multiple
        ):
            return False

        close_location = (
            displacement_bar.close
            - displacement_bar.low
        ) / displacement_range

        if (
            close_location
            < self.minimum_close_location
        ):
            return False

        if (
            displacement_bar.close
            <= source.high
        ):
            return False

        return True

    @staticmethod
    def _has_bullish_structure_confirmation(
        structure: StructureResult,
    ) -> bool:
        """
        Accept completed bullish BOS, CHoCH, or MSS.

        StructureResult exposes these confirmations as booleans.
        """
        return (
            structure.bullish_break
            or structure.bullish_choch
            or structure.bullish_mss
        )

    @staticmethod
    def _body_size(
        bar: MarketBar,
    ) -> float:
        return abs(
            bar.close
            - bar.open
        )

    @staticmethod
    def _bar_range(
        bar: MarketBar,
    ) -> float:
        return (
            bar.high
            - bar.low
        )