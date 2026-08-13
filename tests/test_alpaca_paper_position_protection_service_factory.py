from pathlib import Path

import pytest

from imie.config.settings import AppSettings
from imie.execution import (
    AlpacaPaperPositionProtectionServiceFactory,
    ExistingPositionProtectionService,
)


class PaperClient:
    def get_open_position(self, symbol_or_asset_id):
        raise NotImplementedError

    def submit_order(self, order_data):
        raise NotImplementedError

    def cancel_order_by_id(self, order_id):
        raise NotImplementedError


def settings(*, paper=True, key="paper-key", secret="paper-secret"):
    return AppSettings(
        alpaca_api_key=key,
        alpaca_secret_key=secret,
        alpaca_paper=paper,
    )


def create(tmp_path, **overrides):
    values = {
        "settings": settings(),
        "position_store_path": tmp_path / "positions.json",
        "protection_store_path": tmp_path / "protection.json",
        "attempt_store_path": tmp_path / "attempts.json",
        "trading_client": PaperClient(),
    }
    values.update(overrides)
    return AlpacaPaperPositionProtectionServiceFactory.create(**values)


def test_factory_wires_one_client_through_guarded_paper_service(tmp_path):
    client = PaperClient()
    service = create(tmp_path, trading_client=client)

    assert isinstance(service, ExistingPositionProtectionService)
    assert service._position_query_port._trading_client is client
    assert service._protection_port._trading_client is client
    assert service._position_store.path == tmp_path / "positions.json"
    assert service._protection_store.path == tmp_path / "protection.json"
    assert service._attempt_store.path == tmp_path / "attempts.json"


def test_factory_does_not_create_store_files_until_workflow_runs(tmp_path):
    create(tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_factory_requires_explicit_alpaca_paper_mode(tmp_path):
    with pytest.raises(ValueError, match="ALPACA_PAPER=true"):
        create(tmp_path, settings=settings(paper=False))


@pytest.mark.parametrize(
    "value",
    [settings(key=""), settings(secret="")],
)
def test_factory_requires_both_credentials(tmp_path, value):
    with pytest.raises(ValueError, match="ALPACA_API_KEY"):
        create(tmp_path, settings=value)


@pytest.mark.parametrize(
    "missing_method",
    ["get_open_position", "submit_order", "cancel_order_by_id"],
)
def test_factory_rejects_incomplete_client_before_service_creation(
    tmp_path, missing_method
):
    class Incomplete(PaperClient):
        pass

    client = Incomplete()
    setattr(client, missing_method, None)

    with pytest.raises(TypeError, match=missing_method):
        create(tmp_path, trading_client=client)


@pytest.mark.parametrize(
    "path_name",
    ["position_store_path", "protection_store_path", "attempt_store_path"],
)
def test_factory_requires_path_objects(tmp_path, path_name):
    with pytest.raises(TypeError, match=path_name):
        create(tmp_path, **{path_name: "not-a-path"})


def test_factory_module_is_not_imported_until_requested():
    import imie.execution as execution

    assert "TradingClient" not in execution.__dict__
