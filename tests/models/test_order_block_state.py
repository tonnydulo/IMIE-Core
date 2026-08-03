from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from imie.models import (
    OrderBlockFinding,
    OrderBlockOrigin,
    OrderBlockSide,
    OrderBlockLifecycleState,
    OrderBlockStateType,
)


def make_finding() -> OrderBlockFinding:
    return OrderBlockFinding(
        upper=550.00,
        lower=549.50,
        side=OrderBlockSide.BULLISH,
        origin=OrderBlockOrigin.BOS,
        source_bar_index=10,
        displacement=0.50,
        strength=88.0,
        confidence=92.0,
        reason=(
            "A bearish source candle preceded qualified "
            "bullish displacement."
        ),
        evidence=(
            "Bullish displacement confirmed.",
            "Bullish structural break confirmed.",
        ),
        detector="OrderBlockBuilder",
    )


def make_state(
    *,
    state: OrderBlockStateType = OrderBlockStateType.NEW,
    created_bar: int = 10,
    last_touch_bar: int | None = None,
    touch_count: int = 0,
    mitigation_count: int = 0,
    active: bool = True,
) -> OrderBlockLifecycleState:
    return OrderBlockLifecycleState(
        finding=make_finding(),
        state=state,
        created_bar=created_bar,
        last_touch_bar=last_touch_bar,
        touch_count=touch_count,
        mitigation_count=mitigation_count,
        active=active,
    )


def test_order_block_state_fields() -> None:
    state = make_state()

    assert isinstance(
        state.finding,
        OrderBlockFinding,
    )
    assert state.state is OrderBlockStateType.NEW
    assert state.created_bar == 10
    assert state.last_touch_bar is None
    assert state.touch_count == 0
    assert state.mitigation_count == 0
    assert state.active is True


def test_finding_is_retained() -> None:
    finding = make_finding()

    state = OrderBlockLifecycleState(
        finding=finding,
        state=OrderBlockStateType.NEW,
        created_bar=10,
        last_touch_bar=None,
        touch_count=0,
        mitigation_count=0,
        active=True,
    )

    assert state.finding is finding


@pytest.mark.parametrize(
    (
        "state_type",
        "touch_count",
        "mitigation_count",
        "last_touch_bar",
        "active",
    ),
    [
        (
            OrderBlockStateType.NEW,
            0,
            0,
            None,
            True,
        ),
        (
            OrderBlockStateType.ACTIVE,
            0,
            0,
            None,
            True,
        ),
        (
            OrderBlockStateType.TESTED,
            1,
            0,
            12,
            True,
        ),
        (
            OrderBlockStateType.MITIGATED,
            2,
            1,
            15,
            True,
        ),
        (
            OrderBlockStateType.INVALIDATED,
            0,
            0,
            None,
            False,
        ),
    ],
)
def test_stores_each_lifecycle_state(
    state_type: OrderBlockStateType,
    touch_count: int,
    mitigation_count: int,
    last_touch_bar: int | None,
    active: bool,
) -> None:
    state = make_state(
        state=state_type,
        touch_count=touch_count,
        mitigation_count=mitigation_count,
        last_touch_bar=last_touch_bar,
        active=active,
    )

    assert state.state is state_type


def test_touch_count_is_stored() -> None:
    state = make_state(
        state=OrderBlockStateType.TESTED,
        last_touch_bar=15,
        touch_count=2,
    )

    assert state.touch_count == 2
    assert state.last_touch_bar == 15


def test_mitigation_count_is_stored() -> None:
    state = make_state(
        state=OrderBlockStateType.MITIGATED,
        last_touch_bar=18,
        touch_count=3,
        mitigation_count=1,
    )

    assert state.mitigation_count == 1


def test_active_flag_is_stored() -> None:
    state = make_state(
        state=OrderBlockStateType.INVALIDATED,
        active=False,
    )

    assert state.active is False


def test_order_block_state_is_frozen() -> None:
    state = make_state()

    with pytest.raises(FrozenInstanceError):
        state.touch_count = 1  # type: ignore[misc]


def test_rejects_invalid_finding_type() -> None:
    with pytest.raises(
        TypeError,
        match="finding must be an OrderBlockFinding",
    ):
        OrderBlockLifecycleState(
            finding=None,  # type: ignore[arg-type]
            state=OrderBlockStateType.NEW,
            created_bar=10,
            last_touch_bar=None,
            touch_count=0,
            mitigation_count=0,
            active=True,
        )


def test_rejects_invalid_state_type() -> None:
    with pytest.raises(
        TypeError,
        match="state must be an OrderBlockStateType",
    ):
        OrderBlockLifecycleState(
            finding=make_finding(),
            state="NEW",  # type: ignore[arg-type]
            created_bar=10,
            last_touch_bar=None,
            touch_count=0,
            mitigation_count=0,
            active=True,
        )


def test_rejects_negative_created_bar() -> None:
    with pytest.raises(
        ValueError,
        match="created_bar cannot be negative",
    ):
        make_state(
            created_bar=-1,
        )


def test_rejects_negative_last_touch_bar() -> None:
    with pytest.raises(
        ValueError,
        match="last_touch_bar cannot be negative",
    ):
        make_state(
            last_touch_bar=-1,
        )


def test_rejects_last_touch_before_creation() -> None:
    with pytest.raises(
        ValueError,
        match="last_touch_bar cannot be earlier than created_bar",
    ):
        make_state(
            created_bar=10,
            last_touch_bar=9,
        )


def test_rejects_negative_touch_count() -> None:
    with pytest.raises(
        ValueError,
        match="touch_count cannot be negative",
    ):
        make_state(
            touch_count=-1,
        )


def test_rejects_negative_mitigation_count() -> None:
    with pytest.raises(
        ValueError,
        match="mitigation_count cannot be negative",
    ):
        make_state(
            mitigation_count=-1,
        )


def test_rejects_mitigation_count_above_touch_count() -> None:
    with pytest.raises(
        ValueError,
        match="mitigation_count cannot exceed touch_count",
    ):
        make_state(
            touch_count=1,
            mitigation_count=2,
        )


def test_rejects_touch_count_without_last_touch_bar() -> None:
    with pytest.raises(
        ValueError,
        match="touch_count requires last_touch_bar",
    ):
        make_state(
            touch_count=1,
            last_touch_bar=None,
        )


def test_rejects_last_touch_bar_without_touch_count() -> None:
    with pytest.raises(
        ValueError,
        match="last_touch_bar requires a positive touch_count",
    ):
        make_state(
            touch_count=0,
            last_touch_bar=12,
        )


def test_new_state_requires_zero_touches() -> None:
    with pytest.raises(
        ValueError,
        match="NEW state cannot have touches",
    ):
        make_state(
            state=OrderBlockStateType.NEW,
            last_touch_bar=12,
            touch_count=1,
        )


def test_tested_state_requires_touch() -> None:
    with pytest.raises(
        ValueError,
        match="TESTED state requires at least one touch",
    ):
        make_state(
            state=OrderBlockStateType.TESTED,
            touch_count=0,
            last_touch_bar=None,
        )


def test_mitigated_state_requires_mitigation() -> None:
    with pytest.raises(
        ValueError,
        match="MITIGATED state requires at least one mitigation",
    ):
        make_state(
            state=OrderBlockStateType.MITIGATED,
            last_touch_bar=15,
            touch_count=1,
            mitigation_count=0,
        )


def test_invalidated_state_requires_inactive_flag() -> None:
    with pytest.raises(
        ValueError,
        match="INVALIDATED state must be inactive",
    ):
        make_state(
            state=OrderBlockStateType.INVALIDATED,
            active=True,
        )


def test_non_invalidated_state_requires_active_flag() -> None:
    with pytest.raises(
        ValueError,
        match="Non-invalidated state must remain active",
    ):
        make_state(
            state=OrderBlockStateType.ACTIVE,
            active=False,
        )


def test_new_state_is_active() -> None:
    state = make_state(
        state=OrderBlockStateType.NEW,
        active=True,
    )

    assert state.is_new is True
    assert state.is_active is True


def test_active_state_helper() -> None:
    state = make_state(
        state=OrderBlockStateType.ACTIVE,
        active=True,
    )

    assert state.is_active_state is True
    assert state.is_active is True


def test_tested_state_helper() -> None:
    state = make_state(
        state=OrderBlockStateType.TESTED,
        last_touch_bar=15,
        touch_count=1,
        active=True,
    )

    assert state.is_tested is True


def test_mitigated_state_helper() -> None:
    state = make_state(
        state=OrderBlockStateType.MITIGATED,
        last_touch_bar=15,
        touch_count=1,
        mitigation_count=1,
        active=True,
    )

    assert state.is_mitigated is True


def test_invalidated_state_helper() -> None:
    state = make_state(
        state=OrderBlockStateType.INVALIDATED,
        active=False,
    )

    assert state.is_invalidated is True
    assert state.is_active is False