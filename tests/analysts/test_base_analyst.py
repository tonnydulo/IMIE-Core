from imie.analysts import Analyst, LiquidityAnalyst


def test_liquidity_analyst_implements_protocol() -> None:
    analyst = LiquidityAnalyst()

    assert isinstance(
        analyst,
        Analyst,
    )