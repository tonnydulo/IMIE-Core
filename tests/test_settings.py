from imie.config.settings import (
    AppSettings,
    load_settings,
)


def test_alpaca_paper_is_disabled_by_default() -> None:
    assert AppSettings().alpaca_paper is False


def test_alpaca_paper_environment_requires_explicit_true(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "ALPACA_PAPER",
        "false",
    )

    assert load_settings().alpaca_paper is False

    monkeypatch.setenv(
        "ALPACA_PAPER",
        "true",
    )

    assert load_settings().alpaca_paper is True
