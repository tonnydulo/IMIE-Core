from imie.models import (
    DecisionResult,
    DirectorDecision,
)


def make_result(
    *,
    analyst_summary: (
        dict[str, dict[str, object]]
        | None
    ) = None,
) -> DecisionResult:
    return DecisionResult(
        decision=DirectorDecision.PREPARE,
        actionable=False,
        confidence=75.0,
        recommendation=(
            "Prepare for a possible validated setup."
        ),
        analyst_summary=(
            analyst_summary
            if analyst_summary is not None
            else {}
        ),
    )


def test_analyst_summary_marks_missing_confidence_unavailable(
) -> None:
    result = make_result(
        analyst_summary={
            "TREND": {
                "opinion": "Trend context unavailable.",
                "enabled": True,
            },
        }
    )

    trend = result.analyst_summary["TREND"]

    assert trend["confidence"] == 0.0
    assert trend["confidence_available"] is False


def test_analyst_summary_marks_explicit_zero_confidence_available(
) -> None:
    result = make_result(
        analyst_summary={
            "TREND": {
                "opinion": "Trend confidence is zero.",
                "confidence": 0.0,
                "enabled": True,
            },
        }
    )

    trend = result.analyst_summary["TREND"]

    assert trend["confidence"] == 0.0
    assert trend["confidence_available"] is True


def test_analyst_summary_marks_numeric_confidence_available(
) -> None:
    result = make_result(
        analyst_summary={
            "TREND": {
                "opinion": "Directional trend is bullish.",
                "confidence": 82.0,
                "enabled": True,
            },
        }
    )

    trend = result.analyst_summary["TREND"]

    assert trend["confidence"] == 82.0
    assert trend["confidence_available"] is True