from typing import Any

from imie.execution.broker_execution_port import (
    BrokerExecutionPort,
)
from imie.execution.broker_order_query_port import (
    BrokerOrderQueryPort,
)
from imie.execution.broker_order_intent_store import (
    BrokerOrderIntentStore,
)
from imie.execution.json_file_broker_order_intent_store import (
    JsonFileBrokerOrderIntentStore,
)
from imie.execution.mock_broker_execution_adapter import (
    MockBrokerExecutionAdapter,
)
from imie.execution.protected_execution_plan_builder import (
    ProtectedExecutionPlanBuilder,
)
from imie.execution.protected_execution_port import (
    ProtectedExecutionPort,
)
from imie.execution.execution_reconciliation_engine import (
    ExecutionReconciliationEngine,
)
from imie.execution.execution_reconciliation_service import (
    ExecutionReconciliationService,
)
from imie.execution.console_reconciliation_result_publisher import (
    ConsoleReconciliationResultPublisher,
)
from imie.execution.json_reconciliation_result_publisher import (
    JsonReconciliationResultPublisher,
)
from imie.execution.position_state_engine import PositionStateEngine
from imie.execution.position_state_store import PositionStateStore
from imie.execution.json_file_position_state_store import (
    JsonFilePositionStateStore,
)
from imie.execution.position_reconciliation_service import (
    PositionReconciliationService,
)
from imie.execution.protective_coverage_engine import ProtectiveCoverageEngine
from imie.execution.existing_position_protection_plan_builder import (
    ExistingPositionProtectionPlanBuilder,
)
from imie.execution.existing_position_protection_port import (
    ExistingPositionProtectionPort,
)

__all__ = [
    "AlpacaPaperExecutionAdapter",
    "AlpacaPaperFillActivitySource",
    "AlpacaProtectedOrderRequestBuilder",
    "BrokerExecutionPort",
    "BrokerOrderQueryPort",
    "BrokerOrderIntentStore",
    "ConsoleReconciliationResultPublisher",
    "ExecutionReconciliationEngine",
    "ExecutionReconciliationService",
    "JsonReconciliationResultPublisher",
    "JsonFileBrokerOrderIntentStore",
    "MockBrokerExecutionAdapter",
    "ProtectedExecutionPlanBuilder",
    "ProtectedExecutionPort",
    "PositionStateEngine",
    "PositionStateStore",
    "PositionReconciliationService",
    "ProtectiveCoverageEngine",
    "ExistingPositionProtectionPlanBuilder",
    "ExistingPositionProtectionPort",
    "JsonFilePositionStateStore",
]


def __getattr__(name: str) -> Any:
    if name == "AlpacaPaperExecutionAdapter":
        from imie.execution.alpaca_paper_execution_adapter import (
            AlpacaPaperExecutionAdapter,
        )

        return AlpacaPaperExecutionAdapter

    if name == "AlpacaPaperFillActivitySource":
        from imie.execution.alpaca_paper_fill_activity_source import (
            AlpacaPaperFillActivitySource,
        )

        return AlpacaPaperFillActivitySource

    if name == "AlpacaProtectedOrderRequestBuilder":
        from imie.execution.alpaca_protected_order_request_builder import (
            AlpacaProtectedOrderRequestBuilder,
        )

        return AlpacaProtectedOrderRequestBuilder

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )
