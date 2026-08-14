from __future__ import annotations

from datetime import datetime
import math

from imie.models import (
    BrokerMarketSessionSnapshot,
    MarketSessionSafetyAssessment,
)


class MarketSessionSafetyEngine:
    """Permit new broker risk only while the broker reports an open session."""

    def assess(
        self,
        snapshot: BrokerMarketSessionSnapshot,
        *,
        checked_at: datetime | None = None,
        maximum_session_age_seconds: float | None = None,
    ) -> MarketSessionSafetyAssessment:
        if not isinstance(snapshot, BrokerMarketSessionSnapshot):
            raise TypeError("snapshot must be a BrokerMarketSessionSnapshot.")
        if (checked_at is None) != (maximum_session_age_seconds is None):
            raise ValueError(
                "checked_at and maximum_session_age_seconds must be "
                "configured together."
            )

        session_age_seconds = None
        session_fresh = True
        if checked_at is not None:
            if not isinstance(checked_at, datetime):
                raise TypeError("checked_at must be a datetime or None.")
            if checked_at.tzinfo is None:
                raise ValueError("checked_at must be timezone-aware.")
            if (
                isinstance(maximum_session_age_seconds, bool)
                or not isinstance(maximum_session_age_seconds, int | float)
            ):
                raise TypeError(
                    "maximum_session_age_seconds must be a number or None."
                )
            maximum_session_age_seconds = float(maximum_session_age_seconds)
            if (
                not math.isfinite(maximum_session_age_seconds)
                or maximum_session_age_seconds <= 0
            ):
                raise ValueError(
                    "maximum_session_age_seconds must be finite and positive."
                )
            session_age_seconds = (
                checked_at - snapshot.observed_at
            ).total_seconds()
            if session_age_seconds < 0:
                raise ValueError(
                    "broker market session cannot be observed in the future."
                )
            session_fresh = (
                session_age_seconds <= maximum_session_age_seconds
            )

        violations = []
        if not session_fresh:
            violations.append(
                "Broker market session is stale: "
                f"{session_age_seconds:.3f}s > "
                f"{maximum_session_age_seconds:.3f}s."
            )
        if not snapshot.is_open:
            violations.append("Broker market session is closed.")
        allowed = snapshot.is_open and session_fresh
        return MarketSessionSafetyAssessment(
            broker=snapshot.broker,
            session_open=snapshot.is_open,
            observed_at=snapshot.observed_at,
            next_open=snapshot.next_open,
            next_close=snapshot.next_close,
            allowed=allowed,
            violations=tuple(violations),
            session_age_seconds=session_age_seconds,
            maximum_session_age_seconds=maximum_session_age_seconds,
            session_fresh=session_fresh,
        )
