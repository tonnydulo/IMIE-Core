from enum import Enum


class PositionProtectionAttemptStatus(str, Enum):
    RESERVED = "reserved"
    ACCEPTED = "accepted"
    FAILED = "failed"
    UNCERTAIN = "uncertain"
