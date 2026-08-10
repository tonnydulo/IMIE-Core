from __future__ import annotations

from math import floor

from imie.models import PositionSizeResult, TradePlan


class PositionSizingEngine:
    def __init__(
        self,
        default_risk_percent: float = 0.50,
    ) -> None:
        if default_risk_percent <= 0:
            raise ValueError(
                "default_risk_percent must be greater than zero."
            )

        self.default_risk_percent = default_risk_percent

    def calculate(
        self,
        trade_plan: TradePlan,
        *,
        account_equity: float,
        risk_percent: float | None = None,
    ) -> PositionSizeResult:
        effective_risk_percent = (
            self.default_risk_percent
            if risk_percent is None
            else risk_percent
        )

        if account_equity <= 0:
            raise ValueError(
                "account_equity must be greater than zero."
            )

        if effective_risk_percent <= 0:
            raise ValueError(
                "risk_percent must be greater than zero."
            )

        if (
            not trade_plan.valid
            or not trade_plan.actionable
            or trade_plan.entry is None
            or trade_plan.stop is None
            or trade_plan.risk_per_share is None
            or trade_plan.risk_per_share <= 0
        ):
            raise ValueError(
                "TradePlan must be valid and actionable "
                "with entry, stop, and positive risk_per_share."
            )

        risk_budget = (
            account_equity
            * effective_risk_percent
            / 100.0
        )

        quantity = floor(
            risk_budget
            / trade_plan.risk_per_share
        )

        position_notional = (
            quantity
            * trade_plan.entry
        )

        actual_risk = (
            quantity
            * trade_plan.risk_per_share
        )

        actual_risk_percent = (
            actual_risk
            / account_equity
            * 100.0
        )

        actionable = quantity >= 1

        warnings: tuple[str, ...] = ()

        if not actionable:
            warnings = (
                "Risk budget is insufficient for one share.",
            )

        return PositionSizeResult(
            symbol=trade_plan.symbol,
            direction=trade_plan.direction,
            account_equity=account_equity,
            risk_percent=effective_risk_percent,
            risk_budget=risk_budget,
            entry=trade_plan.entry,
            stop=trade_plan.stop,
            risk_per_share=trade_plan.risk_per_share,
            quantity=quantity,
            position_notional=position_notional,
            actual_risk=actual_risk,
            actual_risk_percent=actual_risk_percent,
            valid=True,
            actionable=actionable,
            reasons=(
                "Position size calculated from account risk budget.",
            ),
            warnings=warnings,
        )