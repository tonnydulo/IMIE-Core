import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppSettings:
    app_name: str = "Institutional Market Intelligence Engine"
    version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"
    default_provider: str = "mock"

    schwab_app_key: str = ""
    schwab_app_secret: str = ""
    schwab_callback_url: str = "https://127.0.0.1"


def load_settings() -> AppSettings:
    load_dotenv()

    return AppSettings(
        environment=os.getenv("IMIE_ENVIRONMENT", "development"),
        log_level=os.getenv("IMIE_LOG_LEVEL", "INFO"),
        default_provider=os.getenv("IMIE_DEFAULT_PROVIDER", "mock"),
        schwab_app_key=os.getenv("SCHWAB_APP_KEY", ""),
        schwab_app_secret=os.getenv("SCHWAB_APP_SECRET", ""),
        schwab_callback_url=os.getenv("SCHWAB_CALLBACK_URL", "https://127.0.0.1"),
    )
