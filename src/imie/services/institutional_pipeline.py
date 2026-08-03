from __future__ import annotations

from dataclasses import replace

from imie.analysts import (
    AuctionAnalyst,
    LiquidityAnalyst,
    OrderBlockAnalyst,
    ParticipationAnalyst,
    PressureAnalyst,
    ValueAnalyst,
)
from imie.engines.liquidity import (
    EqualHighDetector,
    EqualLowDetector,
    LiquidityEngine,
    LiquidityPoolBuilder,
)
from imie.engines.order_blocks import (
    OrderBlockDetector,
)
from imie.engines.structure import (
    StructureAnalyst,
)
from imie.models import (
    AnalystResult,
    LiquidityPoolState,
    LiquidityPoolStateType,
    OrderBlockLifecycleState,
    OrderBlockStateType,
    StructureResult,
    TradingContext,
)
from imie.utils.analyst_ids import (
    ANALYST_LIQUIDITY,
    ANALYST_ORDER_BLOCK,
    ANALYST_STRUCTURE,
)


def build_institutional_results(
    context: TradingContext,
    trend_result: AnalystResult,
) -> tuple[
    AnalystResult,
    AnalystResult,
    AnalystResult,
    AnalystResult,
    AnalystResult,
    AnalystResult,
    AnalystResult,
]:  
    if not isinstance(
        trend_result,
        AnalystResult,
    ):
        raise TypeError(
            "trend_result must be an AnalystResult."
        )

    structure_result = StructureAnalyst().analyze(
        context
    )

    structure_result = replace(
        structure_result,
        analyst_id=ANALYST_STRUCTURE,
    )

    structure = structure_result.payload

    if not isinstance(
        structure,
        StructureResult,
    ):
        raise TypeError(
            "StructureAnalyst did not produce a "
            "StructureResult payload."
        )

    equal_high_findings = EqualHighDetector().detect(
        structure.swings
    )

    equal_low_findings = EqualLowDetector().detect(
        structure.swings
    )

    liquidity_findings = (
        *equal_high_findings,
        *equal_low_findings,
    )

    liquidity_pools = LiquidityPoolBuilder().build(
        liquidity_findings
    )

    liquidity_result = LiquidityEngine().evaluate(
        liquidity_pools
    )

    latest_bar_index = max(
        0,
        len(context.snapshot.bars) - 1,
    )

    liquidity_states = tuple(
        LiquidityPoolState(
            pool=pool,
            state=LiquidityPoolStateType.ACTIVE,
            created_bar=latest_bar_index,
            updated_bar=latest_bar_index,
            sweep_count=0,
            retest_count=0,
            evidence=(
                "Liquidity lifecycle initialized.",
            ),
            warnings=(),
        )
        for pool in liquidity_pools
    )

    liquidity_analyst_result = (
        LiquidityAnalyst().analyze_result(
            liquidity=liquidity_result,
            states=liquidity_states,
            sweeps=(),
        )
    )

    liquidity_analyst_result = replace(
        liquidity_analyst_result,
        analyst_id=ANALYST_LIQUIDITY,
    )

    market_bars = tuple(
        context.snapshot.bars
    )

    order_block_findings = OrderBlockDetector().detect(
        bars=market_bars,
        structure=structure,
    )

    order_block_states = tuple(
        OrderBlockLifecycleState(
            finding=finding,
            state=OrderBlockStateType.NEW,
            created_bar=finding.source_bar_index,
            last_touch_bar=None,
            touch_count=0,
            mitigation_count=0,
            active=True,
        )
        for finding in order_block_findings
    )

    order_block_result = (
        OrderBlockAnalyst().analyze_result(
            order_block_states
        )
    )

    order_block_result = replace(
        order_block_result,
        analyst_id=ANALYST_ORDER_BLOCK,
    )

    auction_result = AuctionAnalyst().analyze_result(
        context=context,
        trend=trend_result,
    )

    pressure_result = PressureAnalyst().analyze_result(
        context
    )

    participation_result = (
        ParticipationAnalyst().analyze_result(
            context=context,
            pressure_result=pressure_result,
        )
    )

    value_result = ValueAnalyst().analyze_result(
        context
    )


    return (
        structure_result,
        liquidity_analyst_result,
        order_block_result,
        auction_result,
        pressure_result,
        participation_result,
        value_result,
    )

   