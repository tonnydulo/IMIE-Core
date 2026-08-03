from __future__ import annotations

import argparse

from pathlib import Path
from typing import Sequence

from imie.runtime.runtime_health_dashboard import (
    DEFAULT_DASHBOARD_HOST,
    DEFAULT_DASHBOARD_PORT,
    DEFAULT_REFRESH_SECONDS,
    run_dashboard,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imie-dashboard",
        description=(
            "Display the IMIE runtime health dashboard."
        ),
    )

    parser.add_argument(
        "--health-status-file",
        type=Path,
        default=Path(
            "runtime/health.json"
        ),
        help=(
            "Runtime health JSON file. Default: "
            "runtime/health.json."
        ),
    )

    parser.add_argument(
        "--host",
        default=DEFAULT_DASHBOARD_HOST,
        help=(
            "Dashboard host. Default: 127.0.0.1."
        ),
    )

    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_DASHBOARD_PORT,
        help=(
            "Dashboard port. Default: 8765."
        ),
    )

    parser.add_argument(
        "--refresh-seconds",
        type=float,
        default=DEFAULT_REFRESH_SECONDS,
        help=(
            "Browser refresh interval. Default: "
            "2 seconds."
        ),
    )

    return parser


def main(
    argv: Sequence[str] | None = None,
) -> int:
    parser = build_parser()

    arguments = parser.parse_args(
        argv
    )

    try:
        run_dashboard(
            health_status_file=(
                arguments.health_status_file
            ),
            host=arguments.host,
            port=arguments.port,
            refresh_seconds=(
                arguments.refresh_seconds
            ),
        )
    except (
        TypeError,
        ValueError,
        OSError,
    ) as error:
        parser.error(
            str(
                error
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )