from __future__ import annotations

import os

from pathlib import Path

from imie.runtime.runtime_health_summary import (
    RuntimeHealthSummary,
)


class JsonHealthFilePublisher:
    def __init__(
        self,
        path: str | Path,
        *,
        indent: int | None = 2,
        create_parent_directories: bool = True,
    ) -> None:
        if not isinstance(
            path,
            str | Path,
        ):
            raise TypeError(
                "path must be a string or Path."
            )

        resolved_path = Path(
            path
        )

        if not str(
            resolved_path
        ).strip():
            raise ValueError(
                "path cannot be empty."
            )

        if isinstance(
            indent,
            bool,
        ) or (
            indent is not None
            and not isinstance(
                indent,
                int,
            )
        ):
            raise TypeError(
                "indent must be an int or None."
            )

        if (
            indent is not None
            and indent < 0
        ):
            raise ValueError(
                "indent cannot be negative."
            )

        if not isinstance(
            create_parent_directories,
            bool,
        ):
            raise TypeError(
                "create_parent_directories must be a bool."
            )

        self.path = resolved_path
        self.indent = indent
        self.create_parent_directories = (
            create_parent_directories
        )

    def publish(
        self,
        summary: RuntimeHealthSummary,
    ) -> None:
        if not isinstance(
            summary,
            RuntimeHealthSummary,
        ):
            raise TypeError(
                "summary must be a RuntimeHealthSummary."
            )

        parent = self.path.parent

        if self.create_parent_directories:
            parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        temporary_path = self.path.with_name(
            f".{self.path.name}.tmp"
        )

        payload = summary.to_json(
            indent=self.indent
        )

        try:
            temporary_path.write_text(
                payload + "\n",
                encoding="utf-8",
            )

            os.replace(
                temporary_path,
                self.path,
            )
        finally:
            if temporary_path.exists():
                temporary_path.unlink()