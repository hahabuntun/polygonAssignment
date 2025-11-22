import sys
import asyncio
from pathlib import Path
from colorama import Fore, Style, init
from aiohttp import ClientSession, ClientTimeout

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger

init(autoreset=True)
logger = setup_logger("functionality-tester")

API_BASE = "http://127.0.0.1:8080"
TEST_ADDRESSES = [
    "0x51f1774249Fc2B0C2603542Ac6184Ae1d048351d",
    "0x4830AF4aB9cd9E381602aE50f71AE481a7727f7C"
]

REQUEST_TIMEOUT = 12
RETRY_COUNT = 2
RETRY_DELAY = 0.6


def header(text: str):
    bar = "=" * max(40, len(text) + 4)
    logger.info(f"\n{bar}\n  {text}\n{bar}")


async def fetch(session: ClientSession, method: str, url: str, **kwargs):
    attempt = 0
    while attempt <= RETRY_COUNT:
        try:
            async with session.request(method, url, **kwargs) as resp:
                try:
                    data = await resp.json()
                except Exception:
                    data = {"_raw_text": await resp.text()}
                return {"status": resp.status, "data": data}
        except Exception as e:
            attempt += 1
            logger.warning(f"{Fore.YELLOW}Request error ({attempt}/{RETRY_COUNT+1}) for {url}: {e}{Style.RESET_ALL}")
            if attempt > RETRY_COUNT:
                return {"status": None, "data": {"error": str(e)}}
            await asyncio.sleep(RETRY_DELAY)


async def test_level_f(session: ClientSession):
    header("LEVEL F")
    url = f"{API_BASE}/health"
    logger.info(f"{Fore.CYAN}GET {url}{Style.RESET_ALL}")
    resp = await fetch(session, "GET", url)
    data = resp["data"]
    ok = isinstance(data, dict) and data.get("status") == "healthy"
    if ok:
        logger.info(Fore.GREEN + "Server healthy")
    else:
        logger.error(Fore.RED + "Health check failed")
    return ok


async def test_level_a(session: ClientSession):
    header("LEVEL A")
    for addr in TEST_ADDRESSES:
        url = f"{API_BASE}/api/get_balance?address={addr}"
        logger.info(f"{Fore.CYAN}GET {url}{Style.RESET_ALL}")
        resp = await fetch(session, "GET", url)
        data = resp["data"]
        if not isinstance(data, dict):
            logger.error(Fore.RED + f"Invalid response for {addr}")
            continue
        if data.get("success"):
            wei = data.get("balance_wei")
            fmt = data.get("balance_formatted")
            logger.info(Fore.GREEN + f"{addr[:10]}... → {fmt} TBY ({wei} wei)")
        else:
            logger.error(Fore.RED + f"{addr[:10]}... → {data.get('error')}")


async def test_level_b(session: ClientSession):
    header("LEVEL B")
    url = f"{API_BASE}/api/get_balance_batch"
    payload = {"addresses": TEST_ADDRESSES}
    logger.info(f"{Fore.CYAN}POST {url} payload={payload}{Style.RESET_ALL}")
    resp = await fetch(session, "POST", url, json=payload)
    data = resp["data"]
    if not isinstance(data, dict) or not data.get("success", False):
        logger.error(Fore.RED + f"Batch request failed: {data.get('error')}")
        return
    balances = data.get("balances", [])
    for item in balances:
        if item.get("success"):
            logger.info(Fore.GREEN + f"{item.get('address')[:10]}... → {item.get('balance_formatted')} TBY")
        else:
            logger.error(Fore.RED + f"{item.get('address')[:10]}... → {item.get('error')}")


async def test_level_c(session: ClientSession):
    header("LEVEL C")
    url = f"{API_BASE}/api/get_top?n=5"
    logger.info(f"{Fore.CYAN}GET {url}{Style.RESET_ALL}")
    resp = await fetch(session, "GET", url)
    data = resp["data"]
    if isinstance(data, dict) and data.get("success"):
        holders = data.get("top_holders", [])
        logger.info(Fore.GREEN + f"Found {len(holders)} holders (requested 5)")
        for h in holders:
            logger.info(f"  {h.get('address')[:12]}... balance={h.get('balance')}")
    else:
        logger.error(Fore.RED + f"get_top error: {data.get('error')}")


async def test_level_d(session: ClientSession):
    header("LEVEL D")
    url = f"{API_BASE}/api/get_top_with_transactions?n=5"
    logger.info(f"{Fore.CYAN}GET {url}{Style.RESET_ALL}")
    resp = await fetch(session, "GET", url)
    data = resp["data"]
    if isinstance(data, dict) and data.get("success"):
        holders = data.get("top_holders", [])
        logger.info(Fore.GREEN + f"Found {len(holders)} holders with tx dates")
        for h in holders:
            logger.info(f"  {h.get('address')[:12]}... balance={h.get('balance')} last_tx={h.get('last_transaction_date')}")
    else:
        logger.error(Fore.RED + f"get_top_with_transactions error: {data.get('error')}")


async def test_level_e(session: ClientSession):
    header("LEVEL E")
    url = f"{API_BASE}/api/get_token_info"
    logger.info(f"{Fore.CYAN}GET {url}{Style.RESET_ALL}")
    resp = await fetch(session, "GET", url)
    data = resp["data"]
    if isinstance(data, dict) and data.get("success"):
        logger.info(Fore.GREEN + f"Token {data.get('symbol')} ({data.get('name')})")
        logger.info(f"TotalSupply: {data.get('totalSupply_formatted')} {data.get('symbol')}")
        logger.info(f"Decimals: {data.get('decimals')}")
    else:
        logger.error(Fore.RED + f"token_info error: {data.get('error')}")


async def run_all():
    header("STARTING TEST")
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    async with ClientSession(timeout=timeout) as session:
        ok = await test_level_f(session)
        if not ok:
            logger.error(Fore.RED + "Server not available; aborting")
            return False
        await test_level_a(session)
        await test_level_b(session)
        await test_level_c(session)
        await test_level_d(session)
        await test_level_e(session)
    header("TEST SUITE FINISHED")
    return True


def main():
    try:
        result = asyncio.run(run_all())
        sys.exit(0 if result else 2)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Critical failure: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
