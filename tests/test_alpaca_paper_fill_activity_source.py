from __future__ import annotations

from datetime import datetime, timezone

import pytest

from imie.execution import (
    AlpacaPaperExecutionAdapter,
    AlpacaPaperFillActivitySource,
)


ORDER_ID = "11111111-1111-1111-1111-111111111111"


def activity(
    activity_id: str,
    *,
    order_id: str = ORDER_ID,
    activity_type: str = "FILL",
) -> dict[str, str]:
    return {
        "activity_type": activity_type,
        "id": activity_id,
        "order_id": order_id,
        "symbol": "NVDA",
        "side": "buy",
        "qty": "25",
        "price": "201.50",
        "transaction_time": "2026-08-13T18:00:02Z",
    }


class FakeResponse:
    def __init__(
        self,
        payload: object,
        error: Exception | None = None,
    ) -> None:
        self.payload = payload
        self.error = error

    def raise_for_status(self) -> None:
        if self.error is not None:
            raise self.error

    def json(self) -> object:
        return self.payload


class RecordingSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.calls: list[dict[str, object]] = []

    def get(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        return self.responses[len(self.calls) - 1]


def make_source(
    session: RecordingSession,
    **overrides: object,
) -> AlpacaPaperFillActivitySource:
    return AlpacaPaperFillActivitySource(
        api_key="paper-key",
        secret_key="paper-secret",
        session=session,
        **overrides,
    )


def test_source_calls_only_paper_fill_activity_endpoint() -> None:
    session = RecordingSession(
        [FakeResponse([activity("fill-1")])]
    )

    fills = make_source(session).get_fill_activities(f" {ORDER_ID} ")

    assert len(fills) == 1
    assert fills[0].order_id == ORDER_ID
    assert fills[0].transaction_time == datetime(
        2026, 8, 13, 18, 0, 2, tzinfo=timezone.utc
    )
    assert session.calls == [
        {
            "url": (
                "https://paper-api.alpaca.markets"
                "/v2/account/activities/FILL"
            ),
            "headers": {
                "APCA-API-KEY-ID": "paper-key",
                "APCA-API-SECRET-KEY": "paper-secret",
            },
            "params": {
                "order_id": ORDER_ID,
                "direction": "asc",
                "page_size": 100,
            },
            "timeout": 10.0,
        }
    ]


def test_source_paginates_using_last_activity_id() -> None:
    first_page = [activity(f"fill-{index:03d}") for index in range(100)]
    session = RecordingSession(
        [
            FakeResponse(first_page),
            FakeResponse([activity("fill-100")]),
        ]
    )

    fills = make_source(session).get_fill_activities(ORDER_ID)

    assert len(fills) == 101
    assert session.calls[1]["params"] == {
        "order_id": ORDER_ID,
        "direction": "asc",
        "page_size": 100,
        "page_token": "fill-099",
    }


def test_http_error_is_propagated() -> None:
    session = RecordingSession(
        [FakeResponse([], RuntimeError("paper endpoint unavailable"))]
    )

    with pytest.raises(RuntimeError, match="paper endpoint unavailable"):
        make_source(session).get_fill_activities(ORDER_ID)


@pytest.mark.parametrize(
    "payload",
    [
        {"activities": []},
        "not-a-list",
    ],
)
def test_response_must_be_a_list(payload: object) -> None:
    with pytest.raises(TypeError, match="must be a list"):
        make_source(
            RecordingSession([FakeResponse(payload)])
        ).get_fill_activities(ORDER_ID)


def test_cross_order_activity_is_rejected() -> None:
    with pytest.raises(ValueError, match="does not match"):
        make_source(
            RecordingSession(
                [FakeResponse([activity("fill-1", order_id="other")])]
            )
        ).get_fill_activities(ORDER_ID)


def test_non_fill_activity_is_rejected() -> None:
    with pytest.raises(ValueError, match="not a fill"):
        make_source(
            RecordingSession(
                [FakeResponse([activity("fill-1", activity_type="DIV")])]
            )
        ).get_fill_activities(ORDER_ID)


def test_repeated_pagination_token_fails_closed() -> None:
    repeated_page = [activity("same-token") for _ in range(100)]
    session = RecordingSession(
        [FakeResponse(repeated_page), FakeResponse(repeated_page)]
    )

    with pytest.raises(RuntimeError, match="repeated a token"):
        make_source(session).get_fill_activities(ORDER_ID)


def test_maximum_pages_fails_closed() -> None:
    full_page = [activity(f"fill-{index}") for index in range(100)]

    with pytest.raises(RuntimeError, match="maximum_pages"):
        make_source(
            RecordingSession([FakeResponse(full_page)]),
            maximum_pages=1,
        ).get_fill_activities(ORDER_ID)


def test_source_integrates_with_existing_fill_translator() -> None:
    source = make_source(
        RecordingSession([FakeResponse([activity("fill-1")])])
    )

    adapter = AlpacaPaperExecutionAdapter(
        api_key="paper-key",
        secret_key="paper-secret",
        trading_client=type(
            "SubmitClient",
            (),
            {"submit_order": lambda self, order_data: None},
        )(),
        fill_activity_source=source,
    )

    fills = adapter.get_order_fills(ORDER_ID)

    assert len(fills) == 1
    assert fills[0].fill_id == "fill-1"
    assert fills[0].quantity == 25
    assert fills[0].price == 201.50


@pytest.mark.parametrize(
    ("name", "value", "exception"),
    [
        ("api_key", "", ValueError),
        ("secret_key", None, TypeError),
        ("timeout_seconds", 0, ValueError),
        ("maximum_pages", 0, ValueError),
    ],
)
def test_configuration_validation(
    name: str,
    value: object,
    exception: type[Exception],
) -> None:
    arguments = {
        "api_key": "paper-key",
        "secret_key": "paper-secret",
        "session": RecordingSession([]),
    }
    arguments[name] = value

    with pytest.raises(exception, match=name):
        AlpacaPaperFillActivitySource(**arguments)

