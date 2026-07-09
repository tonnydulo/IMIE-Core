from imie.models import MarketBar


def calculate_ema(bars: list[MarketBar], period: int) -> float | None:
    if len(bars) < period:
        return None

    closes = [bar.close for bar in bars]
    multiplier = 2 / (period + 1)
    ema = sum(closes[:period]) / period

    for close in closes[period:]:
        ema = (close - ema) * multiplier + ema

    return ema
