from __future__ import annotations

import json
from pathlib import Path

from imie.runtime.runtime_health_snapshot import (
    RuntimeHealthSnapshot,
)


class JsonLinesHealthPublisher:
    """
    Appends one JSON object per runtime health transition.
    """

    def __init__(
        self,
        *,
        file_path: str | Path,
    ) -> None:
        if not isinstance(
            file_path,
            str | Path,
        ):
            raise TypeError(
                "file_path must be a string or Path."
            )

        resolved_path = Path(
            file_path
        )

        if not str(
            resolved_path
        ).strip():
            raise ValueError(
                "file_path cannot be empty."
            )

        self.file_path = resolved_path

    def publish(
        self,
        snapshot: RuntimeHealthSnapshot,
    ) -> None:
        if not isinstance(
            snapshot,
            RuntimeHealthSnapshot,
        ):
            raise TypeError(
                "snapshot must be a "
                "RuntimeHealthSnapshot."
            )

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "state": snapshot.state.value,
            "changed_at": (
                snapshot.changed_at.isoformat()
            ),
            "cycle_count": snapshot.cycle_count,
            "message": snapshot.message,
            "error_type": snapshot.error_type,
        }

        with self.file_path.open(
            "a",
            encoding="utf-8",
        ) as stream:
            stream.write(
                json.dumps(
                    payload,
                    separators=(
                        ",",
                        ":",
                    ),
                    sort_keys=True,
                )
            )
            stream.write(
                "\n"
            )