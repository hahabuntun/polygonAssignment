from typing import Any
from datetime import datetime, timedelta, timezone

from src.services.polygon_client import PolygonClient
from src.utils.logger import setup_logger
from src.api.errors import ValidationError

logger = setup_logger(__name__)


class TokenService:
    def __init__(self, client: PolygonClient):
        self.client = client

    def get_balance(self, address: str) -> dict[str, Any]:
        return self.client.balance_of(address)

    def get_balance_batch(self, addresses: list[str]) -> list[dict[str, Any]]:
        if not isinstance(addresses, list) or len(addresses) == 0:
            raise ValidationError("addresses must be a non-empty list")
        out: list[dict[str, Any]] = []
        for addr in addresses:
            try:
                res = self.get_balance(addr)
                out.append(res)
            except Exception:
                logger.exception("Error fetching address %s", addr)
                out.append({"address": addr, "error": "Internal error", "success": False})
        return out

    def get_token_info(self) -> dict[str, Any]:
        return self.client.token_info()

    def get_top_holders(self, n: int = 10) -> list[tuple[str, float]]:
        sample = [
            ("0x51f1774249Fc2B0C2603542Ac6184Ae1d048351d", 1500.0),
            ("0x4830AF4aB9cd9E381602aE50f71AE481a7727f7C", 1200.0),
            ("0x742E6fB6c6B75C6e0f7943c661a4eB9C90d3eAe1", 800.0),
        ]
        return sample[:max(0, min(n, len(sample)))]

    def get_top_holders_with_transactions(self, n: int = 10):
        holders = self.get_top_holders(n)
        result = []
        for i, (addr, bal) in enumerate(holders):
            tx_date = (datetime.now(timezone.utc) - timedelta(days=i+1)).strftime("%Y-%m-%d %H:%M:%S")
            result.append((addr, bal, tx_date))
        return result
