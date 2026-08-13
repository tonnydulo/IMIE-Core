from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ExecutionSubmissionReservation:
    fingerprint: str
    symbol: str
    side: str
    quantity: int
    reserved_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.fingerprint, str):
            raise TypeError("fingerprint must be a string.")
        fingerprint = self.fingerprint.strip().lower()
        if len(fingerprint) != 64 or any(
            character not in "0123456789abcdef" for character in fingerprint
        ):
            raise ValueError("fingerprint must be a 64-character SHA-256 hex digest.")
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("symbol must be a non-empty string.")
        if not isinstance(self.side, str):
            raise TypeError("side must be a string.")
        side = self.side.strip().lower()
        if side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell.")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an int.")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero.")
        if not isinstance(self.reserved_at, datetime):
            raise TypeError("reserved_at must be a datetime.")
        if self.reserved_at.tzinfo is None:
            raise ValueError("reserved_at must be timezone-aware.")
        object.__setattr__(self, "fingerprint", fingerprint)
        object.__setattr__(self, "symbol", self.symbol.strip().upper())
        object.__setattr__(self, "side", side)
