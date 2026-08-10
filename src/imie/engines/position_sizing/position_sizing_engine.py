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
        buying_power: float | None = None,
        maximum_notional: float | None = None,
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

        if buying_power is not None and buying_power <= 0:
            raise ValueError(
                "buying_power must be greater than zero."
            )

        if maximum_notional is not None and maximum_notional <= 0:
            raise ValueError(
                "maximum_notional must be greater than zero."
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

        risk_quantity = floor(
            risk_budget
            / trade_plan.risk_per_share
        )

        quantity = risk_quantity

        warnings: list[str] = []

        if buying_power is not None:
            buying_power_quantity = floor(
                buying_power
                / trade_plan.entry
            )

            if buying_power_quantity < quantity:
                quantity = buying_power_quantity

                warnings.append(
                    "Position size was constrained by available buying power."
                )

        if maximum_notional is not None:
            maximum_notional_quantity = floor(
                maximum_notional
                / trade_plan.entry
            )

            if maximum_notional_quantity < quantity:
                quantity = maximum_notional_quantity

                warnings.append(
                    "Position size was constrained by the maximum "
                    "notional limit."
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

        if not actionable:
            if risk_quantity < 1:
                warnings.append(
                    "Risk budget is insufficient for one share."
                )
            else:
                warnings.append(
                    "Capital constraints do not allow one share."
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
            warnings=tuple(warnings),
        )