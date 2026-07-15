
from __future__ import annotations

from dataclasses import dataclass

from imie.models import (
    AnalystResult,
    InstitutionalDirection,
    LiquiditySide,
)


@dataclass(frozen=True, slots=True)
class LiquidityDirectionResolver:
    """
    Resolves completed LiquidityAnalyst intelligence into a
    normalized InstitutionalDirection.

    Resolution order:

    1. Missing or disabled analyst results resolve to UNKNOWN.
    2. Structured payload fields are evaluated first.
    3. The analyst opinion is parsed as a fallback.
    4. Conflicting bullish and bearish information resolves
       to UNKNOWN.

    First-pass directional interpretation:

    - demand, support, and buy-side liquidity are bullish;
    - supply, resistance, and sell-side liquidity are bearish;
    - balanced liquidity is neutral;
    - unavailable or unresolved liquidity is unknown.

    The resolver does not detect liquidity, build pools, detect
    sweeps, calculate confidence, or authorize trades.
    """

    def resolve(
        self,
        result: AnalystResult | None,
    ) -> InstitutionalDirection:
        """
        Resolve an optional LiquidityAnalyst result.
        """
        if result is None:
            return InstitutionalDirection.UNKNOWN

        if not isinstance(
            result,
            AnalystResult,
        ):
            raise TypeError(
                "result must be an AnalystResult or None."
            )

        if not result.enabled:
            return InstitutionalDirection.UNKNOWN

        payload_direction = self._resolve_payload(
            result.payload
        )

        if (
            payload_direction
            is not InstitutionalDirection.UNKNOWN
        ):
            return payload_direction

        return self._resolve_text(
            result.opinion
        )

    def _resolve_payload(
        self,
        payload: object | None,
    ) -> InstitutionalDirection:
        """
        Resolve direction from structured liquidity payload fields.

        The method supports the existing LiquidityAnalysis contract
        without requiring the payload to be used as a hard dependency.

        Recognized payload fields include:

        - institutional_bias
        - nearest_active_buy_pool
        - nearest_active_sell_pool
        - nearest_buy_pool
        - nearest_sell_pool
        - strongest_pool
        """
        if payload is None:
            return InstitutionalDirection.UNKNOWN

        buy_pool = self._first_attribute(
            payload,
            (
                "nearest_active_buy_pool",
                "nearest_buy_pool",
            ),
        )

        sell_pool = self._first_attribute(
            payload,
            (
                "nearest_active_sell_pool",
                "nearest_sell_pool",
            ),
        )

        if (
            buy_pool is not None
            and sell_pool is not None
        ):
            return InstitutionalDirection.NEUTRAL

        if buy_pool is not None:
            return InstitutionalDirection.BULLISH

        if sell_pool is not None:
            return InstitutionalDirection.BEARISH

        strongest_pool = getattr(
            payload,
            "strongest_pool",
            None,
        )

        strongest_direction = (
            self._resolve_pool_side(
                strongest_pool
            )
        )

        if (
            strongest_direction
            is not InstitutionalDirection.UNKNOWN
        ):
            return strongest_direction

        institutional_bias = getattr(
            payload,
            "institutional_bias",
            None,
        )

        bias_direction = self._resolve_text(
            institutional_bias
        )

        if (
            bias_direction
            is not InstitutionalDirection.UNKNOWN
        ):
            return bias_direction

        direction = getattr(
            payload,
            "direction",
            None,
        )

        direction_value = (
            InstitutionalDirection.from_value(
                direction
            )
        )

        if direction_value.is_directional:
            return direction_value

        return InstitutionalDirection.UNKNOWN

    def _resolve_pool_side(
        self,
        pool: object | None,
    ) -> InstitutionalDirection:
        if pool is None:
            return InstitutionalDirection.UNKNOWN

        side = getattr(
            pool,
            "side",
            None,
        )

        if side is LiquiditySide.BUY_SIDE:
            return InstitutionalDirection.BULLISH

        if side is LiquiditySide.SELL_SIDE:
            return InstitutionalDirection.BEARISH

        side_text = self._normalize(
            side
        )

        if side_text in {
            "BUY SIDE",
            "BUYSIDE",
            "BUY",
        }:
            return InstitutionalDirection.BULLISH

        if side_text in {
            "SELL SIDE",
            "SELLSIDE",
            "SELL",
        }:
            return InstitutionalDirection.BEARISH

        return InstitutionalDirection.UNKNOWN

    def _resolve_text(
        self,
        value: object,
    ) -> InstitutionalDirection:
        text = self._normalize(
            value
        )

        if not text:
            return InstitutionalDirection.UNKNOWN

        # Explicit neutral context takes priority.
        if self._contains_any(
            text,
            self._neutral_terms(),
        ):
            return InstitutionalDirection.NEUTRAL

        # A sell-side sweep means downside liquidity was taken,
        # which is interpreted as bullish confirmation.
        if self._contains_any(
            text,
            self._bullish_sweep_terms(),
        ):
            return InstitutionalDirection.BULLISH

        # A buy-side sweep means upside liquidity was taken,
        # which is interpreted as bearish confirmation.
        if self._contains_any(
            text,
            self._bearish_sweep_terms(),
        ):
            return InstitutionalDirection.BEARISH

        # Explicit liquidity location takes priority over generic
        # buy-side and sell-side terminology.
        if self._contains_any(
            text,
            self._bullish_location_terms(),
        ):
            return InstitutionalDirection.BULLISH

        if self._contains_any(
            text,
            self._bearish_location_terms(),
        ):
            return InstitutionalDirection.BEARISH

        bullish = self._contains_any(
            text,
            self._bullish_terms(),
        )

        bearish = self._contains_any(
            text,
            self._bearish_terms(),
        )

        if bullish and bearish:
            return InstitutionalDirection.UNKNOWN

        if bullish:
            return InstitutionalDirection.BULLISH

        if bearish:
            return InstitutionalDirection.BEARISH

        if self._contains_any(
            text,
            self._unknown_terms(),
        ):
            return InstitutionalDirection.UNKNOWN

        return InstitutionalDirection.UNKNOWN

    @staticmethod
    def _bullish_terms() -> tuple[str, ...]:
        return (
            "BULLISH",
            "DEMAND",
            "SUPPORT",
            "BUY SIDE",
            "BUYSIDE",
            "BUY-SIDE",
            "BUY LIQUIDITY",
            "BUYERS",
        )

    @staticmethod
    def _bearish_terms() -> tuple[str, ...]:
        return (
            "BEARISH",
            "SUPPLY",
            "RESISTANCE",
            "SELL SIDE",
            "SELLSIDE",
            "SELL-SIDE",
            "SELL LIQUIDITY",
            "SELLERS",
        )
    
    @staticmethod
    def _bullish_sweep_terms() -> tuple[str, ...]:
        return (
            "SELL-SIDE LIQUIDITY SWEPT",
            "SELL SIDE LIQUIDITY SWEPT",
            "SELLSIDE LIQUIDITY SWEPT",
            "SELL-SIDE SWEEP",
            "SELL SIDE SWEEP",
            "SELLSIDE SWEEP",
            "DOWNSIDE LIQUIDITY SWEPT",
        )


    @staticmethod
    def _bearish_sweep_terms() -> tuple[str, ...]:
        return (
            "BUY-SIDE LIQUIDITY SWEPT",
            "BUY SIDE LIQUIDITY SWEPT",
            "BUYSIDE LIQUIDITY SWEPT",
            "BUY-SIDE SWEEP",
            "BUY SIDE SWEEP",
            "BUYSIDE SWEEP",
            "UPSIDE LIQUIDITY SWEPT",
        )


    @staticmethod
    def _bullish_location_terms() -> tuple[str, ...]:
        return (
            "LIQUIDITY BELOW PRICE",
            "LIQUIDITY REMAINS BELOW PRICE",
            "DEMAND BELOW PRICE",
            "SUPPORT BELOW PRICE",
        )

    @staticmethod
    def _bearish_location_terms() -> tuple[str, ...]:
        return (
            "LIQUIDITY ABOVE PRICE",
            "LIQUIDITY REMAINS ABOVE PRICE",
            "SUPPLY ABOVE PRICE",
            "RESISTANCE ABOVE PRICE",
        )

    @staticmethod
    def _neutral_terms() -> tuple[str, ...]:
        return (
            "NEUTRAL",
            "BALANCED",
            "BALANCE",
            "LIQUIDITY ON BOTH SIDES",
            "LIQUIDITY REMAINS ACTIVE ON BOTH SIDES",
            "ACTIVE ON BOTH SIDES",
            "BOTH SIDES ACTIVE",
            "TWO-SIDED LIQUIDITY",
            "TWO SIDED LIQUIDITY",
        )

    @staticmethod
    def _unknown_terms() -> tuple[str, ...]:
        return (
            "UNKNOWN",
            "UNAVAILABLE",
            "UNRESOLVED",
            "UNCLEAR",
            "INDETERMINATE",
            "NO ACTIONABLE LIQUIDITY",
            "NO ACTIVE LIQUIDITY",
            "NO LIQUIDITY",
            "WAITING FOR LIQUIDITY",
            "LIQUIDITY CONTEXT UNAVAILABLE",
        )

    @staticmethod
    def _first_attribute(
        payload: object,
        names: tuple[str, ...],
    ) -> object | None:
        for name in names:
            value = getattr(
                payload,
                name,
                None,
            )

            if value is not None:
                return value

        return None

    @staticmethod
    def _contains_any(
        text: str,
        terms: tuple[str, ...],
    ) -> bool:
        return any(
            term in text
            for term in terms
        )

    @staticmethod
    def _normalize(
        value: object,
    ) -> str:
        enum_value = getattr(
            value,
            "value",
            value,
        )

        return " ".join(
            str(
                enum_value
            )
            .strip()
            .upper()
            .replace("_", " ")
            .split()
        )