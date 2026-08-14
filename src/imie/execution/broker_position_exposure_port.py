from __future__ import annotations

from typing import Protocol, runtime_checkable

from imie.models import BrokerPositionExposure


@runtime_checkable
class BrokerPositionExposurePort(Protocol):
    """Read-only boundary for verified broker-wide position exposure."""

    def get_open_position_exposure(self) -> BrokerPositionExposure:
        ...
