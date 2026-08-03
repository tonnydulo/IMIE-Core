from __future__ import annotations

from dataclasses import dataclass

from imie.analysts.base import Analyst
from imie.models import (
    AnalystResult,
    LiquidityAnalysis,
    LiquidityImportance,
    LiquidityPool,
    LiquidityPoolState,
    LiquidityPoolStateType,
    LiquidityResult,
    LiquiditySide,
    SweepResult,
)


@dataclass(frozen=True, slots=True)
class LiquidityAnalyst(Analyst):
    """
    Produces an institutional interpretation of the current
    liquidity landscape.

    The LiquidityAnalyst consumes completed engine outputs.
    It performs no market detection itself.

    The analyst supports two public outputs:

    - analyze() returns the domain-specific LiquidityAnalysis.
    - analyze_result() wraps that analysis in the standard
      AnalystResult envelope used by IMIE-Core orchestration.
    """

    def analyze(
        self,
        liquidity: LiquidityResult,
        states: tuple[LiquidityPoolState, ...],
        sweeps: tuple[SweepResult, ...],
    ) -> LiquidityAnalysis:
        self._validate_inputs(
            liquidity=liquidity,
            states=states,
            sweeps=sweeps,
        )

        active_states = tuple(
            state
            for state in states
            if state.state is LiquidityPoolStateType.ACTIVE
        )

        nearest_buy = self._nearest_pool(
            states=active_states,
            side=LiquiditySide.BUY_SIDE,
        )

        nearest_sell = self._nearest_pool(
            states=active_states,
            side=LiquiditySide.SELL_SIDE,
        )

        strongest = self._strongest_pool(
            states=active_states,
        )

        swept_count = sum(
            1
            for state in states
            if state.state is LiquidityPoolStateType.SWEPT
        )

        consumed_count = sum(
            1
            for state in states
            if state.state is LiquidityPoolStateType.CONSUMED
        )

        confidence = self._calculate_confidence(
            active_states=active_states,
            strongest=strongest,
        )

        opinion = self._build_opinion(
            buy_pool=nearest_buy,
            sell_pool=nearest_sell,
        )

        evidence = self._build_evidence(
            active_states=active_states,
            sweeps=sweeps,
        )

        warnings = self._build_warnings(
            active_states=active_states,
        )

        return LiquidityAnalysis(
            institutional_bias=liquidity.institutional_bias,
            nearest_active_buy_pool=nearest_buy,
            nearest_active_sell_pool=nearest_sell,
            strongest_pool=strongest,
            active_pool_count=len(active_states),
            swept_pool_count=swept_count,
            consumed_pool_count=consumed_count,
            confidence=confidence,
            opinion=opinion,
            evidence=evidence,
            warnings=warnings,
        )

    def analyze_result(
        self,
        liquidity: LiquidityResult,
        states: tuple[LiquidityPoolState, ...],
        sweeps: tuple[SweepResult, ...],
    ) -> AnalystResult:
        """
        Return liquidity intelligence through IMIE-Core's
        standard AnalystResult envelope.

        The complete LiquidityAnalysis remains available in
        the payload for domain-specific consumers.
        """
        analysis = self.analyze(
            liquidity=liquidity,
            states=states,
            sweeps=sweeps,
        )

        return AnalystResult(
            analyst=self.__class__.__name__,
            opinion=analysis.opinion,
            confidence=analysis.confidence,
            evidence=analysis.evidence,
            warnings=analysis.warnings,
            payload=analysis,
        )

    @staticmethod
    def _validate_inputs(
        *,
        liquidity: LiquidityResult,
        states: tuple[LiquidityPoolState, ...],
        sweeps: tuple[SweepResult, ...],
    ) -> None:
        if not isinstance(
            liquidity,
            LiquidityResult,
        ):
            raise TypeError(
                "liquidity must be a LiquidityResult."
            )

        for state in states:
            if not isinstance(
                state,
                LiquidityPoolState,
            ):
                raise TypeError(
                    "states must contain "
                    "LiquidityPoolState objects."
                )

        for sweep in sweeps:
            if not isinstance(
                sweep,
                SweepResult,
            ):
                raise TypeError(
                    "sweeps must contain SweepResult objects."
                )

    @staticmethod
    def _nearest_pool(
        *,
        states: tuple[LiquidityPoolState, ...],
        side: LiquiditySide,
    ) -> LiquidityPool | None:
        pools = tuple(
            state.pool
            for state in states
            if state.pool.side is side
        )

        if not pools:
            return None

        if side is LiquiditySide.BUY_SIDE:
            return min(
                pools,
                key=lambda pool: pool.price,
            )

        return max(
            pools,
            key=lambda pool: pool.price,
        )

    @staticmethod
    def _strongest_pool(
        *,
        states: tuple[LiquidityPoolState, ...],
    ) -> LiquidityPool | None:
        if not states:
            return None

        return max(
            (
                state.pool
                for state in states
            ),
            key=lambda pool: (
                pool.confidence,
                pool.strength,
            ),
        )

    @staticmethod
    def _calculate_confidence(
        *,
        active_states: tuple[
            LiquidityPoolState,
            ...
        ],
        strongest: LiquidityPool | None,
    ) -> float:
        if not active_states:
            return 0.0

        if strongest is None:
            return 60.0

        if (
            strongest.importance
            is LiquidityImportance.MAJOR
        ):
            return 90.0

        if len(active_states) >= 2:
            return 80.0

        return 60.0

    @staticmethod
    def _build_opinion(
        *,
        buy_pool: LiquidityPool | None,
        sell_pool: LiquidityPool | None,
    ) -> str:
        if (
            buy_pool is not None
            and sell_pool is None
        ):
            return (
                "Institutional buy-side liquidity "
                "remains active."
            )

        if (
            sell_pool is not None
            and buy_pool is None
        ):
            return (
                "Institutional sell-side liquidity "
                "remains active."
            )

        if (
            buy_pool is not None
            and sell_pool is not None
        ):
            return (
                "Institutional liquidity remains balanced."
            )

        return (
            "No actionable institutional liquidity "
            "currently exists."
        )

    @staticmethod
    def _build_evidence(
        *,
        active_states: tuple[
            LiquidityPoolState,
            ...
        ],
        sweeps: tuple[SweepResult, ...],
    ) -> tuple[str, ...]:
        evidence: list[str] = []

        if active_states:
            evidence.append(
                f"{len(active_states)} active liquidity "
                f"pool{'' if len(active_states) == 1 else 's'} "
                "identified."
            )

        confirmed_sweeps = sum(
            1
            for sweep in sweeps
            if sweep.swept
        )

        if confirmed_sweeps:
            evidence.append(
                f"{confirmed_sweeps} confirmed liquidity "
                f"sweep{'' if confirmed_sweeps == 1 else 's'}."
            )

        if not evidence:
            evidence.append(
                "No active institutional liquidity."
            )

        return tuple(evidence)

    @staticmethod
    def _build_warnings(
        *,
        active_states: tuple[
            LiquidityPoolState,
            ...
        ],
    ) -> tuple[str, ...]:
        if active_states:
            return ()

        return (
            "No active liquidity pools available.",
        )