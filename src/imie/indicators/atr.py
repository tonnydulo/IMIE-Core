from imie.models import MarketBar


def calculate_atr_wilder(
    bars: list[MarketBar],
    period: int = 14,
) -> float | None:
    """Calculate ATR using Wilder's recursive moving average."""
    if period <= 0:
        raise ValueError("ATR period must be greater than zero.")

    if len(bars) < period + 1:
        return None

    true_ranges: list[float] = []

    for index in range(1, len(bars)):
        current = bars[index]
        previous = bars[index - 1]

        true_range = max(
            current.high - current.low,
            abs(current.high - previous.close),
            abs(current.low - previous.close),
        )
        true_ranges.append(true_range)

    atr = sum(true_ranges[:period]) / period

    for true_range in true_ranges[period:]:
        atr = ((period - 1) * atr + true_range) / period

    return atr
