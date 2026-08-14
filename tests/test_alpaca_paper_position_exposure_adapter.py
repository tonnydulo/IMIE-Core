from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from imie.execution import (
    AlpacaPaperPositionExposureAdapter,
    BrokerPositionExposurePort,
)
from imie.models import BrokerPositionExposure


NOW = datetime(2026, 8, 14, 15, 30, tzinfo=timezone.utc)


class Client:
    def __init__(self, values=None, error=None):
        self.values = [] if values is None else values
        self.error = error
        self.calls = 0

    def get_all_positions(self):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.values


def adapter(client, *, paper=True, clock=lambda: NOW):
    return AlpacaPaperPositionExposureAdapter(
        trading_client=client,
        paper=paper,
        clock=clock,
    )


def test_adapter_satisfies_broker_position_exposure_port():
    assert isinstance(adapter(Client()), BrokerPositionExposurePort)


def test_all_open_symbols_are_normalized_from_broker_truth():
    client = Client([
        SimpleNamespace(symbol="nvda"),
        SimpleNamespace(symbol=" AAPL "),
    ])

    result = adapter(client).get_open_position_exposure()

    assert isinstance(result, BrokerPositionExposure)
    assert result.broker == "alpaca-paper"
    assert result.open_symbols == ("AAPL", "NVDA")
    assert result.open_position_count == 2
    assert result.observed_at == NOW
    assert client.calls == 1


def test_empty_broker_position_list_is_verified_flat_exposure():
    result = adapter(Client([])).get_open_position_exposure()

    assert result.open_symbols == ()
    assert result.open_position_count == 0


def test_broker_error_is_not_hidden():
    with pytest.raises(RuntimeError, match="unavailable"):
        adapter(Client(error=RuntimeError("unavailable"))).get_open_position_exposure()


@pytest.mark.parametrize("values", [None, object(), {"symbol": "NVDA"}])
def test_invalid_collection_fails_closed(values):
    client = Client()
    client.values = values
    with pytest.raises(TypeError, match="list or tuple"):
        adapter(client).get_open_position_exposure()


@pytest.mark.parametrize("symbol", [None, 123, " "])
def test_invalid_position_symbol_fails_closed(symbol):
    with pytest.raises((TypeError, ValueError), match="symbol"):
        adapter(Client([SimpleNamespace(symbol=symbol)])).get_open_position_exposure()


def test_duplicate_broker_symbols_fail_closed():
    with pytest.raises(ValueError, match="duplicates"):
        adapter(Client([
            SimpleNamespace(symbol="NVDA"),
            SimpleNamespace(symbol="nvda"),
        ])).get_open_position_exposure()


def test_explicit_paper_gate_is_required():
    with pytest.raises(ValueError, match="paper mode"):
        adapter(Client(), paper=False)


def test_client_must_expose_get_all_positions():
    with pytest.raises(TypeError, match="get_all_positions"):
        adapter(object())


@pytest.mark.parametrize(
    "clock, error",
    [
        (lambda: "now", TypeError),
        (lambda: datetime(2026, 8, 14, 15, 30), ValueError),
    ],
)
def test_clock_must_return_aware_datetime(clock, error):
    with pytest.raises(error):
        adapter(Client(), clock=clock).get_open_position_exposure()
