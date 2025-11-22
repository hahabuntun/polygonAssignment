from dataclasses import dataclass


@dataclass
class BalanceDTO:
    address: str
    balance_wei: str
    balance_formatted: float
    success: bool = True


@dataclass
class TokenInfoDTO:
    symbol: str
    name: str
    totalSupply: str
    totalSupply_formatted: float
    decimals: int
    address: str
    success: bool = True


@dataclass
class ErrorDTO:
    error: str
    success: bool = False
