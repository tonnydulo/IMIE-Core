from typing import Any

from imie.execution.broker_execution_port import (
    BrokerExecutionPort,
)
from imie.execution.mock_broker_execution_adapter import (
    MockBrokerExecutionAdapter,
)

__all__ = [
    "AlpacaPaperExecutionAdapter",
    "BrokerExecutionPort",
    "MockBrokerExecutionAdapter",
]


def __getattr__(name: str) -> Any:
    if name == "AlpacaPaperExecutionAdapter":
        from imie.execution.alpaca_paper_execution_adapter import (
            AlpacaPaperExecutionAdapter,
        )

        return AlpacaPaperExecutionAdapter

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )
