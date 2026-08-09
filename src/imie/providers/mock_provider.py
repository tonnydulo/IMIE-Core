from datetime import (
    UTC,
    datetime,
    timedelta,
)

from imie.models import (
    MarketBar,
    ProviderStatus,
    Quote,
)
from imie.providers.base_provider import (
    MarketDataProvider,
)


class MockProvider(MarketDataProvider):
    provider_name = "mock"

    def connect(self) -> ProviderStatus:
        return ProviderStatus(
            provider_name=self.provider_name,
            connected=True,
            timestamp=datetime.now(
                        UTC
            ),
            message="Mock provider connected.",
        )

    def disconnect(self) -> ProviderStatus:
        return ProviderStatus(
            provider_name=self.provider_name,
            connected=False,
            timestamp=datetime.now(
                        UTC
            ),
            message="Mock provider disconnected.",
        )

    def get_quote(
        self,
        symbol: str,
    ) -> Quote:
        return Quote(
            symbol=symbol,
            timestamp=datetime.now(
                        UTC
            ),
            bid=100.00,
            ask=100.05,
            last=100.03,
            volume=1_000_000,
            provider=self.provider_name,
        )

    def get_bars(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[MarketBar]:
        timeframe_minutes = {
            "1m": 1,
            "2m": 2,
            "5m": 5,
            "15m": 15,
        }

        if timeframe not in timeframe_minutes:
            raise ValueError(
                f"Unsupported timeframe: {timeframe}"
            )

        minutes = timeframe_minutes[
            timeframe
        ]

        now = datetime.now(
            UTC
        )

        current_interval_start = now.replace(
            minute=(
                now.minute
                - (
                    now.minute
                    % minutes
                )
            ),
            second=0,
            microsecond=0,
        )

        latest_completed = (
            current_interval_start
            - timedelta(
                minutes=minutes,
            )
        )

        bars: list[
            MarketBar
        ] = []

        for index in range(limit):
            timestamp = (
                latest_completed
                - timedelta(
                    minutes=(
                        minutes
                        * (
                            limit
                            - index
                            - 1
                        )
                    ),
                )
            )

            base_price = 98.00
            trend_step = 0.04

            close = (
                base_price
                + (
                    index
                    * trend_step
                )
            )

            pullback = (
                0.10
                if index % 7 == 0
                else 0.0
            )

            close -= pullback

            open_price = (
                close
                - 0.05
            )

            high = (
                max(
                    open_price,
                    close,
                )
                + 0.08
            )

            low = (
                min(
                    open_price,
                    close,
                )
                - 0.08
            )

            volume = (
                900_000
                + (
                    index
                    * 2_000
                )
            )

            bars.append(
                MarketBar(
                    symbol=symbol,
                    timestamp=timestamp,
                    open=open_price,
                    high=high,
                    low=low,
                    close=close,
                    volume=volume,
                    timeframe=timeframe,
                    provider=self.provider_name,
                )
            )

        return bars
