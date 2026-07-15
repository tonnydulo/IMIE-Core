from __future__ import annotations

from imie.engines.liquidity import LiquidityDetector
from imie.models.liquidity_finding import LiquidityFinding
from imie.models.swing import Swing


class StubLiquidityDetector:
    def detect(
        self,
        swings: tuple[Swing, ...],
    ) -> tuple[LiquidityFinding, ...]:
        return ()


def accepts_liquidity_detector(
    detector: LiquidityDetector,
) -> LiquidityDetector:
    return detector


def test_stub_satisfies_liquidity_detector_contract() -> None:
    detector = StubLiquidityDetector()

    accepted = accepts_liquidity_detector(detector)

    assert accepted.detect(()) == ()