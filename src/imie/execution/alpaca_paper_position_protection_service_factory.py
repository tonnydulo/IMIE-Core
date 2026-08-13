from __future__ import annotations

from pathlib import Path

from alpaca.trading.client import TradingClient

from imie.config.settings import AppSettings
from imie.execution.alpaca_paper_existing_position_protection_adapter import (
    AlpacaPaperExistingPositionProtectionAdapter,
)
from imie.execution.alpaca_paper_position_query_adapter import (
    AlpacaPaperPositionQueryAdapter,
)
from imie.execution.existing_position_protection_service import (
    ExistingPositionProtectionService,
)
from imie.execution.json_file_position_protection_attempt_store import (
    JsonFilePositionProtectionAttemptStore,
)
from imie.execution.json_file_position_protection_store import (
    JsonFilePositionProtectionStore,
)
from imie.execution.json_file_position_state_store import (
    JsonFilePositionStateStore,
)


class AlpacaPaperPositionProtectionServiceFactory:
    """Compose the guarded protection service for Alpaca paper only."""

    @classmethod
    def create(
        cls,
        *,
        settings: AppSettings,
        position_store_path: Path,
        protection_store_path: Path,
        attempt_store_path: Path,
        trading_client: object | None = None,
    ) -> ExistingPositionProtectionService:
        if not isinstance(settings, AppSettings):
            raise TypeError("settings must be an AppSettings.")
        if settings.alpaca_paper is not True:
            raise ValueError("position protection requires ALPACA_PAPER=true.")
        api_key = settings.alpaca_api_key.strip()
        secret_key = settings.alpaca_secret_key.strip()
        if not api_key or not secret_key:
            raise ValueError(
                "position protection requires ALPACA_API_KEY and "
                "ALPACA_SECRET_KEY."
            )
        for name, value in (
            ("position_store_path", position_store_path),
            ("protection_store_path", protection_store_path),
            ("attempt_store_path", attempt_store_path),
        ):
            if not isinstance(value, Path):
                raise TypeError(f"{name} must be a Path.")

        client = trading_client
        if client is None:
            client = TradingClient(
                api_key=api_key,
                secret_key=secret_key,
                paper=True,
            )
        cls._validate_client(client)

        return ExistingPositionProtectionService(
            position_store=JsonFilePositionStateStore(position_store_path),
            position_query_port=AlpacaPaperPositionQueryAdapter(
                trading_client=client,  # type: ignore[arg-type]
                paper=True,
            ),
            protection_port=AlpacaPaperExistingPositionProtectionAdapter(
                trading_client=client,  # type: ignore[arg-type]
                paper=True,
            ),
            protection_store=JsonFilePositionProtectionStore(
                protection_store_path
            ),
            attempt_store=JsonFilePositionProtectionAttemptStore(
                attempt_store_path
            ),
        )

    @staticmethod
    def _validate_client(client: object) -> None:
        for method in (
            "get_open_position",
            "submit_order",
            "cancel_order_by_id",
        ):
            if not callable(getattr(client, method, None)):
                raise TypeError(f"trading_client must expose {method}().")
