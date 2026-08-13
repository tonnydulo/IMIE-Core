from enum import Enum


class ProtectiveCoverageStatus(str, Enum):
    NO_POSITION = "no_position"
    FLAT = "flat"
    READY = "ready"
    PARTIALLY_PROTECTED = "partially_protected"
    PROTECTED = "protected"
    MISMATCH = "mismatch"
