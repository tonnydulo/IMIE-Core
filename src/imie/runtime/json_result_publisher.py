from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from imie.runtime.analysis_cycle_result import (
    AnalysisCycleResult,
)


class JsonResultPublisher:
    """
    Serializes and publishes one AnalysisCycleResult as JSON.

    The publisher emits a stable runtime-facing representation rather
    than exposing internal dataclass objects directly.
    """

    def __init__(
        self,
        *,
        output: Callable[[str], None] = print,
        indent: int | None = None,
        sort_keys: bool = True,
    ) -> None:
        if not callable(
            output
        ):
            raise TypeError(
                "output must be callable."
            )

        if (
            indent is not None
            and isinstance(
                indent,
                bool,
            )
        ):
            raise TypeError(
                "indent must be an int or None."
            )

        if (
            indent is not None
            and not isinstance(
                indent,
                int,
            )
        ):
            raise TypeError(
                "indent must be an int or None."
            )

        if (
            indent is not None
            and indent < 0
        ):
            raise ValueError(
                "indent cannot be negative."
            )

        if not isinstance(
            sort_keys,
            bool,
        ):
            raise TypeError(
                "sort_keys must be a bool."
            )

        self.output = output
        self.indent = indent
        self.sort_keys = sort_keys

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
        self.output(
            self.dumps(
                result
            )
        )

    def dumps(
        self,
        result: AnalysisCycleResult,
    ) -> str:
        payload = self.to_dict(
            result
        )

        return json.dumps(
            payload,
            indent=self.indent,
            sort_keys=self.sort_keys,
            allow_nan=False,
        )

    def to_dict(
        self,
        result: AnalysisCycleResult,
    ) -> dict[str, Any]:
        if not isinstance(
            result,
            AnalysisCycleResult,
        ):
            raise TypeError(
                "result must be an AnalysisCycleResult."
            )

        payload: dict[str, Any] = {
            "status": result.status.value,
            "symbol": result.symbol,
            "timeframe": result.timeframe,
            "started_at": (
                result.started_at.isoformat()
            ),
            "completed_at": (
                result.completed_at.isoformat()
            ),
            "message": result.message,
            "error_type": result.error_type,
            "completed_bar": None,
            "freshness": None,
            "decision": None,
        }

        if result.completed_bar is not None:
            payload["completed_bar"] = {
                "accepted": (
                    result.completed_bar.accepted
                ),
                "is_new": (
                    result.completed_bar.is_new
                ),
                "is_complete": (
                    result.completed_bar.is_complete
                ),
                "timestamp": (
                    result.completed_bar.timestamp.isoformat()
                    if result.completed_bar.timestamp
                    is not None
                    else None
                ),
                "reason": (
                    result.completed_bar.reason
                ),
            }

        if result.freshness is not None:
            payload["freshness"] = {
                "checked_at": (
                    result.freshness.checked_at.isoformat()
                ),
                "quote_timestamp": (
                    result.freshness
                    .quote_timestamp
                    .isoformat()
                ),
                "latest_bar_timestamp": (
                    result.freshness
                    .latest_bar_timestamp
                    .isoformat()
                ),
                "quote_age_seconds": (
                    result.freshness
                    .quote_age_seconds
                ),
                "bar_age_seconds": (
                    result.freshness
                    .bar_age_seconds
                ),
                "quote_bar_gap_seconds": (
                    result.freshness
                    .quote_bar_gap_seconds
                ),
                "quote_is_fresh": (
                    result.freshness
                    .quote_is_fresh
                ),
                "bar_is_fresh": (
                    result.freshness
                    .bar_is_fresh
                ),
                "timestamps_aligned": (
                    result.freshness
                    .timestamps_aligned
                ),
                "actionable": (
                    result.freshness.actionable
                ),
                "status": (
                    result.freshness.status
                ),
                "reason": (
                    result.freshness.reason
                ),
            }

        if result.decision is not None:
            payload["decision"] = {
                "decision": (
                    result.decision.decision.value
                ),
                "actionable": (
                    result.decision.actionable
                ),
                "confidence": (
                    result.decision.confidence
                ),
                "recommendation": (
                    result.decision.recommendation
                ),
                "reasons": list(
                    result.decision.reasons
                ),
                "warnings": list(
                    result.decision.warnings
                ),
                "timestamp": (
                    result.decision.timestamp.isoformat()
                ),
                "analyst_summary": {
                    analyst_id: {
                        "opinion": details[
                            "opinion"
                        ],
                        "confidence": details[
                            "confidence"
                        ],
                        "enabled": details[
                            "enabled"
                        ],
                    }
                    for (
                        analyst_id,
                        details,
                    ) in (
                        result.decision
                        .analyst_summary
                        .items()
                    )
                },
                "has_trade_plan": (
                    result.decision.trade_plan
                    is not None
                ),
                "has_institutional_context": (
                    result.decision
                    .institutional_context
                    is not None
                ),
            }

        return payload