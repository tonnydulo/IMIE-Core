from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from imie.execution import (
    AlpacaPaperPositionQueryAdapter,
    BrokerPositionQueryPort,
)
from imie.models import BrokerPositionSnapshot, PositionDirection


NOW = datetime(2026, 8, 13, 20, 0, tzinfo=timezone.utc)


class Client:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        self.calls = []

    def get_open_position(self, symbol_or_asset_id):
        self.calls.append(symbol_or_asset_id)
        if self.error is not None:
            raise self.error
        return self.value


def alpaca_position(**overrides):
    values = {
        "symbol": "NVDA",
        "side": "long",
        "qty": "40",
        "avg_entry_price": "200.00",
        "current_price": "201.00",
        "unrealized_pl": "40.00",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def adapter(client, *, paper=True):
    return AlpacaPaperPositionQueryAdapter(
        trading_client=client,
        paper=paper,
        clock=lambda: NOW,
    )


def test_adapter_satisfies_position_query_port():
    value = adapter(Client(alpaca_position()))

    assert isinstance(value, BrokerPositionQueryPort)


def test_long_position_is_normalized_from_broker_truth():
    client = Client(alpaca_position())
    result = adapter(client).get_position(" nvda ")

    assert isinstance(result, BrokerPositionSnapshot)
    assert result.broker == "alpaca-paper"
    assert result.symbol == "NVDA"
    assert result.direction is PositionDirection.LONG
    assert result.quantity == 40
    assert result.average_entry_price == 200.0
    assert result.market_price == 201.0
    assert result.unrealized_pnl == 40.0
    assert result.observed_at == NOW
    assert client.calls == ["NVDA"]


def test_short_quantity_is_normalized_to_absolute_whole_shares():
    result = adapter(
        Client(
            alpaca_position(
                side="short",
                qty="-25",
                current_price="198",
                unrealized_pl="50",
            )
        )
    ).get_position("NVDA")

    assert result.direction is PositionDirection.SHORT
    assert result.quantity == 25


def test_404_position_response_means_flat_at_broker():
    error = RuntimeError("position does not exist")
    error.status_code = 404

    assert adapter(Client(error=error)).get_position("NVDA") is None


def test_non_404_broker_error_is_not_hidden():
    error = RuntimeError("endpoint unavailable")
    error.status_code = 503

    with pytest.raises(RuntimeError, match="endpoint unavailable"):
        adapter(Client(error=error)).get_position("NVDA")


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"symbol": "AMD"}, "does not match"),
        ({"side": "flat"}, "long or short"),
        ({"qty": "1.5"}, "whole shares"),
        ({"qty": "0"}, "whole shares"),
        ({"avg_entry_price": "bad"}, "avg_entry_price"),
        ({"current_price": "nan"}, "current_price"),
        ({"unrealized_pl": "inf"}, "unrealized_pl"),
    ],
)
def test_invalid_broker_position_payload_fails_closed(overrides, message):
    with pytest.raises(ValueError, match=message):
        adapter(Client(alpaca_position(**overrides))).get_position("NVDA")


def test_explicit_paper_gate_is_required():
    with pytest.raises(ValueError, match="paper mode"):
        adapter(Client(alpaca_position()), paper=False)


def test_clock_must_return_timezone_aware_datetime():
    value = AlpacaPaperPositionQueryAdapter(
        trading_client=Client(alpaca_position()),
        paper=True,
        clock=lambda: datetime(2026, 8, 13, 20, 0),
    )

    with pytest.raises(ValueError, match="timezone-aware"):
        value.get_position("NVDA")
