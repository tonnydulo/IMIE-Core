from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from imie.execution import (
    AlpacaPaperMarketSessionAdapter,
    BrokerMarketSessionPort,
)
from imie.models import BrokerMarketSessionSnapshot


NOW = datetime(2026, 8, 14, 15, 30, tzinfo=timezone.utc)
NEXT_OPEN = datetime(2026, 8, 17, 13, 30, tzinfo=timezone.utc)
NEXT_CLOSE = datetime(2026, 8, 14, 20, 0, tzinfo=timezone.utc)


def clock(*, is_open=True, timestamp=NOW, next_open=NEXT_OPEN,
          next_close=NEXT_CLOSE):
    return SimpleNamespace(
        is_open=is_open,
        timestamp=timestamp,
        next_open=next_open,
        next_close=next_close,
    )


class Client:
    def __init__(self, value=None, error=None):
        self.value = clock() if value is None else value
        self.error = error
        self.calls = 0

    def get_clock(self):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.value


def adapter(client, *, paper=True):
    return AlpacaPaperMarketSessionAdapter(
        trading_client=client,
        paper=paper,
    )


def test_adapter_satisfies_market_session_port():
    value = adapter(Client())

    assert isinstance(value, BrokerMarketSessionPort)
    assert not hasattr(value, "submit_order")
    assert not hasattr(value, "submit_protected_plan")


@pytest.mark.parametrize("is_open", [True, False])
def test_broker_clock_is_translated_without_local_inference(is_open):
    client = Client(clock(is_open=is_open))

    result = adapter(client).get_market_session()

    assert isinstance(result, BrokerMarketSessionSnapshot)
    assert result.broker == "alpaca-paper"
    assert result.is_open is is_open
    assert result.observed_at == NOW
    assert result.next_open == NEXT_OPEN
    assert result.next_close == NEXT_CLOSE
    assert client.calls == 1


def test_broker_error_is_not_hidden():
    with pytest.raises(RuntimeError, match="unavailable"):
        adapter(Client(error=RuntimeError("unavailable"))).get_market_session()


def test_explicit_paper_gate_is_required():
    with pytest.raises(ValueError, match="paper mode"):
        adapter(Client(), paper=False)


def test_client_must_expose_get_clock():
    with pytest.raises(TypeError, match="get_clock"):
        adapter(object())


@pytest.mark.parametrize("value", [None, 1, "open"])
def test_is_open_must_be_bool(value):
    with pytest.raises(TypeError, match="is_open"):
        adapter(Client(clock(is_open=value))).get_market_session()


@pytest.mark.parametrize("field", ["timestamp", "next_open", "next_close"])
def test_clock_timestamps_are_required(field):
    values = {
        "timestamp": NOW,
        "next_open": NEXT_OPEN,
        "next_close": NEXT_CLOSE,
    }
    values[field] = None

    with pytest.raises(TypeError, match=field):
        adapter(Client(clock(**values))).get_market_session()


@pytest.mark.parametrize("field", ["timestamp", "next_open", "next_close"])
def test_clock_timestamps_must_be_timezone_aware(field):
    values = {
        "timestamp": NOW,
        "next_open": NEXT_OPEN,
        "next_close": NEXT_CLOSE,
    }
    values[field] = datetime(2026, 8, 14, 15, 30)

    with pytest.raises(ValueError, match=field):
        adapter(Client(clock(**values))).get_market_session()
