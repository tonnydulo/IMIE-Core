from __future__ import annotations

from pathlib import Path

from imie.runtime.analysis_cycle_result import (
    AnalysisCycleResult,
)
from imie.runtime.json_result_publisher import (
    JsonResultPublisher,
)


class JsonLinesResultPublisher:
    """
    Appends one AnalysisCycleResult as one JSON line.

    Each publish call writes one complete JSON document followed
    by a newline. Existing records are preserved.
    """

    def __init__(
        self,
        *,
        file_path: str | Path,
        serializer: JsonResultPublisher | None = None,
        encoding: str = "utf-8",
        create_parent_directories: bool = True,
    ) -> None:
        self.file_path = self._normalize_file_path(
            file_path
        )

        if (
            serializer is not None
            and not isinstance(
                serializer,
                JsonResultPublisher,
            )
        ):
            raise TypeError(
                "serializer must be a JsonResultPublisher "
                "or None."
            )

        if not isinstance(
            encoding,
            str,
        ):
            raise TypeError(
                "encoding must be a string."
            )

        normalized_encoding = encoding.strip()

        if not normalized_encoding:
            raise ValueError(
                "encoding cannot be empty."
            )

        if not isinstance(
            create_parent_directories,
            bool,
        ):
            raise TypeError(
                "create_parent_directories must be a bool."
            )

        self.serializer = (
            serializer
            or JsonResultPublisher(
                output=lambda value: None,
                indent=None,
                sort_keys=True,
            )
        )

        self.encoding = normalized_encoding
        self.create_parent_directories = (
            create_parent_directories
        )

    def __call__(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        self.publish(
            result
        )

    def publish(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        if not isinstance(
            result,
            AnalysisCycleResult,
        ):
            raise TypeError(
                "result must be an AnalysisCycleResult."
            )

        if self.create_parent_directories:
            self.file_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        serialized = self.serializer.dumps(
            result
        )

        with self.file_path.open(
            mode="a",
            encoding=self.encoding,
            newline="\n",
        ) as output_file:
            output_file.write(
                serialized
            )

            output_file.write(
                "\n"
            )

    @property
    def exists(self) -> bool:
        return self.file_path.exists()

    @property
    def record_count(self) -> int:
        if not self.file_path.exists():
            return 0

        with self.file_path.open(
            mode="r",
            encoding=self.encoding,
        ) as input_file:
            return sum(
                1
                for line in input_file
                if line.strip()
            )

    @staticmethod
    def _normalize_file_path(
        value: str | Path,
    ) -> Path:
        if isinstance(
            value,
            str,
        ):
            normalized = value.strip()

            if not normalized:
                raise ValueError(
                    "file_path cannot be empty."
                )

            path = Path(
                normalized
            )

        elif isinstance(
            value,
            Path,
        ):
            path = value

        else:
            raise TypeError(
                "file_path must be a string or Path."
            )

        if path.name in {
            "",
            ".",
            "..",
        }:
            raise ValueError(
                "file_path must identify a file."
            )

        if path.suffix.lower() not in {
            ".jsonl",
            ".ndjson",
        }:
            raise ValueError(
                "file_path must use a .jsonl or .ndjson "
                "extension."
            )

        return path