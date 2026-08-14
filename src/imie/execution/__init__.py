from typing import Any

from imie.execution.broker_execution_port import (
    BrokerExecutionPort,
)
from imie.execution.broker_order_query_port import (
    BrokerOrderQueryPort,
)
from imie.execution.broker_position_query_port import BrokerPositionQueryPort
from imie.execution.broker_position_exposure_port import (
    BrokerPositionExposurePort,
)
from imie.execution.broker_position_protection_validator import (
    BrokerPositionProtectionValidator,
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
from imie.execution.position_protection_store import PositionProtectionStore
from imie.execution.position_protection_attempt_store import (
    PositionProtectionAttemptStore,
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
from imie.execution.existing_position_protection_guard import (
    ExistingPositionProtectionGuard,
)
from imie.execution.existing_position_protection_service import (
    ExistingPositionProtectionService,
)
from imie.execution.protection_audit_persistence_error import (
    ProtectionAuditPersistenceError,
)
from imie.execution.position_protection_status_service import (
    PositionProtectionStatusService,
)
from imie.execution.position_protection_reconciliation_engine import (
    PositionProtectionReconciliationEngine,
)
from imie.execution.position_protection_reconciliation_service import (
    PositionProtectionReconciliationService,
)
from imie.execution.position_protection_reconciliation_store import (
    PositionProtectionReconciliationStore,
)
from imie.execution.position_protection_reconciliation_history_service import (
    PositionProtectionReconciliationHistoryService,
)
from imie.execution.position_protection_monitoring_engine import (
    PositionProtectionMonitoringEngine,
)
from imie.execution.position_protection_monitoring_service import (
    PositionProtectionMonitoringService,
)
from imie.execution.execution_safety_engine import ExecutionSafetyEngine
from imie.execution.concurrent_position_safety_engine import (
    ConcurrentPositionSafetyEngine,
)
from imie.execution.execution_safety_submission_service import (
    ExecutionSafetySubmissionService,
)
from imie.execution.protected_execution_safety_service import (
    ProtectedExecutionSafetyService,
)
from imie.execution.execution_submission_fingerprint import (
    ExecutionSubmissionFingerprint,
)
from imie.execution.execution_submission_reservation_store import (
    ExecutionSubmissionReservationStore,
)
from imie.execution.json_file_execution_submission_reservation_store import (
    JsonFileExecutionSubmissionReservationStore,
)
from imie.execution.json_file_position_protection_reconciliation_store import (
    JsonFilePositionProtectionReconciliationStore,
)

__all__ = [
    "AlpacaPaperExecutionAdapter",
    "AlpacaPaperExistingPositionProtectionAdapter",
    "AlpacaPaperFillActivitySource",
    "AlpacaExistingPositionProtectionRequestBuilder",
    "AlpacaProtectedOrderRequestBuilder",
    "BrokerExecutionPort",
    "BrokerOrderQueryPort",
    "BrokerPositionQueryPort",
    "BrokerPositionExposurePort",
    "BrokerPositionProtectionValidator",
    "AlpacaPaperPositionQueryAdapter",
    "AlpacaPaperPositionExposureAdapter",
    "AlpacaPaperPositionProtectionServiceFactory",
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
    "PositionProtectionStore",
    "PositionProtectionAttemptStore",
    "JsonFilePositionProtectionAttemptStore",
    "JsonFilePositionProtectionStore",
    "PositionReconciliationService",
    "ProtectiveCoverageEngine",
    "ExistingPositionProtectionPlanBuilder",
    "ExistingPositionProtectionPort",
    "ExistingPositionProtectionGuard",
    "ExistingPositionProtectionService",
    "ProtectionAuditPersistenceError",
    "PositionProtectionStatusService",
    "PositionProtectionReconciliationEngine",
    "PositionProtectionReconciliationService",
    "PositionProtectionReconciliationStore",
    "PositionProtectionReconciliationHistoryService",
    "PositionProtectionMonitoringEngine",
    "PositionProtectionMonitoringService",
    "ExecutionSafetyEngine",
    "ConcurrentPositionSafetyEngine",
    "ExecutionSafetySubmissionService",
    "ProtectedExecutionSafetyService",
    "ExecutionSubmissionFingerprint",
    "ExecutionSubmissionReservationStore",
    "JsonFileExecutionSubmissionReservationStore",
    "JsonFilePositionProtectionReconciliationStore",
    "JsonFilePositionStateStore",
]


def __getattr__(name: str) -> Any:
    if name == "AlpacaPaperPositionExposureAdapter":
        from imie.execution.alpaca_paper_position_exposure_adapter import (
            AlpacaPaperPositionExposureAdapter,
        )

        return AlpacaPaperPositionExposureAdapter

    if name == "AlpacaPaperPositionProtectionServiceFactory":
        from imie.execution.alpaca_paper_position_protection_service_factory import (
            AlpacaPaperPositionProtectionServiceFactory,
        )

        return AlpacaPaperPositionProtectionServiceFactory

    if name == "AlpacaPaperPositionQueryAdapter":
        from imie.execution.alpaca_paper_position_query_adapter import (
            AlpacaPaperPositionQueryAdapter,
        )

        return AlpacaPaperPositionQueryAdapter

    if name == "AlpacaPaperExistingPositionProtectionAdapter":
        from imie.execution.alpaca_paper_existing_position_protection_adapter import (
            AlpacaPaperExistingPositionProtectionAdapter,
        )

        return AlpacaPaperExistingPositionProtectionAdapter

    if name == "AlpacaExistingPositionProtectionRequestBuilder":
        from imie.execution.alpaca_existing_position_protection_request_builder import (
            AlpacaExistingPositionProtectionRequestBuilder,
        )

        return AlpacaExistingPositionProtectionRequestBuilder

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
