from __future__ import annotations

from dataclasses import dataclass

from imie.runtime.market_session_result import (
    MarketSessionResult,
)
from imie.runtime.session_policy_action import (
    SessionPolicyAction,
)


@dataclass(frozen=True, slots=True)
class SessionPolicyResult:
    action: SessionPolicyAction
    session: MarketSessionResult
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.action,
            SessionPolicyAction,
        ):
            raise TypeError(
                "action must be a SessionPolicyAction."
            )

        if not isinstance(
            self.session,
            MarketSessionResult,
        ):
            raise TypeError(
                "session must be a MarketSessionResult."
            )

        reason = str(
            self.reason
        ).strip()

        if not reason:
            raise ValueError(
                "reason cannot be empty."
            )

        object.__setattr__(
            self,
            "reason",
            reason,
        )

    @property
    def may_analyze(self) -> bool:
        return (
            self.action
            is SessionPolicyAction.ANALYZE
        )

    @property
    def should_skip(self) -> bool:
        return (
            self.action
            is SessionPolicyAction.SKIP
        )