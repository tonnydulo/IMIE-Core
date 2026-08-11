from __future__ import annotations

from collections.abc import Callable

from imie.runtime.analysis_cycle_result import (
    AnalysisCycleResult,
)
from imie.runtime.analysis_cycle_status import (
    AnalysisCycleStatus,
)


class ConsoleResultPublisher:
    """
    Formats and publishes one AnalysisCycleResult.

    Output is kept outside the runtime runners so orchestration
    remains independent of console, file, database, or UI concerns.
    """

    def __init__(
        self,
        *,
        output: Callable[[str], None] = print,
    ) -> None:
        if not callable(
            output
        ):
            raise TypeError(
                "output must be callable."
            )

        self.output = output

    def __call__(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        self.publish(
            result
        )

    def publish(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        if not isinstance(
            result,
            AnalysisCycleResult,
        ):
            raise TypeError(
                "result must be an AnalysisCycleResult."
            )

        for line in self.format_lines(
            result
        ):
            self.output(
                line
            )

    def format_lines(
        self,
        result: AnalysisCycleResult,
    ) -> tuple[str, ...]:
        if not isinstance(
            result,
            AnalysisCycleResult,
        ):
            raise TypeError(
                "result must be an AnalysisCycleResult."
            )

        lines: list[str] = [
            "=" * 60,
            "IMIE Runtime Cycle",
            f"Status       : {result.status.value}",
            f"Symbol       : {result.symbol}",
            f"Timeframe    : {result.timeframe}",
            (
                "Started      : "
                f"{result.started_at.isoformat()}"
            ),
            (
                "Completed    : "
                f"{result.completed_at.isoformat()}"
            ),
            f"Message      : {result.message}",
        ]

        if result.market_session is not None:
            lines.extend(
                [
                    (
                        "Session      : "
                        f"{result.market_session.state.value}"
                    ),
                    (
                        "Market Time  : "
                        f"{result.market_session.market_time.isoformat()}"
                    ),
                    (
                        "Trading Day  : "
                        f"{result.market_session.is_trading_day}"
                    ),
                ]
            )

        if result.session_policy is not None:
            lines.extend(
                [
                    (
                        "Session Action: "
                        f"{result.session_policy.action.value}"
                    ),
                    (
                        "Session Rule : "
                        f"{result.session_policy.reason}"
                    ),
                ]
            )

        if result.completed_bar is not None:
            bar_timestamp = (
                result.completed_bar.timestamp.isoformat()
                if result.completed_bar.timestamp is not None
                else "n/a"
            )

            lines.extend(
                [
                    f"Bar Time     : {bar_timestamp}",
                    (
                        "Bar Complete : "
                        f"{result.completed_bar.is_complete}"
                    ),
                    (
                        "Bar New      : "
                        f"{result.completed_bar.is_new}"
                    ),
                ]
            )

        if result.freshness is not None:
            lines.extend(
                [
                    (
                        "Freshness    : "
                        f"{result.freshness.status}"
                    ),
                    (
                        "Fresh Data   : "
                        f"{result.freshness.actionable}"
                    ),
                ]
            )

        if result.decision is not None:
            lines.extend(
                [
                    (
                        "Decision     : "
                        f"{result.decision.decision.value}"
                    ),
                    (
                        "Actionable   : "
                        f"{result.decision.actionable}"
                    ),
                    (
                        "Confidence   : "
                        f"{result.decision.confidence:.1f}"
                    ),
                    (
                        "Recommendation: "
                        f"{result.decision.recommendation}"
                    ),
                ]
            )

            if result.decision.reasons:
                lines.append(
                    "Reasons      :"
                )

                lines.extend(
                    f" - {reason}"
                    for reason in result.decision.reasons
                )

            if result.decision.warnings:
                lines.append(
                    "Warnings     :"
                )

                lines.extend(
                    f" - {warning}"
                    for warning in result.decision.warnings
                )

        if result.position_size is not None:
            position_size = result.position_size

            lines.extend(
                [
                    "Position Size :",
                    (
                        "Direction    : "
                        f"{position_size.direction}"
                    ),
                    (
                        "Risk Budget  : "
                        f"${position_size.risk_budget:.2f}"
                    ),
                    (
                        "Risk %       : "
                        f"{position_size.risk_percent:.2f}%"
                    ),
                    (
                        "Quantity     : "
                        f"{position_size.quantity}"
                    ),
                    (
                        "Notional     : "
                        f"${position_size.position_notional:.2f}"
                    ),
                    (
                        "Actual Risk  : "
                        f"${position_size.actual_risk:.2f}"
                    ),
                    (
                        "Actual Risk %: "
                        f"{position_size.actual_risk_percent:.4f}%"
                    ),
                    (
                        "Size Actionable: "
                        f"{position_size.actionable}"
                    ),
                ]
            )

            if position_size.warnings:
                lines.append(
                    "Sizing Warnings:"
                )

                lines.extend(
                    f" - {warning}"
                    for warning in position_size.warnings
                )

        if result.execution_candidate is not None:
            execution_candidate = (
                result.execution_candidate
            )

            lines.extend(
                [
                    "Execution Candidate :",
                    (
                        "Strategy     : "
                        f"{execution_candidate.strategy}"
                    ),
                    (
                        "Direction    : "
                        f"{execution_candidate.direction}"
                    ),
                    (
                        "Quantity     : "
                        f"{execution_candidate.quantity}"
                    ),
                    (
                        "Entry        : "
                        f"${execution_candidate.entry:.2f}"
                    ),
                    (
                        "Stop         : "
                        f"${execution_candidate.stop:.2f}"
                    ),
                    (
                        "Target 1     : "
                        f"${execution_candidate.target1:.2f}"
                    ),
                    (
                        "Target 2     : "
                        f"${execution_candidate.target2:.2f}"
                    ),
                    (
                        "Notional     : "
                        f"${execution_candidate.position_notional:.2f}"
                    ),
                    (
                        "Risk Amount  : "
                        f"${execution_candidate.risk_amount:.2f}"
                    ),
                    (
                        "Exec Valid   : "
                        f"{execution_candidate.valid}"
                    ),
                    (
                        "Exec Actionable: "
                        f"{execution_candidate.actionable}"
                    ),
                ]
            )

            if execution_candidate.warnings:
                lines.append(
                    "Execution Warnings:"
                )

                lines.extend(
                    f" - {warning}"
                    for warning
                    in execution_candidate.warnings
                )

        if (
            result.status
            is AnalysisCycleStatus.FAILED
        ):
            lines.append(
                "Error Type   : "
                f"{result.error_type or 'UnknownError'}"
            )

        lines.append(
            "=" * 60
        )

        return tuple(
            lines
        )