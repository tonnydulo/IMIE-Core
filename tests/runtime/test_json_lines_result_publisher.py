import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from imie.runtime import (
    AnalysisCycleResult,
    AnalysisCycleStatus,
    JsonLinesResultPublisher,
    JsonResultPublisher,
)


CHECKED_AT = datetime(
    2026,
    7,
    18,
    14,
    32,
    3,
    tzinfo=timezone.utc,
)


def make_result(
    message: str = "No new completed bar.",
) -> AnalysisCycleResult:
    return AnalysisCycleResult(
        status=(
            AnalysisCycleStatus.SKIPPED_NO_NEW_BAR
        ),
        symbol="NVDA",
        timeframe="2m",
        started_at=CHECKED_AT,
        completed_at=CHECKED_AT,
        message=message,
    )


def test_publisher_can_be_created(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "cycles.jsonl"

    publisher = JsonLinesResultPublisher(
        file_path=file_path,
    )

    assert publisher.file_path == file_path
    assert publisher.encoding == "utf-8"
    assert publisher.create_parent_directories is True
    assert publisher.exists is False
    assert publisher.record_count == 0


@pytest.mark.parametrize(
    "file_path",
    [
        "",
        " ",
    ],
)
def test_file_path_cannot_be_empty(
    file_path: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="file_path",
    ):
        JsonLinesResultPublisher(
            file_path=file_path,
        )


def test_file_path_must_be_string_or_path() -> None:
    with pytest.raises(
        TypeError,
        match="file_path",
    ):
        JsonLinesResultPublisher(
            file_path=object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "file_name",
    [
        "cycles.json",
        "cycles.txt",
        "cycles",
    ],
)
def test_file_extension_must_be_json_lines(
    tmp_path: Path,
    file_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="extension",
    ):
        JsonLinesResultPublisher(
            file_path=tmp_path / file_name,
        )


def test_ndjson_extension_is_supported(
    tmp_path: Path,
) -> None:
    publisher = JsonLinesResultPublisher(
        file_path=tmp_path / "cycles.ndjson",
    )

    assert (
        publisher.file_path.suffix
        == ".ndjson"
    )


def test_serializer_must_be_json_result_publisher(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match="serializer",
    ):
        JsonLinesResultPublisher(
            file_path=tmp_path / "cycles.jsonl",
            serializer=object(),  # type: ignore[arg-type]
        )


def test_encoding_must_be_string(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match="encoding",
    ):
        JsonLinesResultPublisher(
            file_path=tmp_path / "cycles.jsonl",
            encoding=123,  # type: ignore[arg-type]
        )


def test_encoding_cannot_be_empty(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="encoding",
    ):
        JsonLinesResultPublisher(
            file_path=tmp_path / "cycles.jsonl",
            encoding=" ",
        )


def test_create_parent_directories_must_be_bool(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        TypeError,
        match="create_parent_directories",
    ):
        JsonLinesResultPublisher(
            file_path=tmp_path / "cycles.jsonl",
            create_parent_directories="yes",  # type: ignore[arg-type]
        )


def test_publish_creates_file_and_writes_record(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "cycles.jsonl"

    publisher = JsonLinesResultPublisher(
        file_path=file_path,
    )

    publisher.publish(
        make_result()
    )

    assert publisher.exists is True
    assert publisher.record_count == 1

    lines = file_path.read_text(
        encoding="utf-8",
    ).splitlines()

    assert len(
        lines
    ) == 1

    payload = json.loads(
        lines[0]
    )

    assert payload["status"] == (
        "SKIPPED_NO_NEW_BAR"
    )
    assert payload["symbol"] == "NVDA"
    assert payload["message"] == (
        "No new completed bar."
    )


def test_publish_appends_multiple_records(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "cycles.jsonl"

    publisher = JsonLinesResultPublisher(
        file_path=file_path,
    )

    publisher.publish(
        make_result(
            "Cycle 1",
        )
    )

    publisher.publish(
        make_result(
            "Cycle 2",
        )
    )

    assert publisher.record_count == 2

    lines = file_path.read_text(
        encoding="utf-8",
    ).splitlines()

    payloads = [
        json.loads(
            line
        )
        for line in lines
    ]

    assert [
        payload["message"]
        for payload in payloads
    ] == [
        "Cycle 1",
        "Cycle 2",
    ]


def test_publisher_is_callable(
    tmp_path: Path,
) -> None:
    publisher = JsonLinesResultPublisher(
        file_path=tmp_path / "cycles.jsonl",
    )

    publisher(
        make_result()
    )

    assert publisher.record_count == 1


def test_parent_directories_are_created(
    tmp_path: Path,
) -> None:
    file_path = (
        tmp_path
        / "runtime"
        / "history"
        / "cycles.jsonl"
    )

    publisher = JsonLinesResultPublisher(
        file_path=file_path,
    )

    publisher.publish(
        make_result()
    )

    assert file_path.exists()


def test_missing_parent_directory_raises_when_disabled(
    tmp_path: Path,
) -> None:
    file_path = (
        tmp_path
        / "missing"
        / "cycles.jsonl"
    )

    publisher = JsonLinesResultPublisher(
        file_path=file_path,
        create_parent_directories=False,
    )

    with pytest.raises(
        FileNotFoundError,
    ):
        publisher.publish(
            make_result()
        )


def test_custom_serializer_is_used(
    tmp_path: Path,
) -> None:
    serializer = JsonResultPublisher(
        output=lambda value: None,
        sort_keys=False,
    )

    publisher = JsonLinesResultPublisher(
        file_path=tmp_path / "cycles.jsonl",
        serializer=serializer,
    )

    assert publisher.serializer is serializer


def test_result_must_be_analysis_cycle_result(
    tmp_path: Path,
) -> None:
    publisher = JsonLinesResultPublisher(
        file_path=tmp_path / "cycles.jsonl",
    )

    with pytest.raises(
        TypeError,
        match="AnalysisCycleResult",
    ):
        publisher.publish(
            object(),  # type: ignore[arg-type]
        )