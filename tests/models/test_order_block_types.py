from imie.models import (
    OrderBlockImportance,
    OrderBlockOrigin,
    OrderBlockSide,
    OrderBlockState,
)


def test_order_block_side_values() -> None:
    assert OrderBlockSide.BULLISH.value == "BULLISH"
    assert OrderBlockSide.BEARISH.value == "BEARISH"


def test_order_block_state_values() -> None:
    assert OrderBlockState.ACTIVE.value == "ACTIVE"
    assert OrderBlockState.TESTED.value == "TESTED"
    assert OrderBlockState.MITIGATED.value == "MITIGATED"
    assert OrderBlockState.BROKEN.value == "BROKEN"
    assert OrderBlockState.RETIRED.value == "RETIRED"


def test_order_block_importance_values() -> None:
    assert OrderBlockImportance.MINOR.value == "MINOR"
    assert (
        OrderBlockImportance.INTERMEDIATE.value
        == "INTERMEDIATE"
    )
    assert OrderBlockImportance.MAJOR.value == "MAJOR"


def test_order_block_origin_values() -> None:
    assert OrderBlockOrigin.BOS.value == "BOS"
    assert OrderBlockOrigin.CHOCH.value == "CHOCH"
    assert OrderBlockOrigin.MSS.value == "MSS"
    assert (
        OrderBlockOrigin.DISPLACEMENT.value
        == "DISPLACEMENT"
    )
    assert (
        OrderBlockOrigin.UNCLASSIFIED.value
        == "UNCLASSIFIED"
    )