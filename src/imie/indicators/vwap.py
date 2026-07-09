from imie.models import MarketBar


def calculate_vwap(bars: list[MarketBar]) -> float | None:
    total_price_volume = 0.0
    total_volume = 0

    for bar in bars:
        typical_price = (bar.high + bar.low + bar.close) / 3
        total_price_volume += typical_price * bar.volume
        total_volume += bar.volume

    if total_volume == 0:
        return None

    return total_price_volume / total_volume
