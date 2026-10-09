"""Check univ3-tick-math against a live Uniswap v3 pool.

Reads slot0() over plain JSON-RPC, verifies that the pool's stored tick equals
get_tick_at_sqrt_ratio(sqrtPriceX96), and prints the price with token decimals.

  python examples/check_live_pool.py
  python examples/check_live_pool.py --pool 0x... --rpc https://...
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tickmath import get_sqrt_ratio_at_tick, get_tick_at_sqrt_ratio, sqrtx96_to_price  # noqa: E402

USDC_WETH_005 = "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"  # Uniswap v3 USDC/WETH 0.05% on Ethereum
SLOT0, TOKEN0, TOKEN1, DECIMALS, SYMBOL = "0x3850c7bd", "0x0dfe1681", "0xd21220a7", "0x313ce567", "0x95d89b41"


def eth_call(rpc: str, to: str, data: str) -> bytes:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json",
                                                          "User-Agent": "univ3-tick-math"})
    with urllib.request.urlopen(req, timeout=20) as r:
        res = json.load(r)
    if "error" in res:
        raise RuntimeError(res["error"])
    return bytes.fromhex(res["result"][2:])


def word(data: bytes, i: int) -> int:
    return int.from_bytes(data[32 * i:32 * i + 32], "big")


def signed(value: int) -> int:
    return value - (1 << 256) if value >> 255 else value


def symbol(rpc: str, token: str) -> str:
    data = eth_call(rpc, token, SYMBOL)
    if len(data) == 32:  # a few old tokens return bytes32 instead of string
        return data.rstrip(b"\0").decode()
    return data[64:64 + word(data, 1)].decode()


def main() -> int:
    ap = argparse.ArgumentParser(description="Check univ3-tick-math against a live Uniswap v3 pool")
    ap.add_argument("--pool", default=USDC_WETH_005)
    ap.add_argument("--rpc", default="https://ethereum-rpc.publicnode.com")
    a = ap.parse_args()

    slot0 = eth_call(a.rpc, a.pool, SLOT0)
    sqrt_price, tick = word(slot0, 0), signed(word(slot0, 1))
    tokens = ["0x" + eth_call(a.rpc, a.pool, sel)[12:32].hex() for sel in (TOKEN0, TOKEN1)]
    dec0, dec1 = (word(eth_call(a.rpc, t, DECIMALS), 0) for t in tokens)
    sym0, sym1 = (symbol(a.rpc, t) for t in tokens)

    computed = get_tick_at_sqrt_ratio(sqrt_price)
    # A downward (zeroForOne) swap that ends exactly on a tick boundary stores tick = boundary - 1
    # with sqrtPriceX96 = ratio(boundary), while getTickAtSqrtRatio returns the boundary itself.
    on_boundary = computed == tick + 1 and get_sqrt_ratio_at_tick(computed) == sqrt_price
    verdict = "match" if computed == tick else "boundary case" if on_boundary else "MISMATCH"
    price = sqrtx96_to_price(sqrt_price, dec0, dec1)

    print(f"pool           {a.pool}")
    print(f"tokens         {sym0} / {sym1} ({dec0} / {dec1} decimals)")
    print(f"sqrtPriceX96   {sqrt_price}")
    print(f"slot0 tick     {tick}")
    print(f"computed tick  {computed}  ({verdict})")
    print(f"price          {price:.8g} {sym1} per {sym0}  ({1 / price:.8g} {sym0} per {sym1})")
    return 0 if verdict != "MISMATCH" else 1


if __name__ == "__main__":
    sys.exit(main())
