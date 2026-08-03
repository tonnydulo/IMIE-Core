from __future__ import annotations

from dataclasses import dataclass

from imie.core import StateMachine, Transition
from imie.models import (
    LiquidityPoolState,
    LiquidityPoolStateType,
    SweepResult,
)


_LIQUIDITY_LIFECYCLE_RULES: dict[
    LiquidityPoolStateType,
    frozenset[LiquidityPoolStateType],
] = {
    LiquidityPoolStateType.ACTIVE: frozenset(
        {
            LiquidityPoolStateType.ACTIVE,
            LiquidityPoolStateType.SWEPT,
        }
    ),
    LiquidityPoolStateType.SWEPT: frozenset(
        {
            LiquidityPoolStateType.SWEPT,
            LiquidityPoolStateType.RETESTED,
        }
    ),
    LiquidityPoolStateType.RETESTED: frozenset(
        {
            LiquidityPoolStateType.RETESTED,
            LiquidityPoolStateType.CONSUMED,
        }
    ),
    LiquidityPoolStateType.CONSUMED: frozenset(
        {
            LiquidityPoolStateType.CONSUMED,
            LiquidityPoolStateType.RETIRED,
        }
    ),
    LiquidityPoolStateType.RETIRED: frozenset(
        {
            LiquidityPoolStateType.RETIRED,
        }
    ),
}


@dataclass(frozen=True, slots=True)
class LiquidityLifecycleEngine:
    """
    Applies liquidity-pool lifecycle transitions.

    The engine decides which state should follow from a liquidity
    event. The generic StateMachine validates whether that proposed
    transition is legal.

    Version 1 supports:
    - ACTIVE -> SWEPT after a confirmed sweep;
    - self-transitions for all other conditions.

    Retest, consumption, and retirement transitions will be added
    in later modules.
    """

    def transition(
        self,
        previous: LiquidityPoolState,
        sweep: SweepResult,
        current_bar: int,
    ) -> LiquidityPoolState:
        """
        Apply one lifecycle evaluation.

        A new immutable LiquidityPoolState is always returned.
        """
        self._validate_inputs(
            previous=previous,
            sweep=sweep,
            current_bar=current_bar,
        )

        next_state = self._resolve_next_state(
            previous=previous,
            sweep=sweep,
        )

        transition = Transition(
            previous=previous.state,
            current=next_state,
            reason=self._build_transition_reason(
                previous=previous,
                sweep=sweep,
                next_state=next_state,
            ),
            evidence=self._build_transition_evidence(
                previous=previous,
                sweep=sweep,
                next_state=next_state,
            ),
            warnings=(),
        )

        state_machine = StateMachine(
            rules=_LIQUIDITY_LIFECYCLE_RULES,
        )

        state_machine.apply(transition)

        sweep_increment = (
            1
            if (
                previous.state
                is LiquidityPoolStateType.ACTIVE
                and next_state
                is LiquidityPoolStateType.SWEPT
            )
            else 0
        )

        return LiquidityPoolState(
            pool=previous.pool,
            state=next_state,
            created_bar=previous.created_bar,
            updated_bar=current_bar,
            sweep_count=(
                previous.sweep_count
                + sweep_increment
            ),
            retest_count=previous.retest_count,
            evidence=(
                previous.evidence
                + transition.evidence
            ),
            warnings=(
                previous.warnings
                + transition.warnings
            ),
        )

    @staticmethod
    def _validate_inputs(
        *,
        previous: LiquidityPoolState,
        sweep: SweepResult,
        current_bar: int,
    ) -> None:
        if not isinstance(
            previous,
            LiquidityPoolState,
        ):
            raise TypeError(
                "previous must be a LiquidityPoolState."
            )

        if not isinstance(
            sweep,
            SweepResult,
        ):
            raise TypeError(
                "sweep must be a SweepResult."
            )

        if current_bar < previous.updated_bar:
            raise ValueError(
                "current_bar cannot be earlier than "
                "the previous updated_bar."
            )

        if sweep.pool != previous.pool:
            raise ValueError(
                "SweepResult pool must match the lifecycle pool."
            )

    @staticmethod
    def _resolve_next_state(
        *,
        previous: LiquidityPoolState,
        sweep: SweepResult,
    ) -> LiquidityPoolStateType:
        if (
            previous.state
            is LiquidityPoolStateType.ACTIVE
            and sweep.swept
        ):
            return LiquidityPoolStateType.SWEPT

        return previous.state

    @staticmethod
    def _build_transition_reason(
        *,
        previous: LiquidityPoolState,
        sweep: SweepResult,
        next_state: LiquidityPoolStateType,
    ) -> str:
        if (
            previous.state
            is LiquidityPoolStateType.ACTIVE
            and next_state
            is LiquidityPoolStateType.SWEPT
        ):
            return (
                "A confirmed liquidity sweep moved the pool "
                "from ACTIVE to SWEPT."
            )

        return (
            "No lifecycle-changing event occurred; "
            f"the pool remained {previous.state.value}."
        )

    @staticmethod
    def _build_transition_evidence(
        *,
        previous: LiquidityPoolState,
        sweep: SweepResult,
        next_state: LiquidityPoolStateType,
    ) -> tuple[str, ...]:
        if (
            previous.state
            is LiquidityPoolStateType.ACTIVE
            and next_state
            is LiquidityPoolStateType.SWEPT
        ):
            return (
                sweep.reason,
                (
                    "Liquidity pool state transitioned from "
                    "ACTIVE to SWEPT."
                ),
            )

        return (
            (
                "Liquidity pool remained in state "
                f"{previous.state.value}."
            ),
        )