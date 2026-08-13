from __future__ import annotations

from imie.models import (
    BrokerFill,
    ExecutionPosition,
    PositionDirection,
)


class PositionStateEngine:
    """Apply ordered broker fills using average-cost position accounting."""

    def apply_fills(
        self,
        *,
        position: ExecutionPosition,
        fills: tuple[BrokerFill, ...],
        market_price: float | None = None,
    ) -> ExecutionPosition:
        if not isinstance(position, ExecutionPosition):
            raise TypeError("position must be an ExecutionPosition.")
        if not isinstance(fills, tuple) or not all(
            isinstance(fill, BrokerFill) for fill in fills
        ):
            raise TypeError("fills must be a tuple of BrokerFill.")

        seen: set[str] = set()
        previous_time = position.last_updated_at
        signed_quantity = position.signed_quantity
        average_entry = position.average_entry_price
        realized_pnl = position.realized_pnl

        for fill in fills:
            if fill.broker != position.broker or fill.symbol != position.symbol:
                raise ValueError("fill broker and symbol must match position.")
            if fill.fill_id in seen:
                raise ValueError(f"duplicate fill_id {fill.fill_id!r}.")
            seen.add(fill.fill_id)
            if fill.executed_at < previous_time:
                raise ValueError("fills must be chronological and not predate position.")
            previous_time = fill.executed_at

            delta = fill.quantity if fill.side == "buy" else -fill.quantity
            if signed_quantity == 0 or signed_quantity * delta > 0:
                old_quantity = abs(signed_quantity)
                new_quantity = old_quantity + abs(delta)
                average_entry = (
                    fill.price
                    if old_quantity == 0
                    else (
                        average_entry * old_quantity + fill.price * abs(delta)
                    ) / new_quantity
                )
                signed_quantity += delta
                continue

            closing_quantity = min(abs(signed_quantity), abs(delta))
            if signed_quantity > 0:
                realized_pnl += (fill.price - average_entry) * closing_quantity
            else:
                realized_pnl += (average_entry - fill.price) * closing_quantity

            resulting_quantity = signed_quantity + delta
            if resulting_quantity == 0:
                signed_quantity = 0
                average_entry = None
            elif signed_quantity * resulting_quantity > 0:
                signed_quantity = resulting_quantity
            else:
                signed_quantity = resulting_quantity
                average_entry = fill.price

        resolved_market_price = (
            market_price if market_price is not None else position.market_price
        )
        direction = (
            PositionDirection.LONG
            if signed_quantity > 0
            else PositionDirection.SHORT
            if signed_quantity < 0
            else PositionDirection.FLAT
        )
        quantity = abs(signed_quantity)
        unrealized_pnl = 0.0
        if quantity and resolved_market_price is not None:
            unrealized_pnl = (
                (resolved_market_price - average_entry) * quantity
                if direction is PositionDirection.LONG
                else (average_entry - resolved_market_price) * quantity
            )
        return ExecutionPosition(
            broker=position.broker,
            symbol=position.symbol,
            direction=direction,
            quantity=quantity,
            average_entry_price=average_entry,
            market_price=resolved_market_price,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=realized_pnl,
            last_updated_at=(fills[-1].executed_at if fills else position.last_updated_at),
            warnings=position.warnings,
        )

