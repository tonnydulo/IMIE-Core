from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    provider_name: str
    enabled: bool = True
    environment: str = "development"
