from dataclasses import dataclass


@dataclass(frozen=True)
class AppSettings:
    app_name: str = "Institutional Market Intelligence Engine"
    version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"


def load_settings() -> AppSettings:
    return AppSettings()
