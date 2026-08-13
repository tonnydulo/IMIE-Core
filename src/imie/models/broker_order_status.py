from __future__ import annotations

from enum import Enum


class BrokerOrderStatus(str, Enum):
    PENDING_SUBMISSION = "pending_submission"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    PENDING_CANCEL = "pending_cancel"
    CANCELED = "canceled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REPLACED = "replaced"
    UNKNOWN = "unknown"

