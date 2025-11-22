from pathlib import Path
import sys
import pytest
from unittest.mock import MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


@pytest.fixture
def mock_polygon_client():
    client = MagicMock()

    def balance_side_effect(address):
        if address == "0x0000000000000000000000000000000000000001":
            return {"address": address, "balance_wei": "100000000000000000000", "balance_formatted": 100, "success": True}
        elif address == "0x0000000000000000000000000000000000000002":
            return {"address": address, "balance_wei": "200000000000000000000", "balance_formatted": 200, "success": True}
        return {"address": address, "error": "Invalid address", "success": False}

    client.balance_of.side_effect = balance_side_effect

    client.token_info.return_value = {
        "symbol": "TBY",
        "name": "TestToken",
        "totalSupply": "1000000000000000000000",
        "totalSupply_formatted": 1000,
        "decimals": 18,
        "address": "0x0000000000000000000000000000000000000001",
        "success": True
    }

    client.get_top_holders.return_value = [("0x0000000000000000000000000000000000000001", 100)]
    client.get_top_holders_with_transactions.return_value = [("0x0000000000000000000000000000000000000001", 100, "2025-11-22")]

    return client


@pytest.fixture
def token_service(mock_polygon_client):
    from src.services.token_service import TokenService

    class TestTokenService(TokenService):
        def get_top_holders(self, n: int = 10):
            return self.client.get_top_holders(n)

        def get_top_holders_with_transactions(self, n: int = 10):
            return self.client.get_top_holders_with_transactions(n)

    return TestTokenService(mock_polygon_client)
