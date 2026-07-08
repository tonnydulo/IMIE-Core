import logging

from imie.config.settings import load_settings
from imie.utils.logging_utils import configure_logging
from imie.version import IMIE_NAME, IMIE_VERSION


def main() -> None:
    settings = load_settings()
    configure_logging(settings.log_level)

    logger = logging.getLogger("imie")
    logger.info("Starting IMIE Core")

    print("=" * 60)
    print(IMIE_NAME)
    print(f"Version : {IMIE_VERSION}")
    print("Status  : Initializing")
    print()
    print("? Configuration Loaded")
    print("? Logging Started")
    print("? Version Loaded")
    print("? Scanner Framework Ready")
    print()
    print("System Ready")
    print("=" * 60)


if __name__ == "__main__":
    main()
