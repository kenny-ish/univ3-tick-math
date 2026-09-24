"""Uniswap v3 tick / price / sqrtPriceX96 conversions."""
import argparse
import math
from decimal import Decimal, getcontext

getcontext().prec = 80
Q96 = Decimal(2) ** 96
BASE = Decimal("1.0001")
TICK_SPACING = {100: 1, 500: 10, 3000: 60, 10000: 200}
MIN_TICK, MAX_TICK = -887272, 887272


def tick_to_price(tick: int, dec0=0, dec1=0) -> Decimal:
    return BASE ** tick * Decimal(10) ** (dec0 - dec1)


def price_to_tick(price: float, dec0=0, dec1=0) -> int:
    raw = Decimal(str(price)) / Decimal(10) ** (dec0 - dec1)
    tick = math.floor(raw.ln() / BASE.ln())
    return max(MIN_TICK, min(MAX_TICK, tick))


def sqrtx96_to_price(sqrt_price_x96: int, dec0=0, dec1=0) -> Decimal:
    return (Decimal(sqrt_price_x96) / Q96) ** 2 * Decimal(10) ** (dec0 - dec1)


def price_to_sqrtx96(price: float, dec0=0, dec1=0) -> int:
    raw = Decimal(str(price)) / Decimal(10) ** (dec0 - dec1)
    return int(raw.sqrt() * Q96)


def nearest_usable(tick: int, fee: int) -> int:
    spacing = TICK_SPACING[fee]
    return round(tick / spacing) * spacing


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["tick2price", "price2tick", "sqrt2price", "price2sqrt"])
    ap.add_argument("value")
    ap.add_argument("--dec0", type=int, default=0, help="decimals of token0")
    ap.add_argument("--dec1", type=int, default=0, help="decimals of token1")
    ap.add_argument("--fee", type=int, choices=sorted(TICK_SPACING), help="fee tier for tick snapping")
    a = ap.parse_args()

    if a.cmd == "tick2price":
        p = tick_to_price(int(a.value), a.dec0, a.dec1)
        print(f"price {p:.10g}  (inverse {1 / p:.10g})")
    elif a.cmd == "price2tick":
        t = price_to_tick(float(a.value), a.dec0, a.dec1)
        print(f"tick {t}")
        if a.fee:
            u = nearest_usable(t, a.fee)
            print(f"nearest usable tick for fee {a.fee}: {u} -> price {tick_to_price(u, a.dec0, a.dec1):.10g}")
    elif a.cmd == "sqrt2price":
        p = sqrtx96_to_price(int(a.value), a.dec0, a.dec1)
        print(f"price {p:.10g}  (inverse {1 / p:.10g})")
    else:
        print(f"sqrtPriceX96 {price_to_sqrtx96(float(a.value), a.dec0, a.dec1)}")


if __name__ == "__main__":
    main()
