from __future__ import annotations

from dataclasses import dataclass

from imie.models.order_block_finding import (
    OrderBlockFinding,
)
from imie.models.order_block_state_type import (
    OrderBlockStateType,
)


@dataclass(frozen=True, slots=True)
class OrderBlockLifecycleState:
    """
    Immutable lifecycle snapshot for an institutional
    order-block finding.

    Every lifecycle transition produces a new snapshot.
    The underlying OrderBlockFinding remains unchanged.
    """

    finding: OrderBlockFinding
    state: OrderBlockStateType

    created_bar: int
    last_touch_bar: int | None

    touch_count: int
    mitigation_count: int

    active: bool

    def __post_init__(self) -> None:
        if not isinstance(
            self.finding,
            OrderBlockFinding,
        ):
            raise TypeError(
                "finding must be an OrderBlockFinding."
            )

        if not isinstance(
            self.state,
            OrderBlockStateType,
        ):
            raise TypeError(
                "state must be an OrderBlockStateType."
            )

        if self.created_bar < 0:
            raise ValueError(
                "created_bar cannot be negative."
            )

        if (
            self.last_touch_bar is not None
            and self.last_touch_bar < 0
        ):
            raise ValueError(
                "last_touch_bar cannot be negative."
            )

        if (
            self.last_touch_bar is not None
            and self.last_touch_bar < self.created_bar
        ):
            raise ValueError(
                "last_touch_bar cannot be earlier than created_bar."
            )

        if self.touch_count < 0:
            raise ValueError(
                "touch_count cannot be negative."
            )

        if self.mitigation_count < 0:
            raise ValueError(
                "mitigation_count cannot be negative."
            )

        if self.mitigation_count > self.touch_count:
            raise ValueError(
                "mitigation_count cannot exceed touch_count."
            )

        if (
            self.touch_count > 0
            and self.last_touch_bar is None
        ):
            raise ValueError(
                "touch_count requires last_touch_bar."
            )

        if (
            self.last_touch_bar is not None
            and self.touch_count <= 0
        ):
            raise ValueError(
                "last_touch_bar requires a positive touch_count."
            )

        if (
            self.state is OrderBlockStateType.NEW
            and self.touch_count > 0
        ):
            raise ValueError(
                "NEW state cannot have touches."
            )

        if (
            self.state is OrderBlockStateType.TESTED
            and self.touch_count < 1
        ):
            raise ValueError(
                "TESTED state requires at least one touch."
            )

        if (
            self.state is OrderBlockStateType.MITIGATED
            and self.mitigation_count < 1
        ):
            raise ValueError(
                "MITIGATED state requires at least one mitigation."
            )

        if (
            self.state is OrderBlockStateType.INVALIDATED
            and self.active
        ):
            raise ValueError(
                "INVALIDATED state must be inactive."
            )

        if (
            self.state is not OrderBlockStateType.INVALIDATED
            and not self.active
        ):
            raise ValueError(
                "Non-invalidated state must remain active."
            )

    @property
    def is_new(self) -> bool:
        return self.state is OrderBlockStateType.NEW

    @property
    def is_active_state(self) -> bool:
        return self.state is OrderBlockStateType.ACTIVE

    @property
    def is_tested(self) -> bool:
        return self.state is OrderBlockStateType.TESTED

    @property
    def is_mitigated(self) -> bool:
        return self.state is OrderBlockStateType.MITIGATED

    @property
    def is_invalidated(self) -> bool:
        return self.state is OrderBlockStateType.INVALIDATED

    @property
    def is_active(self) -> bool:
        return self.active