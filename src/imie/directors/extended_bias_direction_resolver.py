from __future__ import annotations

from dataclasses import dataclass

from imie.models import (
    AnalystResult,
    InstitutionalDirection,
)


@dataclass(frozen=True)
class ExtendedBiasDirectionResolver:
    """
    Resolves optional extended institutional analyst results.

    Supported domains:

    - AUCTION
    - PRESSURE
    - PARTICIPATION
    - VALUE

    Resolution order:

    1. Missing or disabled results resolve to UNKNOWN.
    2. Structured payload direction fields are evaluated first.
    3. Domain-specific payload state and opinion fields follow.
    4. AnalystResult opinion is used as a fallback.
    5. Conflicting bullish and bearish language resolves UNKNOWN.

    Domain interpretation
    ---------------------

    Auction:
        Buyers controlling or accepting higher prices is bullish.
        Sellers controlling or accepting lower prices is bearish.
        Balanced discovery is neutral.

    Pressure:
        Buying or upward pressure is bullish.
        Selling or downward pressure is bearish.
        Balanced pressure is neutral.

    Participation:
        Participation must include directional context to resolve
        bullish or bearish. Strong participation alone is neutral.

    Value:
        Discount, below value, or value support is bullish.
        Premium, above value, or value resistance is bearish.
        Fair value is neutral.

    The resolver does not calculate analyst confidence, detect market
    events, or authorize trades.
    """

    SUPPORTED_DOMAINS = (
        "AUCTION",
        "PRESSURE",
        "PARTICIPATION",
        "VALUE",
    )

    def resolve(
        self,
        *,
        domain: str,
        result: AnalystResult | None,
    ) -> InstitutionalDirection:
        """
        Resolve one optional extended analyst result.
        """
        normalized_domain = self._normalize_domain(
            domain
        )

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
            domain=normalized_domain,
            payload=result.payload,
        )

        if (
            payload_direction
            is not InstitutionalDirection.UNKNOWN
        ):
            return payload_direction

        return self._resolve_text(
            domain=normalized_domain,
            value=result.opinion,
        )

    def _resolve_payload(
        self,
        *,
        domain: str,
        payload: object | None,
    ) -> InstitutionalDirection:
        if payload is None:
            return InstitutionalDirection.UNKNOWN

        for attribute in (
            "direction",
            "bias",
            "institutional_direction",
            "market_direction",
            "control_direction",
            "pressure_direction",
            "participation_direction",
            "value_direction",
        ):
            value = getattr(
                payload,
                attribute,
                None,
            )

            normalized = (
                InstitutionalDirection.from_value(
                    value
                )
            )

            if normalized.is_directional:
                return normalized

            text_direction = self._resolve_text(
                domain=domain,
                value=value,
            )

            if (
                text_direction
                is not InstitutionalDirection.UNKNOWN
            ):
                return text_direction

        for attribute in (
            "state",
            "control",
            "acceptance",
            "pressure",
            "participation",
            "value_state",
            "opinion",
            "reason",
            "narrative",
        ):
            direction = self._resolve_text(
                domain=domain,
                value=getattr(
                    payload,
                    attribute,
                    None,
                ),
            )

            if (
                direction
                is not InstitutionalDirection.UNKNOWN
            ):
                return direction

        return InstitutionalDirection.UNKNOWN

    def _resolve_text(
        self,
        *,
        domain: str,
        value: object,
    ) -> InstitutionalDirection:
        text = self._normalize_text(
            value
        )

        if not text:
            return InstitutionalDirection.UNKNOWN

        if self._contains_any(
            text,
            self._unknown_terms(
                domain
            ),
        ):
            return InstitutionalDirection.UNKNOWN

        explicit_bullish = (
            "BULLISH" in text
        )

        explicit_bearish = (
            "BEARISH" in text
        )

        if (
            explicit_bullish
            and explicit_bearish
        ):
            return InstitutionalDirection.UNKNOWN

        if explicit_bullish:
            return InstitutionalDirection.BULLISH

        if explicit_bearish:
            return InstitutionalDirection.BEARISH

        # Exhaustion reverses the meaning of the generic pressure term.
        # Selling pressure exhaustion is bullish.
        if (
            domain == "PRESSURE"
            and self._contains_any(
                text,
                self._bullish_exhaustion_terms(),
            )
        ):
            return InstitutionalDirection.BULLISH

        # Buying pressure exhaustion is bearish.
        if (
            domain == "PRESSURE"
            and self._contains_any(
                text,
                self._bearish_exhaustion_terms(),
            )
        ):
            return InstitutionalDirection.BEARISH

        bullish = self._contains_any(
            text,
            self._bullish_terms(
                domain
            ),
        )

        bearish = self._contains_any(
            text,
            self._bearish_terms(
                domain
            ),
        )

        if bullish and bearish:
            return InstitutionalDirection.UNKNOWN

        if bullish:
            return InstitutionalDirection.BULLISH

        if bearish:
            return InstitutionalDirection.BEARISH

        if self._contains_any(
            text,
            self._neutral_terms(
                domain
            ),
        ):
            return InstitutionalDirection.NEUTRAL

        return InstitutionalDirection.UNKNOWN

    @staticmethod
    def _bullish_terms(
        domain: str,
    ) -> tuple[str, ...]:
        terms = {
            "AUCTION": (
                "BUYERS CONTROL",
                "BUYER CONTROL",
                "BUYERS ARE IN CONTROL",
                "ACCEPTANCE HIGHER",
                "ACCEPTED HIGHER",
                "HIGHER PRICES ACCEPTED",
                "AUCTION MOVING HIGHER",
                "AUCTION TRENDING HIGHER",
                "UPWARD AUCTION",
                "DEMAND AUCTION",
                "SELLER REJECTION",
                "SELLERS REJECTED",
            ),
            "PRESSURE": (
                "BUYING PRESSURE",
                "BUY PRESSURE",
                "BULL PRESSURE",
                "UPWARD PRESSURE",
                "POSITIVE PRESSURE",
                "BUYERS APPLYING PRESSURE",
                "BUYERS DOMINATE PRESSURE",
                            ),
            "PARTICIPATION": (
                "BULLISH PARTICIPATION",
                "BUYER PARTICIPATION",
                "BUYING PARTICIPATION",
                "LONG PARTICIPATION",
                "PARTICIPATION SUPPORTS BUYERS",
                "PARTICIPATION SUPPORTS UPSIDE",
                "RISING PARTICIPATION WITH BUYERS",
                "STRONG PARTICIPATION HIGHER",
                "VOLUME SUPPORTS BUYERS",
            ),
            "VALUE": (
                "BELOW VALUE",
                "BELOW FAIR VALUE",
                "AT DISCOUNT",
                "IN DISCOUNT",
                "VALUE DISCOUNT",
                "UNDERVALUED",
                "DEMAND VALUE",
                "VALUE SUPPORT",
                "RECLAIMED VALUE",
                "RECLAIMING VALUE",
                "ACCEPTANCE ABOVE VALUE",
            ),
        }

        return terms[
            domain
        ]

    @staticmethod
    def _bearish_terms(
        domain: str,
    ) -> tuple[str, ...]:
        terms = {
            "AUCTION": (
                "SELLERS CONTROL",
                "SELLER CONTROL",
                "SELLERS ARE IN CONTROL",
                "ACCEPTANCE LOWER",
                "ACCEPTED LOWER",
                "LOWER PRICES ACCEPTED",
                "AUCTION MOVING LOWER",
                "AUCTION TRENDING LOWER",
                "DOWNWARD AUCTION",
                "SUPPLY AUCTION",
                "BUYER REJECTION",
                "BUYERS REJECTED",
            ),
            "PRESSURE": (
                "SELLING PRESSURE",
                "SELL PRESSURE",
                "BEAR PRESSURE",
                "DOWNWARD PRESSURE",
                "NEGATIVE PRESSURE",
                "SELLERS APPLYING PRESSURE",
                "SELLERS DOMINATE PRESSURE",
                
            ),
            "PARTICIPATION": (
                "BEARISH PARTICIPATION",
                "SELLER PARTICIPATION",
                "SELLING PARTICIPATION",
                "SHORT PARTICIPATION",
                "PARTICIPATION SUPPORTS SELLERS",
                "PARTICIPATION SUPPORTS DOWNSIDE",
                "RISING PARTICIPATION WITH SELLERS",
                "STRONG PARTICIPATION LOWER",
                "VOLUME SUPPORTS SELLERS",
            ),
            "VALUE": (
                "ABOVE VALUE",
                "ABOVE FAIR VALUE",
                "AT PREMIUM",
                "IN PREMIUM",
                "VALUE PREMIUM",
                "OVERVALUED",
                "SUPPLY VALUE",
                "VALUE RESISTANCE",
                "REJECTED VALUE",
                "REJECTING VALUE",
                "ACCEPTANCE BELOW VALUE",
            ),
        }

        return terms[
            domain
        ]
    
    @staticmethod
    def _bullish_exhaustion_terms() -> tuple[str, ...]:
        return (
            "SELLING PRESSURE EXHAUSTED",
            "SELL PRESSURE EXHAUSTED",
            "SELLER EXHAUSTION",
            "SELLERS EXHAUSTED",
        )


    @staticmethod
    def _bearish_exhaustion_terms() -> tuple[str, ...]:
        return (
            "BUYING PRESSURE EXHAUSTED",
            "BUY PRESSURE EXHAUSTED",
            "BUYER EXHAUSTION",
            "BUYERS EXHAUSTED",
        )

    @staticmethod
    def _neutral_terms(
        domain: str,
    ) -> tuple[str, ...]:
        common = (
            "NEUTRAL",
            "BALANCED",
            "BALANCE",
        )

        terms = {
            "AUCTION": (
                *common,
                "AUCTION DISCOVERY",
                "DISCOVERY PHASE",
                "TWO-SIDED AUCTION",
                "TWO SIDED AUCTION",
                "NO AUCTION CONTROL",
            ),
            "PRESSURE": (
                *common,
                "BALANCED PRESSURE",
                "NO PRESSURE ADVANTAGE",
                "BUYING AND SELLING PRESSURE BALANCED",
            ),
            "PARTICIPATION": (
                *common,
                "STRONG PARTICIPATION",
                "WEAK PARTICIPATION",
                "INCREASING PARTICIPATION",
                "DECREASING PARTICIPATION",
                "PARTICIPATION IS NON-DIRECTIONAL",
                "NO DIRECTIONAL PARTICIPATION",
            ),
            "VALUE": (
                *common,
                "AT FAIR VALUE",
                "FAIR VALUE",
                "INSIDE VALUE",
                "VALUE AREA",
                "VALUE ACCEPTANCE",
            ),
        }

        return terms[
            domain
        ]

    @staticmethod
    def _unknown_terms(
        domain: str,
    ) -> tuple[str, ...]:
        common = (
            "UNKNOWN",
            "UNAVAILABLE",
            "UNRESOLVED",
            "UNCLEAR",
            "INDETERMINATE",
            "NOT EVALUATED",
            "INSUFFICIENT DATA",
        )

        terms = {
            "AUCTION": (
                *common,
                "AUCTION CONTEXT UNAVAILABLE",
                "NO AUCTION DATA",
                "WAITING FOR AUCTION",
            ),
            "PRESSURE": (
                *common,
                "PRESSURE CONTEXT UNAVAILABLE",
                "NO PRESSURE DATA",
                "WAITING FOR PRESSURE",
            ),
            "PARTICIPATION": (
                *common,
                "PARTICIPATION CONTEXT UNAVAILABLE",
                "NO PARTICIPATION DATA",
                "WAITING FOR PARTICIPATION",
            ),
            "VALUE": (
                *common,
                "VALUE CONTEXT UNAVAILABLE",
                "NO VALUE DATA",
                "WAITING FOR VALUE",
            ),
        }

        return terms[
            domain
        ]

    @classmethod
    def _normalize_domain(
        cls,
        value: object,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "domain must be a string."
            )

        normalized = value.strip().upper()

        if not normalized:
            raise ValueError(
                "domain cannot be empty."
            )

        if normalized not in cls.SUPPORTED_DOMAINS:
            raise KeyError(
                "Unsupported extended bias domain: "
                f"{normalized}."
            )

        return normalized

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
    def _normalize_text(
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