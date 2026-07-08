from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol:
    ticker: str
    name: str = ""
    asset_class: str = "equity"
    exchange: str = ""
    provider: str = ""
