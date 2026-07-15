from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Analyst(Protocol):
    """
    Common interface implemented by every institutional analyst.

    Analysts consume completed engine outputs and return
    a domain-specific analysis object.

    Analysts never perform market detection.
    """

    def analyze(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Produce a domain analysis.

        Implementations define their own argument and return types.
        """
        ...