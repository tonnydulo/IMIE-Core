from imie.models import MarketBar


def calculate_ema(
    bars: list[MarketBar],
    period: int,
    *,
    seed_method: str = "first",
) -> float | None:
    """
    Calculate an exponential moving average.

    seed_method:
        "first" - begins with the first close; useful for chart-style
                  recursive EMA calculations with sufficient warm-up data.
        "sma"   - begins with the SMA of the first `period` closes.
    """
    if period <= 0:
        raise ValueError("EMA period must be greater than zero.")

    if not bars:
        return None

    closes = [bar.close for bar in bars]
    alpha = 2.0 / (period + 1.0)

    if seed_method == "first":
        ema = closes[0]
        remaining_closes = closes[1:]
    elif seed_method == "sma":
        if len(closes) < period:
            return None

        ema = sum(closes[:period]) / period
        remaining_closes = closes[period:]
    else:
        raise ValueError(f"Unsupported EMA seed method: {seed_method}")

    for close in remaining_closes:
        ema = alpha * close + (1.0 - alpha) * ema

    return ema
