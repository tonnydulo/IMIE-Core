from __future__ import annotations

from enum import Enum


class RuntimeHealthState(str, Enum):
    CREATED = "CREATED"
    STARTING = "STARTING"
    CONNECTED = "CONNECTED"
    RUNNING = "RUNNING"
    SLEEPING = "SLEEPING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"