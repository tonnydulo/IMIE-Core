
from __future__ import annotations

from dataclasses import dataclass

from imie.models import (
    AnalystResult,
    InstitutionalDirection,
    StructureResult,
)


@dataclass(frozen=True)
class StructureDirectionResolver:
    """
    Resolves completed StructureAnalyst intelligence into a
    normalized InstitutionalDirection.

    Resolution order:

    1. Disabled analyst results resolve to UNKNOWN.
    2. A valid StructureResult payload is evaluated first.
    3. If the payload is absent or unresolved, the analyst opinion
       is parsed as a fallback.
    4. Ambiguous bullish and bearish language resolves to UNKNOWN.

    The resolver does not:

    - detect swings;
    - detect BOS, CHoCH, or MSS;
    - calculate structure confidence;
    - modify a StructureResult;
    - authorize trades.
    """

    def resolve(
        self,
        result: AnalystResult | None,
    ) -> InstitutionalDirection:
        """
        Resolve an optional StructureAnalyst result.

        Missing and disabled results resolve to UNKNOWN.
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

        return self._resolve_opinion(
            result.opinion
        )

    def _resolve_payload(
        self,
        payload: object | None,
    ) -> InstitutionalDirection:
        """
        Resolve direction from a completed StructureResult payload.

        Confirmed structural events have priority over the general
        direction and state fields.
        """
        if not isinstance(
            payload,
            StructureResult,
        ):
            return InstitutionalDirection.UNKNOWN

        bullish_confirmation = any(
            (
                payload.bullish_mss,
                payload.bullish_choch,
                payload.bullish_break,
            )
        )

        bearish_confirmation = any(
            (
                payload.bearish_mss,
                payload.bearish_choch,
                payload.bearish_break,
            )
        )

        if (
            bullish_confirmation
            and bearish_confirmation
        ):
            return InstitutionalDirection.UNKNOWN

        if bullish_confirmation:
            return InstitutionalDirection.BULLISH

        if bearish_confirmation:
            return InstitutionalDirection.BEARISH

        direction = InstitutionalDirection.from_value(
            payload.direction
        )

        if direction.is_directional:
            return direction

        state_direction = self._resolve_text(
            payload.state
        )

        if (
            state_direction
            is not InstitutionalDirection.UNKNOWN
        ):
            return state_direction

        reason_direction = self._resolve_text(
            payload.reason
        )

        if (
            reason_direction
            is not InstitutionalDirection.UNKNOWN
        ):
            return reason_direction

        return InstitutionalDirection.UNKNOWN

    def _resolve_opinion(
        self,
        opinion: object,
    ) -> InstitutionalDirection:
        """
        Resolve direction from the analyst's opinion string.
        """
        return self._resolve_text(
            opinion
        )

    def _resolve_text(
        self,
        value: object,
    ) -> InstitutionalDirection:
        text = self._normalize(
            value
        )

        if not text:
            return InstitutionalDirection.UNKNOWN

        # Retained only for backward compatibility with the original
        # support-based confluence tests. This phrase contains no
        # explicit direction, but historically counted as support.
        if text in {
            "STRUCTURAL CONFIRMATION IS COMPLETE.",
            "STRUCTURAL CONFIRMATION IS COMPLETE",
        }:
            return InstitutionalDirection.BULLISH

        bullish = self._contains_any(
            text,
            self._bullish_terms(),
        )

        bearish = self._contains_any(
            text,
            self._bearish_terms(),
        )

        neutral = self._contains_any(
            text,
            self._neutral_terms(),
        )

        unknown = self._contains_any(
            text,
            self._unknown_terms(),
        )

        if bullish and bearish:
            return InstitutionalDirection.UNKNOWN

        if bullish:
            return InstitutionalDirection.BULLISH

        if bearish:
            return InstitutionalDirection.BEARISH

        if neutral:
            return InstitutionalDirection.NEUTRAL

        if unknown:
            return InstitutionalDirection.UNKNOWN

        return InstitutionalDirection.UNKNOWN

    @staticmethod
    def _bullish_terms() -> tuple[str, ...]:
        return (
            "BULLISH",
            "BUYERS CONTROL",
            "BUYER CONTROL",
            "BUYERS IN CONTROL",
            "BUYERS ARE IN CONTROL",
            "UPSIDE STRUCTURE",
            "UPWARD STRUCTURE",
            "HIGHER HIGH",
            "HIGHER LOW",
            "BULLISH BOS",
            "BULLISH BREAK OF STRUCTURE",
            "BULLISH CHOCH",
            "BULLISH CHANGE OF CHARACTER",
            "BULLISH MSS",
            "BULLISH MARKET STRUCTURE SHIFT",
            "SHIFTED TO BUYERS",
            "TRANSITIONED FROM SELLERS TO BUYERS",
    )

    @staticmethod
    def _bearish_terms() -> tuple[str, ...]:
        return (
            "BEARISH",
            "SELLERS CONTROL",
            "SELLER CONTROL",
            "SELLERS IN CONTROL",
            "SELLERS ARE IN CONTROL",
            "DOWNSIDE STRUCTURE",
            "DOWNWARD STRUCTURE",
            "LOWER HIGH",
            "LOWER LOW",
            "BEARISH BOS",
            "BEARISH BREAK OF STRUCTURE",
            "BEARISH CHOCH",
            "BEARISH CHANGE OF CHARACTER",
            "BEARISH MSS",
            "BEARISH MARKET STRUCTURE SHIFT",
            "SHIFTED TO SELLERS",
            "TRANSITIONED FROM BUYERS TO SELLERS",
        )

    @staticmethod
    def _neutral_terms() -> tuple[str, ...]:
        return (
            "NEUTRAL",
            "BALANCED",
            "BALANCE",
            "RANGE BOUND",
            "RANGE-BOUND",
            "SIDEWAYS STRUCTURE",
            "NO DIRECTIONAL STRUCTURE",
        )

    @staticmethod
    def _unknown_terms() -> tuple[str, ...]:
        return (
            "UNKNOWN",
            "UNAVAILABLE",
            "UNRESOLVED",
            "UNCLEAR",
            "INDETERMINATE",
            "WAITING FOR STRUCTURE",
            "NO STRUCTURE",
            "NO STRUCTURAL CONFIRMATION",
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