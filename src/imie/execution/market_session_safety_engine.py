from __future__ import annotations

from imie.models import (
    BrokerMarketSessionSnapshot,
    MarketSessionSafetyAssessment,
)


class MarketSessionSafetyEngine:
    """Permit new broker risk only while the broker reports an open session."""

    def assess(
        self,
        snapshot: BrokerMarketSessionSnapshot,
    ) -> MarketSessionSafetyAssessment:
        if not isinstance(snapshot, BrokerMarketSessionSnapshot):
            raise TypeError("snapshot must be a BrokerMarketSessionSnapshot.")
        violations = () if snapshot.is_open else (
            "Broker market session is closed.",
        )
        return MarketSessionSafetyAssessment(
            broker=snapshot.broker,
            session_open=snapshot.is_open,
            observed_at=snapshot.observed_at,
            next_open=snapshot.next_open,
            next_close=snapshot.next_close,
            allowed=snapshot.is_open,
            violations=violations,
        )
