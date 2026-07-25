from __future__ import annotations

from imie.runtime.market_session_result import (
    MarketSessionResult,
)
from imie.runtime.market_session_state import (
    MarketSessionState,
)
from imie.runtime.session_policy_action import (
    SessionPolicyAction,
)
from imie.runtime.session_policy_config import (
    SessionPolicyConfig,
)
from imie.runtime.session_policy_result import (
    SessionPolicyResult,
)


class SessionPolicy:
    """
    Determines whether runtime analysis may execute for the
    current market session.
    """

    def __init__(
        self,
        config: SessionPolicyConfig | None = None,
    ) -> None:
        self.config = (
            config
            or SessionPolicyConfig()
        )

        if not isinstance(
            self.config,
            SessionPolicyConfig,
        ):
            raise TypeError(
                "config must be a SessionPolicyConfig."
            )

    def evaluate(
        self,
        session: MarketSessionResult,
    ) -> SessionPolicyResult:
        if not isinstance(
            session,
            MarketSessionResult,
        ):
            raise TypeError(
                "session must be a MarketSessionResult."
            )

        allowed = self._is_allowed(
            session.state
        )

        if allowed:
            return SessionPolicyResult(
                action=SessionPolicyAction.ANALYZE,
                session=session,
                reason=(
                    "Runtime analysis is allowed during "
                    f"the {session.state.value} session."
                ),
            )

        return SessionPolicyResult(
            action=SessionPolicyAction.SKIP,
            session=session,
            reason=(
                "Runtime analysis is disabled during "
                f"the {session.state.value} session."
            ),
        )

    def _is_allowed(
        self,
        state: MarketSessionState,
    ) -> bool:
        if state is MarketSessionState.PREMARKET:
            return self.config.allow_premarket

        if (
            state
            is MarketSessionState.REGULAR_SESSION
        ):
            return (
                self.config.allow_regular_session
            )

        if state is MarketSessionState.AFTER_HOURS:
            return self.config.allow_after_hours

        if state is MarketSessionState.CLOSED:
            return self.config.allow_closed

        return False