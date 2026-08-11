import pytest

from imie.runtime import PositionSizingConfig


def test_position_sizing_is_disabled_by_default() -> None:
    config = PositionSizingConfig()

    assert config.enabled is False
    assert config.account_equity is None
    assert config.risk_percent == pytest.approx(
        0.50
    )
    assert config.buying_power is None
    assert config.maximum_notional is None


def test_enabled_config_requires_account_equity() -> None:
    with pytest.raises(
        ValueError,
        match="account_equity is required",
    ):
        PositionSizingConfig(
            enabled=True,
        )


def test_enabled_config_accepts_account_constraints() -> None:
    config = PositionSizingConfig(
        enabled=True,
        account_equity=25_000,
        risk_percent=0.25,
        buying_power=20_000,
        maximum_notional=10_000,
    )

    assert config.enabled is True
    assert config.account_equity == pytest.approx(
        25_000.0
    )
    assert config.risk_percent == pytest.approx(
        0.25
    )
    assert config.buying_power == pytest.approx(
        20_000.0
    )
    assert config.maximum_notional == pytest.approx(
        10_000.0
    )


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("account_equity", 0.0),
        ("account_equity", -1.0),
        ("risk_percent", 0.0),
        ("risk_percent", -0.1),
        ("buying_power", 0.0),
        ("buying_power", -1.0),
        ("maximum_notional", 0.0),
        ("maximum_notional", -1.0),
    ],
)
def test_rejects_non_positive_values(
    field_name: str,
    value: float,
) -> None:
    arguments = {
        "enabled": False,
        field_name: value,
    }

    with pytest.raises(ValueError):
        PositionSizingConfig(
            **arguments,  # type: ignore[arg-type]
        )