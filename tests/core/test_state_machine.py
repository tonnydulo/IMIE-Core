from enum import Enum

import pytest

from imie.core import StateMachine, Transition


class ExampleState(str, Enum):
    ACTIVE = "ACTIVE"
    SWEPT = "SWEPT"
    RETIRED = "RETIRED"


def make_rules() -> dict[
    ExampleState,
    frozenset[ExampleState],
]:
    return {
        ExampleState.ACTIVE: frozenset(
            {
                ExampleState.ACTIVE,
                ExampleState.SWEPT,
            }
        ),
        ExampleState.SWEPT: frozenset(
            {
                ExampleState.SWEPT,
                ExampleState.RETIRED,
            }
        ),
        ExampleState.RETIRED: frozenset(
            {
                ExampleState.RETIRED,
            }
        ),
    }


def make_machine() -> StateMachine[ExampleState]:
    return StateMachine(
        rules=make_rules(),
    )


def test_can_transition_returns_true_for_legal_transition() -> None:
    machine = make_machine()

    assert machine.can_transition(
        ExampleState.ACTIVE,
        ExampleState.SWEPT,
    ) is True


def test_can_transition_returns_true_for_self_transition() -> None:
    machine = make_machine()

    assert machine.can_transition(
        ExampleState.ACTIVE,
        ExampleState.ACTIVE,
    ) is True


def test_can_transition_returns_false_for_illegal_transition() -> None:
    machine = make_machine()

    assert machine.can_transition(
        ExampleState.RETIRED,
        ExampleState.ACTIVE,
    ) is False


def test_validate_transition_accepts_legal_transition() -> None:
    machine = make_machine()

    machine.validate_transition(
        ExampleState.SWEPT,
        ExampleState.RETIRED,
    )


def test_validate_transition_rejects_illegal_transition() -> None:
    machine = make_machine()

    with pytest.raises(
        ValueError,
        match="Illegal state transition",
    ):
        machine.validate_transition(
            ExampleState.ACTIVE,
            ExampleState.RETIRED,
        )


def test_apply_returns_same_transition() -> None:
    machine = make_machine()

    transition = Transition(
        previous=ExampleState.ACTIVE,
        current=ExampleState.SWEPT,
        reason="Liquidity was swept.",
        evidence=("Sweep confirmed.",),
        warnings=(),
    )

    result = machine.apply(transition)

    assert result is transition


def test_apply_rejects_illegal_transition() -> None:
    machine = make_machine()

    transition = Transition(
        previous=ExampleState.RETIRED,
        current=ExampleState.ACTIVE,
        reason="Invalid reactivation.",
        evidence=("Attempted invalid transition.",),
        warnings=(),
    )

    with pytest.raises(
        ValueError,
        match="Illegal state transition",
    ):
        machine.apply(transition)


def test_apply_rejects_non_transition() -> None:
    machine = make_machine()

    with pytest.raises(
        TypeError,
        match="requires a Transition",
    ):
        machine.apply(
            "not-a-transition",  # type: ignore[arg-type]
        )


def test_rejects_empty_rules() -> None:
    with pytest.raises(
        ValueError,
        match="rules cannot be empty",
    ):
        StateMachine[
            ExampleState
        ](
            rules={},
        )


def test_rejects_non_frozenset_rule_values() -> None:
    with pytest.raises(
        TypeError,
        match="rule values must be frozensets",
    ):
        StateMachine(
            rules={
                ExampleState.ACTIVE: {
                    ExampleState.ACTIVE,
                },
            }  # type: ignore[arg-type]
        )


def test_rejects_empty_allowed_state_set() -> None:
    with pytest.raises(
        ValueError,
        match="must allow at least one transition",
    ):
        StateMachine(
            rules={
                ExampleState.ACTIVE: frozenset(),
            }
        )


def test_rejects_destination_missing_from_rule_map() -> None:
    with pytest.raises(
        ValueError,
        match="destination state must exist",
    ):
        StateMachine(
            rules={
                ExampleState.ACTIVE: frozenset(
                    {
                        ExampleState.SWEPT,
                    }
                ),
            }
        )


def test_unknown_previous_state_returns_false() -> None:
    machine = make_machine()

    assert machine.can_transition(
        "UNKNOWN",  # type: ignore[arg-type]
        ExampleState.ACTIVE,
    ) is False


def test_validate_rejects_unknown_previous_state() -> None:
    machine = make_machine()

    with pytest.raises(
        ValueError,
        match="Unknown previous state",
    ):
        machine.validate_transition(
            "UNKNOWN",  # type: ignore[arg-type]
            ExampleState.ACTIVE,
        )


def test_validate_rejects_unknown_current_state() -> None:
    machine = make_machine()

    with pytest.raises(
        ValueError,
        match="Unknown current state",
    ):
        machine.validate_transition(
            ExampleState.ACTIVE,
            "UNKNOWN",  # type: ignore[arg-type]
        )