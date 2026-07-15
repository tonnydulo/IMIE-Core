from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Mapping, TypeVar

from imie.core.transition import Transition


StateT = TypeVar("StateT")


@dataclass(frozen=True, slots=True)
class StateMachine(Generic[StateT]):
    """
    Validates immutable state transitions against a supplied
    transition rule map.

    The StateMachine contains no market-specific or domain-specific
    logic. It only determines whether movement from one state to
    another is allowed.

    Domain engines remain responsible for deciding which transition
    should be attempted.
    """

    rules: Mapping[
        StateT,
        frozenset[StateT],
    ]

    def __post_init__(self) -> None:
        if not self.rules:
            raise ValueError(
                "StateMachine rules cannot be empty."
            )

        for previous, allowed_states in self.rules.items():
            if not isinstance(
                allowed_states,
                frozenset,
            ):
                raise TypeError(
                    "StateMachine rule values must be frozensets."
                )

            if not allowed_states:
                raise ValueError(
                    "Each StateMachine state must allow at least "
                    "one transition."
                )

            if previous not in self.rules:
                raise ValueError(
                    "Every previous state must exist in the rule map."
                )

            for current in allowed_states:
                if current not in self.rules:
                    raise ValueError(
                        "Every allowed destination state must exist "
                        "in the rule map."
                    )

    def can_transition(
        self,
        previous: StateT,
        current: StateT,
    ) -> bool:
        """
        Return True when the proposed transition is legal.

        Unknown states are treated as invalid rather than raising
        an exception from this query method.
        """
        allowed_states = self.rules.get(previous)

        if allowed_states is None:
            return False

        return current in allowed_states

    def validate_transition(
        self,
        previous: StateT,
        current: StateT,
    ) -> None:
        """
        Validate a proposed state transition.

        Raises:
            ValueError:
                If either state is unknown or the transition is not
                permitted by the configured rules.
        """
        if previous not in self.rules:
            raise ValueError(
                f"Unknown previous state: {previous!r}."
            )

        if current not in self.rules:
            raise ValueError(
                f"Unknown current state: {current!r}."
            )

        if not self.can_transition(
            previous,
            current,
        ):
            raise ValueError(
                "Illegal state transition from "
                f"{previous!r} to {current!r}."
            )

    def apply(
        self,
        transition: Transition[StateT],
    ) -> Transition[StateT]:
        """
        Validate and return an immutable Transition.

        Returning the same transition object preserves immutability
        and allows domain engines to compose validated transitions
        without introducing hidden state or mutation.
        """
        if not isinstance(
            transition,
            Transition,
        ):
            raise TypeError(
                "StateMachine apply requires a Transition."
            )

        self.validate_transition(
            transition.previous,
            transition.current,
        )

        return transition