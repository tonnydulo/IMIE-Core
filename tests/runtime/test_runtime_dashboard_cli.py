from pathlib import Path

from imie.runtime_dashboard import (
    build_parser,
)


def test_dashboard_parser_defaults() -> None:
    arguments = (
        build_parser()
        .parse_args(
            []
        )
    )

    assert (
        arguments.health_status_file
        == Path(
            "runtime/health.json"
        )
    )

    assert arguments.host == "127.0.0.1"
    assert arguments.port == 8765
    assert arguments.refresh_seconds == 2.0


def test_dashboard_parser_accepts_options() -> None:
    arguments = (
        build_parser()
        .parse_args(
            [
                "--health-status-file",
                "output/status.json",
                "--host",
                "localhost",
                "--port",
                "9000",
                "--refresh-seconds",
                "1",
            ]
        )
    )

    assert (
        arguments.health_status_file
        == Path(
            "output/status.json"
        )
    )

    assert arguments.host == "localhost"
    assert arguments.port == 9000
    assert arguments.refresh_seconds == 1.0