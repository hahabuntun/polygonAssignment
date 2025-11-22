from typing import Any
from web3 import Web3, HTTPProvider
from web3.exceptions import ContractLogicError
from src.utils.logger import setup_logger
from src.utils.validators import to_checksum
from config import AppConfig
from src.api.errors import BlockchainError, ServiceError

logger = setup_logger(__name__)
_cfg = AppConfig()


class PolygonClient:
    def __init__(self, rpc_urls: list[str] | None = None, contract_address: str | None = None, abi: list | None = None):
        self.rpc_urls = rpc_urls or _cfg.rpc.urls
        self.contract_address = Web3.to_checksum_address(contract_address or _cfg.contract.address)
        self.abi = abi or _cfg.contract.abi
        self.w3 = None

        for url in self.rpc_urls:
            try:
                provider = HTTPProvider(url.strip(), request_kwargs={"timeout": _cfg.web3_request_timeout})
                w3 = Web3(provider)
                if w3.is_connected():
                    self.w3 = w3
                    self.rpc_url = url.strip()
                    break
            except Exception:
                continue
        if not self.w3:
            raise BlockchainError(f"Unable to connect to any RPC: {self.rpc_urls}")

        self._contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
        logger.info("Connected to RPC: %s", self.rpc_url)

    def is_connected(self) -> bool:
        return bool(self.w3 and self.w3.is_connected())

    def _call(self, fn_name: str, *args) -> Any:
        if not self._contract:
            raise ServiceError("Contract not initialized")
        try:
            func = getattr(self._contract.functions, fn_name)(*args)
            return func.call()
        except ContractLogicError as exc:
            raise BlockchainError("Smart contract error") from exc
        except Exception as exc:
            raise ServiceError("RPC call failed") from exc

    def decimals(self) -> int:
        return self._call("decimals")

    def balance_of(self, address: str) -> dict[str, object]:
        try:
            checksum = to_checksum(address)
        except Exception:
            return {"address": address, "error": "Invalid address", "success": False}

        try:
            balance_wei = self._call("balanceOf", checksum)
            decimals = self.decimals()
            balance_formatted = balance_wei / (10 ** decimals)
            return {"address": address, "balance_wei": str(balance_wei), "balance_formatted": balance_formatted, "success": True}
        except (BlockchainError, ServiceError):
            return {"address": address, "error": "RPC or contract error", "success": False}
        except Exception:
            return {"address": address, "error": "Internal error", "success": False}

    def token_info(self) -> dict[str, object]:
        try:
            symbol = self._call("symbol")
            name = self._call("name")
            total_supply = self._call("totalSupply")
            decimals = self.decimals()
            total_fmt = total_supply / (10 ** decimals)
            return {
                "symbol": symbol,
                "name": name,
                "totalSupply": str(total_supply),
                "totalSupply_formatted": total_fmt,
                "decimals": decimals,
                "address": self.contract_address,
                "success": True
            }
        except (BlockchainError, ServiceError):
            return {"error": "RPC or contract error", "success": False}
        except Exception:
            return {"error": "Internal error", "success": False}
