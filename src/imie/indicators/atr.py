from imie.models import MarketBar


def calculate_atr_wilder(bars: list[MarketBar], period: int = 14) -> float | None:
    if len(bars) < period + 1:
        return None

    true_ranges: list[float] = []

    for i in range(1, len(bars)):
        current = bars[i]
        previous = bars[i - 1]

        true_range = max(
            current.high - current.low,
            abs(current.high - previous.close),
            abs(current.low - previous.close),
        )
        true_ranges.append(true_range)

    first_atr = sum(true_ranges[:period]) / period
    atr = first_atr

    for true_range in true_ranges[period:]:
        atr = ((atr * (period - 1)) + true_range) / period

    return atr
