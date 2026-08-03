from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ProviderStatus:
    provider_name: str
    connected: bool
    timestamp: datetime
    message: str = ""
