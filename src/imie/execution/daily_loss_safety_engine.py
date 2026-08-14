from __future__ import annotations

import math

from imie.models import BrokerDailyPnlSnapshot, DailyLossAssessment


class DailyLossSafetyEngine:
    """Block new risk once verified current-day losses reach the limit."""

    def assess(
        self,
        *,
        snapshot: BrokerDailyPnlSnapshot,
        maximum_daily_loss: float,
    ) -> DailyLossAssessment:
        if not isinstance(snapshot, BrokerDailyPnlSnapshot):
            raise TypeError("snapshot must be a BrokerDailyPnlSnapshot.")
        if isinstance(maximum_daily_loss, bool) or not isinstance(
            maximum_daily_loss, int | float
        ):
            raise TypeError("maximum_daily_loss must be a number.")
        maximum_daily_loss = float(maximum_daily_loss)
        if not math.isfinite(maximum_daily_loss) or maximum_daily_loss <= 0:
            raise ValueError("maximum_daily_loss must be finite and positive.")

        within_limit = snapshot.loss_amount < maximum_daily_loss
        violations = () if within_limit else (
            "Maximum daily loss reached: "
            f"{snapshot.loss_amount:.2f} >= {maximum_daily_loss:.2f}.",
        )
        return DailyLossAssessment(
            broker=snapshot.broker,
            realized_pnl=snapshot.realized_pnl,
            unrealized_pnl=snapshot.unrealized_pnl,
            total_pnl=snapshot.total_pnl,
            loss_amount=snapshot.loss_amount,
            maximum_daily_loss=maximum_daily_loss,
            within_limit=within_limit,
            allowed=within_limit,
            violations=violations,
        )
