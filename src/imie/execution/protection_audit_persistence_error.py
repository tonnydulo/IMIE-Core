from __future__ import annotations

from imie.models import ExistingPositionProtectionResult


class ProtectionAuditPersistenceError(RuntimeError):
    """Broker accepted protection, but its local audit record was not saved."""

    def __init__(
        self,
        *,
        result: ExistingPositionProtectionResult,
        cause: Exception,
    ) -> None:
        if not isinstance(result, ExistingPositionProtectionResult):
            raise TypeError("result must be an ExistingPositionProtectionResult.")
        if not result.accepted:
            raise ValueError("result must represent accepted protection.")
        if not isinstance(cause, Exception):
            raise TypeError("cause must be an Exception.")
        self.result = result
        self.cause = cause
        super().__init__(
            "CRITICAL: broker accepted position protection, but the audit "
            f"record could not be persisted: {cause}"
        )
