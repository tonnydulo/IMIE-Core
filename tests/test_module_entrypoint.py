from __future__ import annotations

import runpy

import imie.runtime_cli


def test_module_entrypoint_delegates_to_runtime_cli(
    monkeypatch,
) -> None:
    calls: list[bool] = []

    def fake_main() -> int:
        calls.append(
            True
        )
        return 0

    monkeypatch.setattr(
        imie.runtime_cli,
        "main",
        fake_main,
    )

    try:
        runpy.run_module(
            "imie",
            run_name="__main__",
        )
    except SystemExit as exc:
        assert exc.code == 0

    assert calls == [
        True
    ]