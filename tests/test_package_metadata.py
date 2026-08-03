from importlib.metadata import entry_points


def test_runtime_console_command_is_installed() -> None:
    console_scripts = entry_points(
        group="console_scripts",
    )

    matching_entries = [
        entry
        for entry in console_scripts
        if entry.name == "imie-runtime"
    ]

    assert len(matching_entries) == 1

    entry = matching_entries[0]

    assert entry.value == "imie.runtime_cli:main"


def test_runtime_console_command_loads_main() -> None:
    console_scripts = entry_points(
        group="console_scripts",
    )

    entry = next(
        entry
        for entry in console_scripts
        if entry.name == "imie-runtime"
    )

    loaded = entry.load()

    from imie.runtime_cli import main

    assert loaded is main