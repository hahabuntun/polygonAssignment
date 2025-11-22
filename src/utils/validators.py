from web3 import Web3


def is_valid_address(address: str) -> bool:
    if not isinstance(address, str):
        return False
    try:
        return Web3.is_address(address)
    except Exception:
        return False


def to_checksum(address: str) -> str:
    return Web3.to_checksum_address(address)
