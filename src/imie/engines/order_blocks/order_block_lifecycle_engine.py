from __future__ import annotations

from dataclasses import dataclass

from imie.models import (
    MarketBar,
    OrderBlockLifecycleState,
    OrderBlockSide,
    OrderBlockStateType,
)


@dataclass(frozen=True, slots=True)
class OrderBlockLifecycleEngine:
    """
    Advances an institutional order block through its lifecycle
    using the latest completed market bar.

    First-pass support is focused on bullish order blocks.

    Bullish lifecycle rules:

    - NEW becomes ACTIVE when no interaction occurs.
    - Price entering the block marks it TESTED.
    - Price reaching the block midpoint marks it MITIGATED.
    - A completed close below the lower boundary invalidates it.
    - INVALIDATED is terminal.

    Every transition returns a new immutable lifecycle snapshot,
    except terminal INVALIDATED states, which are returned unchanged.
    """

    mitigation_depth: float = 0.50

    def __post_init__(self) -> None:
        if not 0.0 <= self.mitigation_depth <= 1.0:
            raise ValueError(
                "mitigation_depth must be between 0 and 1."
            )

    def transition(
        self,
        *,
        state: OrderBlockLifecycleState,
        latest_bar: MarketBar,
    ) -> OrderBlockLifecycleState:
        """
        Evaluate one completed bar and return the next lifecycle
        snapshot.
        """
        self._validate_inputs(
            state=state,
            latest_bar=latest_bar,
        )

        if state.is_invalidated:
            return state

        if (
            state.finding.side
            is OrderBlockSide.BULLISH
        ):
            return self._transition_bullish(
                state=state,
                latest_bar=latest_bar,
            )

        return self._copy_state(
            state=state,
            next_state=(
                OrderBlockStateType.ACTIVE
                if state.is_new
                else state.state
            ),
        )

    def _transition_bullish(
        self,
        *,
        state: OrderBlockLifecycleState,
        latest_bar: MarketBar,
    ) -> OrderBlockLifecycleState:
        finding = state.finding

        if latest_bar.close < finding.lower:
            return OrderBlockLifecycleState(
                finding=finding,
                state=OrderBlockStateType.INVALIDATED,
                created_bar=state.created_bar,
                last_touch_bar=state.last_touch_bar,
                touch_count=state.touch_count,
                mitigation_count=state.mitigation_count,
                active=False,
            )

        touched = self._bar_touches_block(
            latest_bar=latest_bar,
            lower=finding.lower,
            upper=finding.upper,
        )

        if not touched:
            next_state = (
                OrderBlockStateType.ACTIVE
                if state.is_new
                else state.state
            )

            return self._copy_state(
                state=state,
                next_state=next_state,
            )

        touch_bar = self._bar_index(
            latest_bar
        )

        touch_count = state.touch_count + 1

        mitigated = (
            latest_bar.low
            <= self._bullish_mitigation_price(
                lower=finding.lower,
                upper=finding.upper,
            )
        )

        if mitigated:
            return OrderBlockLifecycleState(
                finding=finding,
                state=OrderBlockStateType.MITIGATED,
                created_bar=state.created_bar,
                last_touch_bar=touch_bar,
                touch_count=touch_count,
                mitigation_count=(
                    state.mitigation_count + 1
                ),
                active=True,
            )

        return OrderBlockLifecycleState(
            finding=finding,
            state=OrderBlockStateType.TESTED,
            created_bar=state.created_bar,
            last_touch_bar=touch_bar,
            touch_count=touch_count,
            mitigation_count=state.mitigation_count,
            active=True,
        )

    @staticmethod
    def _validate_inputs(
        *,
        state: OrderBlockLifecycleState,
        latest_bar: MarketBar,
    ) -> None:
        if not isinstance(
            state,
            OrderBlockLifecycleState,
        ):
            raise TypeError(
                "state must be an "
                "OrderBlockLifecycleState."
            )

        if not isinstance(
            latest_bar,
            MarketBar,
        ):
            raise TypeError(
                "latest_bar must be a MarketBar."
            )

    @staticmethod
    def _bar_touches_block(
        *,
        latest_bar: MarketBar,
        lower: float,
        upper: float,
    ) -> bool:
        return (
            latest_bar.low <= upper
            and latest_bar.high >= lower
        )

    def _bullish_mitigation_price(
        self,
        *,
        lower: float,
        upper: float,
    ) -> float:
        """
        Return the required penetration price for a bullish block.

        At the default depth of 0.50, mitigation occurs when price
        reaches the midpoint of the block.
        """
        height = upper - lower

        return (
            upper
            - height * self.mitigation_depth
        )

    @staticmethod
    def _bar_index(
        latest_bar: MarketBar,
    ) -> int:
        """
        Use the test/runtime bar timestamp as the lifecycle index.

        Current IMIE MarketBar fixtures use integer timestamps.
        """
        timestamp = latest_bar.timestamp

        if not isinstance(
            timestamp,
            int,
        ):
            raise TypeError(
                "latest_bar timestamp must be an integer "
                "for lifecycle tracking."
            )

        return timestamp

    @staticmethod
    def _copy_state(
        *,
        state: OrderBlockLifecycleState,
        next_state: OrderBlockStateType,
    ) -> OrderBlockLifecycleState:
        return OrderBlockLifecycleState(
            finding=state.finding,
            state=next_state,
            created_bar=state.created_bar,
            last_touch_bar=state.last_touch_bar,
            touch_count=state.touch_count,
            mitigation_count=state.mitigation_count,
            active=True,
        )