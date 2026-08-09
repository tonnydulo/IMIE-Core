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
from imie.engines.order_blocks import OrderBlockDetector
from imie.engines.structure.core import StructureEngine


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
            trend_step = 0.02

            wave = (
                0.00,
                0.12,
                0.28,
                0.12,
                0.00,
                -0.12,
                -0.28,
                -0.12,
            )

            phase = (
                index
                % len(
                    wave
                )
            )

            wave_value = wave[
                phase
            ]

            close = (
                base_price
                + (
                    index
                    * trend_step
                )
                + wave_value
            )

            if index == 0:
                previous_close = (
                    close
                    - 0.04
                )
            else:
                previous_phase = (
                    index - 1
                ) % len(
                    wave
                )

                previous_close = (
                    base_price
                    + (
                        (
                            index - 1
                        )
                        * trend_step
                    )
                    + wave[
                        previous_phase
                    ]
                )

            open_price = previous_close

            wick_size = 0.06

            if phase == 2:
                high = (
                    max(
                        open_price,
                        close,
                    )
                    + 0.20
                )
            else:
                high = (
                    max(
                        open_price,
                        close,
                    )
                    + wick_size
                )

            if phase == 6:
                low = (
                    min(
                        open_price,
                        close,
                    )
                    - 0.20
                )
            else:
                low = (
                    min(
                        open_price,
                        close,
                    )
                    - wick_size
                )

            if index in (
                4,
                10,
            ):
                high = 99.20

            if index in (
                7,
                13,
            ):
                low = 97.20

            is_order_block_source = (
                index == limit - 2
            )

            is_order_block_displacement = (
                index == limit - 1
            )

            if is_order_block_source:
                open_price = close + 0.08
                high = open_price + 0.04
                low = close - 0.04

            if is_order_block_displacement:
                previous_source_close = bars[-1].close

                prior_high = max(
                    bar.high
                    for bar in bars
                )

                open_price = (
                    previous_source_close
                    - 0.02
                )

                close = (
                    prior_high
                    + 0.20
                )

                high = (
                    close
                    + 0.05
                )

                low = (
                    open_price
                    - 0.03
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

def test_mock_provider_generates_bullish_order_block() -> None:
    provider = MockProvider()

    bars = provider.get_bars(
        "NVDA",
        "2m",
        limit=40,
    )

    structure = StructureEngine().evaluate(
        # use the same TradingContext construction already used
        # by an existing structure test if this method requires context
    )
