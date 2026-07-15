from __future__ import annotations

from enum import Enum


class InstitutionalDirection(str, Enum):
    """
    Normalized directional classification used by
    institutional reasoning components.

    Values:

    - BULLISH:
      The domain supports upward continuation or demand.

    - BEARISH:
      The domain supports downward continuation or supply.

    - NEUTRAL:
      The domain explicitly reports balanced or neutral context.

    - UNKNOWN:
      The domain does not provide enough information to resolve
      a direction.
    """

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"

    @property
    def is_bullish(self) -> bool:
        return self is InstitutionalDirection.BULLISH

    @property
    def is_bearish(self) -> bool:
        return self is InstitutionalDirection.BEARISH

    @property
    def is_neutral(self) -> bool:
        return self is InstitutionalDirection.NEUTRAL

    @property
    def is_unknown(self) -> bool:
        return self is InstitutionalDirection.UNKNOWN

    @property
    def is_directional(self) -> bool:
        return self in {
            InstitutionalDirection.BULLISH,
            InstitutionalDirection.BEARISH,
        }

    @property
    def is_resolved(self) -> bool:
        return self is not InstitutionalDirection.UNKNOWN

    @property
    def is_non_directional(self) -> bool:
        return self in {
            InstitutionalDirection.NEUTRAL,
            InstitutionalDirection.UNKNOWN,
        }

    def opposes(
        self,
        other: InstitutionalDirection,
    ) -> bool:
        """
        Return True when two resolved directional values oppose
        one another.

        Neutral and unknown values never count as opposition.
        """
        if not isinstance(
            other,
            InstitutionalDirection,
        ):
            raise TypeError(
                "other must be an InstitutionalDirection."
            )

        return (
            (
                self is InstitutionalDirection.BULLISH
                and other is InstitutionalDirection.BEARISH
            )
            or (
                self is InstitutionalDirection.BEARISH
                and other is InstitutionalDirection.BULLISH
            )
        )

    def aligns_with(
        self,
        other: InstitutionalDirection,
    ) -> bool:
        """
        Return True when both values represent the same resolved
        directional opinion.

        Neutral does not count as directional alignment.
        Unknown never counts as alignment.
        """
        if not isinstance(
            other,
            InstitutionalDirection,
        ):
            raise TypeError(
                "other must be an InstitutionalDirection."
            )

        return (
            self.is_directional
            and other.is_directional
            and self is other
        )

    @classmethod
    def from_value(
        cls,
        value: object,
    ) -> InstitutionalDirection:
        """
        Normalize an enum or string-like value into an
        InstitutionalDirection.

        Unrecognized values resolve to UNKNOWN instead of raising.
        """
        if isinstance(
            value,
            InstitutionalDirection,
        ):
            return value

        enum_value = getattr(
            value,
            "value",
            value,
        )

        text = str(
            enum_value
        ).strip().upper()

        aliases = {
            "BULL": cls.BULLISH,
            "LONG": cls.BULLISH,
            "UP": cls.BULLISH,
            "UPWARD": cls.BULLISH,
            "BULLISH": cls.BULLISH,
            "BEAR": cls.BEARISH,
            "SHORT": cls.BEARISH,
            "DOWN": cls.BEARISH,
            "DOWNWARD": cls.BEARISH,
            "BEARISH": cls.BEARISH,
            "NEUTRAL": cls.NEUTRAL,
            "BALANCED": cls.NEUTRAL,
            "BALANCE": cls.NEUTRAL,
            "NONE": cls.UNKNOWN,
            "UNKNOWN": cls.UNKNOWN,
            "UNAVAILABLE": cls.UNKNOWN,
            "UNRESOLVED": cls.UNKNOWN,
            "": cls.UNKNOWN,
        }

        return aliases.get(
            text,
            cls.UNKNOWN,
        )