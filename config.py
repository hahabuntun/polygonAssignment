import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT.joinpath(".env"))


def load_abi(path: Path) -> List[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@dataclass(frozen=True)
class RpcConfig:
    urls: List[str]


@dataclass(frozen=True)
class ContractConfig:
    address: str
    abi: List[dict]


@dataclass(frozen=True)
class AppConfig:
    rpc: RpcConfig = field(default_factory=lambda: RpcConfig(
        urls=[url.strip() for url in os.getenv(
            "POLYGON_RPC_URLS",
            "https://rpc.ankr.com/polygon,https://polygon-rpc.com,https://1rpc.io/matic"
        ).split(",")]
    ))
    contract: ContractConfig = field(default_factory=lambda: ContractConfig(
        address=os.getenv(
            "TOKEN_ADDRESS",
            "0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0"
        ),
        abi=load_abi(ROOT.joinpath("abi/erc20.json"))
    ))
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8080"))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    web3_request_timeout: int = int(os.getenv("WEB3_REQUEST_TIMEOUT", "10"))
    web3_pool_maxsize: int = int(os.getenv("WEB3_POOL_MAXSIZE", "10"))
    rate_limit_default: str = os.getenv("RATE_LIMIT_DEFAULT", "60/minute")
    secret_key: str = os.getenv("SECRET_KEY", "default-secret")
