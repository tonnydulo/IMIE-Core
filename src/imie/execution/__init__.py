from typing import Any

from imie.execution.broker_execution_port import (
    BrokerExecutionPort,
)
from imie.execution.broker_order_query_port import (
    BrokerOrderQueryPort,
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

__all__ = [
    "AlpacaPaperExecutionAdapter",
    "AlpacaPaperFillActivitySource",
    "AlpacaProtectedOrderRequestBuilder",
    "BrokerExecutionPort",
    "BrokerOrderQueryPort",
    "ExecutionReconciliationEngine",
    "ExecutionReconciliationService",
    "MockBrokerExecutionAdapter",
    "ProtectedExecutionPlanBuilder",
    "ProtectedExecutionPort",
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
