from __future__ import annotations

from enum import StrEnum


class SessionPolicyAction(StrEnum):
    ANALYZE = "ANALYZE"
    SKIP = "SKIP"