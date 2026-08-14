from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from imie.execution import AlpacaPaperDailyPnlAdapter, BrokerDailyPnlPort
from imie.models import BrokerDailyPnlSnapshot


NOW = datetime(2026, 8, 14, 18, 0, tzinfo=timezone.utc)


class Client:
    def __init__(self, account=None, positions=None, error=None):
        self.account = account
        self.positions = [] if positions is None else positions
        self.error = error
        self.calls = []

    def get_account(self):
        self.calls.append("account")
        if self.error is not None:
            raise self.error
        return self.account

    def get_all_positions(self):
        self.calls.append("positions")
        if self.error is not None:
            raise self.error
        return self.positions


def account(equity="24900", last_equity="25000"):
    return SimpleNamespace(equity=equity, last_equity=last_equity)


def position(pnl):
    return SimpleNamespace(unrealized_intraday_pl=pnl)


def adapter(client, *, paper=True, clock=lambda: NOW):
    return AlpacaPaperDailyPnlAdapter(
        trading_client=client, paper=paper, clock=clock
    )


def test_adapter_satisfies_daily_pnl_port():
    assert isinstance(adapter(Client(account())), BrokerDailyPnlPort)


def test_account_and_position_truth_are_normalized():
    client = Client(
        account=account(equity="24750", last_equity="25000"),
        positions=[position("-75"), position("25")],
    )

    result = adapter(client).get_daily_pnl()

    assert isinstance(result, BrokerDailyPnlSnapshot)
    assert result.broker == "alpaca-paper"
    assert result.total_pnl == -250.0
    assert result.unrealized_pnl == -50.0
    assert result.realized_pnl == -200.0
    assert result.loss_amount == 250.0
    assert result.observed_at == NOW
    assert client.calls == ["account", "positions"]


def test_no_open_positions_assigns_total_pnl_to_realized():
    result = adapter(
        Client(account=account(equity="25100", last_equity="25000"))
    ).get_daily_pnl()

    assert result.total_pnl == 100.0
    assert result.realized_pnl == 100.0
    assert result.unrealized_pnl == 0.0


def test_broker_errors_are_not_hidden():
    with pytest.raises(RuntimeError, match="unavailable"):
        adapter(
            Client(account=account(), error=RuntimeError("unavailable"))
        ).get_daily_pnl()


@pytest.mark.parametrize(
    "account_value, field",
    [
        (account(equity="bad"), "equity"),
        (account(last_equity="nan"), "last_equity"),
    ],
)
def test_invalid_account_values_fail_closed(account_value, field):
    with pytest.raises(ValueError, match=field):
        adapter(Client(account=account_value)).get_daily_pnl()


def test_invalid_position_collection_fails_closed():
    with pytest.raises(TypeError, match="list or tuple"):
        adapter(Client(account=account(), positions=object())).get_daily_pnl()


@pytest.mark.parametrize("value", [None, "bad", "inf"])
def test_invalid_intraday_position_pnl_fails_closed(value):
    with pytest.raises(ValueError, match="unrealized_intraday_pl"):
        adapter(
            Client(account=account(), positions=[position(value)])
        ).get_daily_pnl()


def test_explicit_paper_gate_is_required():
    with pytest.raises(ValueError, match="paper mode"):
        adapter(Client(account=account()), paper=False)


@pytest.mark.parametrize("missing", ["get_account", "get_all_positions"])
def test_client_must_expose_both_read_methods(missing):
    class IncompleteClient:
        pass

    client = IncompleteClient()
    other = "get_all_positions" if missing == "get_account" else "get_account"
    setattr(client, other, lambda: None)
    with pytest.raises(TypeError, match=missing):
        adapter(client)


@pytest.mark.parametrize(
    "clock, error",
    [
        (lambda: "now", TypeError),
        (lambda: datetime(2026, 8, 14, 18, 0), ValueError),
    ],
)
def test_clock_must_return_aware_datetime(clock, error):
    with pytest.raises(error):
        adapter(Client(account=account()), clock=clock).get_daily_pnl()
