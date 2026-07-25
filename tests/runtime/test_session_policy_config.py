import pytest

from imie.runtime import (
    SessionPolicyConfig,
)


def test_default_policy_configuration() -> None:
    config = SessionPolicyConfig()

    assert config.allow_premarket is True
    assert config.allow_regular_session is True
    assert config.allow_after_hours is False
    assert config.allow_closed is False


@pytest.mark.parametrize(
    "field_name",
    [
        "allow_premarket",
        "allow_regular_session",
        "allow_after_hours",
        "allow_closed",
    ],
)
def test_policy_flags_must_be_bool(
    field_name: str,
) -> None:
    arguments = {
        "allow_premarket": True,
        "allow_regular_session": True,
        "allow_after_hours": False,
        "allow_closed": False,
    }

    arguments[field_name] = "yes"

    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        SessionPolicyConfig(
            **arguments,  # type: ignore[arg-type]
        )