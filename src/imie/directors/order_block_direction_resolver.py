from __future__ import annotations

from dataclasses import dataclass

from imie.models import (
    AnalystResult,
    InstitutionalDirection,
    OrderBlockAnalysis,
    OrderBlockSide,
)


@dataclass(frozen=True, slots=True)
class OrderBlockDirectionResolver:
    """
    Resolves completed OrderBlockAnalyst intelligence into a
    normalized InstitutionalDirection.

    Resolution order:

    1. Missing or disabled analyst results resolve to UNKNOWN.
    2. A valid OrderBlockAnalysis payload is evaluated first.
    3. The analyst opinion is parsed as a fallback.
    4. Conflicting bullish and bearish information resolves
       to UNKNOWN.

    First-pass interpretation:

    - bullish blocks and institutional demand are bullish;
    - bearish blocks and institutional supply are bearish;
    - active blocks on both sides are neutral;
    - unavailable or unresolved context is unknown.

    The resolver does not detect, build, score, or update order
    blocks and does not authorize trades.
    """

    def resolve(
        self,
        result: AnalystResult | None,
    ) -> InstitutionalDirection:
        """
        Resolve an optional OrderBlockAnalyst result.
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
        Resolve direction from an OrderBlockAnalysis payload.

        Nearest directional blocks take priority. If both bullish
        and bearish blocks remain available, the result is neutral.
        """
        if not isinstance(
            payload,
            OrderBlockAnalysis,
        ):
            return InstitutionalDirection.UNKNOWN

        bullish = (
            payload.nearest_bullish_block
            is not None
        )

        bearish = (
            payload.nearest_bearish_block
            is not None
        )

        if bullish and bearish:
            return InstitutionalDirection.NEUTRAL

        if bullish:
            return InstitutionalDirection.BULLISH

        if bearish:
            return InstitutionalDirection.BEARISH

        strongest_direction = (
            self._resolve_state_side(
                payload.strongest_block
            )
        )

        if (
            strongest_direction
            is not InstitutionalDirection.UNKNOWN
        ):
            return strongest_direction

        opinion_direction = self._resolve_text(
            payload.opinion
        )

        if (
            opinion_direction
            is not InstitutionalDirection.UNKNOWN
        ):
            return opinion_direction

        return InstitutionalDirection.UNKNOWN

    def _resolve_state_side(
        self,
        state: object | None,
    ) -> InstitutionalDirection:
        if state is None:
            return InstitutionalDirection.UNKNOWN

        finding = getattr(
            state,
            "finding",
            None,
        )

        side = getattr(
            finding,
            "side",
            None,
        )

        if side is OrderBlockSide.BULLISH:
            return InstitutionalDirection.BULLISH

        if side is OrderBlockSide.BEARISH:
            return InstitutionalDirection.BEARISH

        side_text = self._normalize(
            side
        )

        if side_text in {
            "BULLISH",
            "BUY",
            "LONG",
            "DEMAND",
        }:
            return InstitutionalDirection.BULLISH

        if side_text in {
            "BEARISH",
            "SELL",
            "SHORT",
            "SUPPLY",
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

        if self._contains_any(
            text,
            self._neutral_terms(),
        ):
            return InstitutionalDirection.NEUTRAL

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
            "BULLISH ORDER BLOCK",
            "BULLISH BLOCK",
            "BUY ORDER BLOCK",
            "LONG ORDER BLOCK",
            "INSTITUTIONAL DEMAND",
            "DEMAND BLOCK",
            "DEMAND REMAINS",
            "DEMAND BELOW PRICE",
            "BUYERS DEFEND",
            "BUYER DEFENDS",
            "BUYERS ARE DEFENDING",
            "SUPPORTING LONG",
            "SUPPORTS LONG",
        )

    @staticmethod
    def _bearish_terms() -> tuple[str, ...]:
        return (
            "BEARISH",
            "BEARISH ORDER BLOCK",
            "BEARISH BLOCK",
            "SELL ORDER BLOCK",
            "SHORT ORDER BLOCK",
            "INSTITUTIONAL SUPPLY",
            "SUPPLY BLOCK",
            "SUPPLY REMAINS",
            "SUPPLY ABOVE PRICE",
            "SELLERS DEFEND",
            "SELLER DEFENDS",
            "SELLERS ARE DEFENDING",
            "SUPPORTING SHORT",
            "SUPPORTS SHORT",
        )

    @staticmethod
    def _neutral_terms() -> tuple[str, ...]:
        return (
            "NEUTRAL",
            "BALANCED",
            "BALANCE",
            "ORDER FLOW REMAINS BALANCED",
            "BLOCKS ON BOTH SIDES",
            "ORDER BLOCKS ON BOTH SIDES",
            "BULLISH AND BEARISH BLOCKS REMAIN ACTIVE",
            "BOTH BULLISH AND BEARISH BLOCKS",
            "TWO-SIDED ORDER BLOCK CONTEXT",
            "TWO SIDED ORDER BLOCK CONTEXT",
        )

    @staticmethod
    def _unknown_terms() -> tuple[str, ...]:
        return (
            "UNKNOWN",
            "UNAVAILABLE",
            "UNRESOLVED",
            "UNCLEAR",
            "INDETERMINATE",
            "NO ACTIONABLE ORDER BLOCKS",
            "NO ACTIVE ORDER BLOCKS",
            "NO ORDER BLOCKS",
            "ORDER BLOCK CONTEXT UNAVAILABLE",
            "WAITING FOR ORDER BLOCKS",
        )

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