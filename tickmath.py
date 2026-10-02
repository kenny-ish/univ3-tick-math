"""Uniswap v3 tick / price / sqrtPriceX96 conversions.

get_sqrt_ratio_at_tick and get_tick_at_sqrt_ratio are exact integer ports of TickMath.sol.
The Decimal helpers convert to and from human prices with token decimals.
"""
import argparse
from decimal import ROUND_FLOOR, Decimal, getcontext

getcontext().prec = 80
Q96 = Decimal(2) ** 96
BASE = Decimal("1.0001")
TICK_SPACING = {100: 1, 500: 10, 3000: 60, 10000: 200}
MIN_TICK, MAX_TICK = -887272, 887272
MIN_SQRT_RATIO = 4295128739
MAX_SQRT_RATIO = 1461446703485210103287273052203988822378723970342

# 2^128 / sqrt(1.0001)^(2^i) for i = 0..19, rounded: the constants hard-coded in TickMath.sol
_RATIOS = (
    0xfffcb933bd6fad37aa2d162d1a594001, 0xfff97272373d413259a46990580e213a,
    0xfff2e50f5f656932ef12357cf3c7fdcc, 0xffe5caca7e10e4e61c3624eaa0941cd0,
    0xffcb9843d60f6159c9db58835c926644, 0xff973b41fa98c081472e6896dfb254c0,
    0xff2ea16466c96a3843ec78b326b52861, 0xfe5dee046a99a2a811c461f1969c3053,
    0xfcbe86c7900a88aedcffc83b479aa3a4, 0xf987a7253ac413176f2b074cf7815e54,
    0xf3392b0822b70005940c7a398e4b70f3, 0xe7159475a2c29b7443b29c7fa6e889d9,
    0xd097f3bdfd2022b8845ad8f792aa5825, 0xa9f746462d870fdf8a65dc1f90e061e5,
    0x70d869a156d2a1b890bb3df62baf32f7, 0x31be135f97d08fd981231505542fcfa6,
    0x9aa508b5b7a84e1c677de54f3e99bc9, 0x5d6af8dedb81196699c329225ee604,
    0x2216e584f5fa1ea926041bedfe98, 0x48a170391f7dc42444e8fa2,
)
_MAX_UINT256 = (1 << 256) - 1


def get_sqrt_ratio_at_tick(tick: int) -> int:
    """sqrt(1.0001^tick) * 2^96 as a Q64.96 integer, exactly like TickMath.getSqrtRatioAtTick."""
    if not MIN_TICK <= tick <= MAX_TICK:
        raise ValueError(f"tick {tick} outside [{MIN_TICK}, {MAX_TICK}]")
    abs_tick = abs(tick)
    ratio = _RATIOS[0] if abs_tick & 1 else 1 << 128
    for i in range(1, 20):
        if abs_tick & (1 << i):
            ratio = (ratio * _RATIOS[i]) >> 128
    if tick > 0:
        ratio = _MAX_UINT256 // ratio
    return (ratio >> 32) + (1 if ratio & 0xFFFFFFFF else 0)  # Q128.128 -> Q64.96, rounding up


def get_tick_at_sqrt_ratio(sqrt_price_x96: int) -> int:
    """Greatest tick whose sqrt ratio is <= sqrt_price_x96, like TickMath.getTickAtSqrtRatio."""
    if not MIN_SQRT_RATIO <= sqrt_price_x96 < MAX_SQRT_RATIO:
        raise ValueError(f"sqrtPriceX96 {sqrt_price_x96} outside [MIN_SQRT_RATIO, MAX_SQRT_RATIO)")
    lo, hi = MIN_TICK, MAX_TICK  # ratio(lo) <= sqrt_price_x96 < ratio(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if get_sqrt_ratio_at_tick(mid) <= sqrt_price_x96:
            lo = mid
        else:
            hi = mid
    return lo


def _raw(price, dec0, dec1) -> Decimal:
    """Human price (token1 per token0) -> raw price in the tokens' smallest units."""
    return Decimal(str(price)) / Decimal(10) ** (dec0 - dec1)


def tick_to_price(tick: int, dec0=0, dec1=0) -> Decimal:
    return BASE ** tick * Decimal(10) ** (dec0 - dec1)


def price_to_tick(price, dec0=0, dec1=0) -> int:
    """Greatest tick whose price is <= price, clamped to [MIN_TICK, MAX_TICK].

    Round-trips exactly with tick_to_price. Pass str, int or Decimal for exact input;
    a float carries only about 17 significant digits.
    """
    raw = _raw(price, dec0, dec1)
    if raw <= 0:
        raise ValueError("price must be positive")
    tick = int((raw.ln() / BASE.ln()).to_integral_value(rounding=ROUND_FLOOR))
    # ln() is only accurate to the context precision: settle the boundary with the same power
    # tick_to_price uses, so that price_to_tick(tick_to_price(t)) == t
    while BASE ** (tick + 1) <= raw:
        tick += 1
    while BASE ** tick > raw:
        tick -= 1
    return max(MIN_TICK, min(MAX_TICK, tick))


def sqrtx96_to_price(sqrt_price_x96: int, dec0=0, dec1=0) -> Decimal:
    return (Decimal(sqrt_price_x96) / Q96) ** 2 * Decimal(10) ** (dec0 - dec1)


def price_to_sqrtx96(price, dec0=0, dec1=0) -> int:
    return int(_raw(price, dec0, dec1).sqrt() * Q96)


def usable_tick_range(spacing: int) -> tuple:
    """Lowest and highest ticks a position can use with this tick spacing."""
    return -(MAX_TICK // spacing) * spacing, (MAX_TICK // spacing) * spacing


def nearest_usable(tick: int, fee: int = None, spacing: int = None) -> int:
    """Nearest tick a position can use: a multiple of the tick spacing inside the tick range.

    Halves round up, like nearestUsableTick in the Uniswap v3 SDK. Give either a fee tier
    (100, 500, 3000, 10000) or an explicit tick spacing, e.g. 50 for PancakeSwap v3's 0.25% tier.
    """
    if spacing is None:
        spacing = TICK_SPACING[fee]
    if spacing <= 0:
        raise ValueError("tick spacing must be positive")
    lo, hi = usable_tick_range(spacing)
    rounded = (tick + spacing // 2) // spacing * spacing
    return max(lo, min(hi, rounded))


def main():
    ap = argparse.ArgumentParser(description="Uniswap v3 tick / price / sqrtPriceX96 conversions")
    ap.add_argument("cmd", choices=["tick2price", "price2tick", "sqrt2price", "price2sqrt",
                                    "tick2sqrt", "sqrt2tick"])
    ap.add_argument("value")
    ap.add_argument("--dec0", type=int, default=0, help="decimals of token0")
    ap.add_argument("--dec1", type=int, default=0, help="decimals of token1")
    ap.add_argument("--fee", type=int, choices=sorted(TICK_SPACING), help="fee tier for tick snapping")
    ap.add_argument("--spacing", type=int, help="explicit tick spacing (overrides --fee)")
    a = ap.parse_args()

    if a.cmd == "tick2price":
        p = tick_to_price(int(a.value), a.dec0, a.dec1)
        print(f"price {p:.10g}  (inverse {1 / p:.10g})")
    elif a.cmd == "price2tick":
        t = price_to_tick(a.value, a.dec0, a.dec1)
        print(f"tick {t}")
        if a.fee or a.spacing:
            spacing = a.spacing or TICK_SPACING[a.fee]
            u = nearest_usable(t, spacing=spacing)
            print(f"nearest usable tick (spacing {spacing}): {u} -> price {tick_to_price(u, a.dec0, a.dec1):.10g}")
    elif a.cmd == "sqrt2price":
        p = sqrtx96_to_price(int(a.value), a.dec0, a.dec1)
        print(f"price {p:.10g}  (inverse {1 / p:.10g})")
    elif a.cmd == "price2sqrt":
        print(f"sqrtPriceX96 {price_to_sqrtx96(a.value, a.dec0, a.dec1)}")
    elif a.cmd == "tick2sqrt":
        print(f"sqrtPriceX96 {get_sqrt_ratio_at_tick(int(a.value))}")
    else:
        print(f"tick {get_tick_at_sqrt_ratio(int(a.value))}")


if __name__ == "__main__":
    main()
