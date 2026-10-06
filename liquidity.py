"""Token amounts <-> liquidity for a Uniswap v3 position: a port of LiquidityAmounts.sol.

Inputs and outputs are raw integers (sqrt prices as Q64.96, amounts in the token's smallest
unit) and every division rounds down, like the Solidity library. The pool itself rounds the
amounts owed up when minting, so a mint can take one unit more than these functions report.
"""
import argparse

from tickmath import get_sqrt_ratio_at_tick

Q96 = 1 << 96


def _sorted(a: int, b: int):
    return (a, b) if a <= b else (b, a)


def _uint128(value: int) -> int:
    if value >= 1 << 128:
        raise OverflowError("liquidity does not fit in uint128")
    return value


def get_amount0_for_liquidity(sqrt_a: int, sqrt_b: int, liquidity: int) -> int:
    sqrt_a, sqrt_b = _sorted(sqrt_a, sqrt_b)
    return ((liquidity << 96) * (sqrt_b - sqrt_a) // sqrt_b) // sqrt_a


def get_amount1_for_liquidity(sqrt_a: int, sqrt_b: int, liquidity: int) -> int:
    sqrt_a, sqrt_b = _sorted(sqrt_a, sqrt_b)
    return liquidity * (sqrt_b - sqrt_a) // Q96


def get_amounts_for_liquidity(sqrt_price: int, sqrt_a: int, sqrt_b: int, liquidity: int):
    """(amount0, amount1) held by `liquidity` in the range [sqrt_a, sqrt_b] at `sqrt_price`."""
    sqrt_a, sqrt_b = _sorted(sqrt_a, sqrt_b)
    if sqrt_price <= sqrt_a:
        return get_amount0_for_liquidity(sqrt_a, sqrt_b, liquidity), 0
    if sqrt_price < sqrt_b:
        return (get_amount0_for_liquidity(sqrt_price, sqrt_b, liquidity),
                get_amount1_for_liquidity(sqrt_a, sqrt_price, liquidity))
    return 0, get_amount1_for_liquidity(sqrt_a, sqrt_b, liquidity)


def get_liquidity_for_amount0(sqrt_a: int, sqrt_b: int, amount0: int) -> int:
    sqrt_a, sqrt_b = _sorted(sqrt_a, sqrt_b)
    intermediate = sqrt_a * sqrt_b // Q96
    return _uint128(amount0 * intermediate // (sqrt_b - sqrt_a))


def get_liquidity_for_amount1(sqrt_a: int, sqrt_b: int, amount1: int) -> int:
    sqrt_a, sqrt_b = _sorted(sqrt_a, sqrt_b)
    return _uint128(amount1 * Q96 // (sqrt_b - sqrt_a))


def get_liquidity_for_amounts(sqrt_price: int, sqrt_a: int, sqrt_b: int, amount0: int, amount1: int) -> int:
    """Largest liquidity the amounts can fund in the range at `sqrt_price`."""
    sqrt_a, sqrt_b = _sorted(sqrt_a, sqrt_b)
    if sqrt_price <= sqrt_a:
        return get_liquidity_for_amount0(sqrt_a, sqrt_b, amount0)
    if sqrt_price < sqrt_b:
        return min(get_liquidity_for_amount0(sqrt_price, sqrt_b, amount0),
                   get_liquidity_for_amount1(sqrt_a, sqrt_price, amount1))
    return get_liquidity_for_amount1(sqrt_a, sqrt_b, amount1)


def main():
    ap = argparse.ArgumentParser(description="Uniswap v3 position: token amounts <-> liquidity")
    price = ap.add_mutually_exclusive_group(required=True)
    price.add_argument("--tick", type=int, help="current pool tick")
    price.add_argument("--sqrt-price", type=int, help="current sqrtPriceX96")
    ap.add_argument("--lower", type=int, required=True, help="lower tick of the position")
    ap.add_argument("--upper", type=int, required=True, help="upper tick of the position")
    ap.add_argument("--liquidity", type=int, help="liquidity -> token amounts")
    ap.add_argument("--amount0", type=int, default=0, help="raw token0 amount -> liquidity")
    ap.add_argument("--amount1", type=int, default=0, help="raw token1 amount -> liquidity")
    a = ap.parse_args()

    sqrt_price = a.sqrt_price if a.sqrt_price is not None else get_sqrt_ratio_at_tick(a.tick)
    sqrt_a, sqrt_b = get_sqrt_ratio_at_tick(a.lower), get_sqrt_ratio_at_tick(a.upper)
    liquidity = a.liquidity
    if liquidity is None:
        liquidity = get_liquidity_for_amounts(sqrt_price, sqrt_a, sqrt_b, a.amount0, a.amount1)
        print(f"liquidity {liquidity}")
    amount0, amount1 = get_amounts_for_liquidity(sqrt_price, sqrt_a, sqrt_b, liquidity)
    print(f"amount0   {amount0}\namount1   {amount1}")


if __name__ == "__main__":
    main()
