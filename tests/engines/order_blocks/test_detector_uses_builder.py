from __future__ import annotations

from dataclasses import dataclass

from imie.engines.order_blocks import (
    OrderBlockBuilder,
    OrderBlockDetector,
)

from imie.models import (
    OrderBlockFinding,
    OrderBlockOrigin,
    OrderBlockSide,
)

from tests.engines.order_blocks.test_order_block_detector import (
    make_displacement_bar,
    make_source_bar,
    make_structure,
)


@dataclass(frozen=True, slots=True)
class StubBuilder(OrderBlockBuilder):

    def build_bullish(
        self,
        *,
        candidate,
        structure,
    ) -> OrderBlockFinding:

        return OrderBlockFinding(
            upper=2.0,
            lower=1.0,
            side=OrderBlockSide.BULLISH,
            origin=OrderBlockOrigin.BOS,
            source_bar_index=99,
            displacement=5.0,
            strength=88.0,
            confidence=95.0,
            reason="stub",
            evidence=("stub",),
            detector="StubBuilder",
    )


def test_detector_uses_builder() -> None:
    detector = OrderBlockDetector(
        builder=StubBuilder(),
    )

    findings = detector.detect(
        bars=(
            make_source_bar(),
            make_displacement_bar(),
        ),
        structure=make_structure(),
    )

    assert len(findings) == 1
    assert findings[0].detector == "StubBuilder"
    assert findings[0].source_bar_index == 99