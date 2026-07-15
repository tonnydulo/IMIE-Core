from __future__ import annotations

from dataclasses import dataclass

from imie.models import (
    AnalystResult,
    InstitutionalDirection,
)


@dataclass(frozen=True, slots=True)
class TrendDirectionResolver:
    """
    Resolves completed TrendAnalyst intelligence into a normalized
    InstitutionalDirection.

    Resolution order:

    1. Missing or disabled results resolve to UNKNOWN.
    2. Structured payload direction is evaluated first.
    3. Structured payload trend/state/opinion fields are evaluated.
    4. AnalystResult opinion is parsed as a fallback.
    5. Conflicting bullish and bearish language resolves UNKNOWN.

    The resolver does not calculate EMA, VWAP, trend confidence,
    or trade authorization.
    """

    def resolve(
        self,
        result: AnalystResult | None,
    ) -> InstitutionalDirection:
        """
        Resolve an optional TrendAnalyst result.
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
        Resolve direction from common structured trend fields.

        The resolver deliberately uses attribute inspection instead
        of depending on one concrete trend payload model. This keeps
        it compatible with existing and future TrendAnalyst payloads.
        """
        if payload is None:
            return InstitutionalDirection.UNKNOWN

        for attribute in (
            "direction",
            "trend",
            "trend_direction",
            "bias",
            "market_direction",
        ):
            value = getattr(
                payload,
                attribute,
                None,
            )

            direction = (
                InstitutionalDirection.from_value(
                    value
                )
            )

            if direction.is_directional:
                return direction

            text_direction = self._resolve_text(
                value
            )

            if (
                text_direction
                is not InstitutionalDirection.UNKNOWN
            ):
                return text_direction

        for attribute in (
            "state",
            "trend_state",
            "opinion",
            "reason",
            "narrative",
        ):
            value = getattr(
                payload,
                attribute,
                None,
            )

            direction = self._resolve_text(
                value
            )

            if (
                direction
                is not InstitutionalDirection.UNKNOWN
            ):
                return direction

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

        explicit_bullish = (
            "BULLISH" in text
        )

        explicit_bearish = (
            "BEARISH" in text
        )

        if explicit_bullish and explicit_bearish:
            return InstitutionalDirection.UNKNOWN

        if explicit_bullish:
            return InstitutionalDirection.BULLISH

        if explicit_bearish:
            return InstitutionalDirection.BEARISH

        # Specific unavailable or unresolved phrases must be checked
        # before generic neutral phrases such as "NO TREND".
        if self._contains_any(
            text,
            self._unknown_terms(),
        ):
            return InstitutionalDirection.UNKNOWN

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
            self._neutral_terms(),
        ):
            return InstitutionalDirection.NEUTRAL

        return InstitutionalDirection.UNKNOWN

    @staticmethod
    def _bullish_terms() -> tuple[str, ...]:
        return (
            "UPTREND",
            "UP TREND",
            "TRENDING HIGHER",
            "PRICE TRENDING HIGHER",
            "BUYERS CONTROL",
            "BUYERS ARE IN CONTROL",
            "BUYER CONTROL",
            "HIGHER HIGHS",
            "HIGHER LOWS",
            "HIGHER HIGH",
            "HIGHER LOW",
            "ABOVE EMA9",
            "ABOVE EMA 9",
            "ABOVE VWAP",
            "EMA9 RISING",
            "EMA 9 RISING",
            "RISING EMA9",
            "RISING EMA 9",
            "UPSIDE MOMENTUM",
            "POSITIVE TREND",
            "LONG BIAS",
            "UPWARD TREND",
            "UPWARD DIRECTION",
        )

    @staticmethod
    def _bearish_terms() -> tuple[str, ...]:
        return (
            "DOWNTREND",
            "DOWN TREND",
            "TRENDING LOWER",
            "PRICE TRENDING LOWER",
            "SELLERS CONTROL",
            "SELLERS ARE IN CONTROL",
            "SELLER CONTROL",
            "LOWER HIGHS",
            "LOWER LOWS",
            "LOWER HIGH",
            "LOWER LOW",
            "BELOW EMA9",
            "BELOW EMA 9",
            "BELOW VWAP",
            "EMA9 FALLING",
            "EMA 9 FALLING",
            "FALLING EMA9",
            "FALLING EMA 9",
            "DOWNSIDE MOMENTUM",
            "NEGATIVE TREND",
            "SHORT BIAS",
            "DOWNWARD TREND",
            "DOWNWARD DIRECTION",
        )

    @staticmethod
    def _neutral_terms() -> tuple[str, ...]:
        return (
            "NEUTRAL",
            "BALANCED",
            "BALANCE",
            "SIDEWAYS",
            "RANGE BOUND",
            "RANGE-BOUND",
            "CHOPPY",
            "NO TREND",
            "NO DIRECTIONAL TREND",
            "MIXED TREND",
            "FLAT TREND",
            "EMA9 FLAT",
            "EMA 9 FLAT",
        )

    @staticmethod
    def _unknown_terms() -> tuple[str, ...]:
        return (
            "UNKNOWN",
            "UNAVAILABLE",
            "UNRESOLVED",
            "UNCLEAR",
            "INDETERMINATE",
            "WAITING FOR TREND",
            "TREND CONTEXT UNAVAILABLE",
            "INSUFFICIENT TREND DATA",
            "NO TREND DATA",
            "TREND NOT EVALUATED",
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