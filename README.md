# univ3-tick-math

[![CI](https://github.com/kenny-ish/univ3-tick-math/actions/workflows/ci.yml/badge.svg)](https://github.com/kenny-ish/univ3-tick-math/actions/workflows/ci.yml)

Uniswap v3 keeps a pool's price in three different forms. This library converts between them,
including the token decimals, and computes how much of each token a position holds:

| form | definition | where you meet it |
|---|---|---|
| tick | `price = 1.0001 ^ tick` | position bounds, `slot0().tick` |
| sqrtPriceX96 | `sqrt(price) * 2^96` (Q64.96 fixed point) | `slot0().sqrtPriceX96`, swap price limits |
| human price | raw price `* 10^(decimals0 - decimals1)` | UIs, logs, strategy code |

Prices are always token1 per token0, the order the pool stores its tokens (token0 is the
token with the lower address).

## Install

```bash
pip install git+https://github.com/kenny-ish/univ3-tick-math
```

Requires Python 3.10 or newer and nothing else.

## Command line

```bash
$ univ3-tick tick2price 197480 --dec0 6 --dec1 18
price 0.0003767199631  (inverse 2654.491660)
$ univ3-tick price2tick 2650 --dec0 18 --dec1 6 --fee 3000
tick -197497
nearest usable tick (spacing 60): -197520 -> price 2643.895430
$ univ3-tick tick2sqrt -887272
sqrtPriceX96 4295128739
$ univ3-tick sqrt2tick 79228162514264337593543950336
tick 0
```

The first line is the USDC/WETH pool (USDC is token0 with 6 decimals, WETH token1 with 18): at
tick 197480 one USDC is worth 0.000377 WETH, i.e. about 2654 USDC per WETH. Without installing,
`python tickmath.py ...` does the same.

## Library

```python
from tickmath import nearest_usable, price_to_tick, sqrtx96_to_price

# USDC/WETH pools: token0 = USDC (6 decimals), token1 = WETH (18 decimals)
weth_per_usdc = sqrtx96_to_price(sqrt_price_x96, dec0=6, dec1=18)
usdc_per_weth = 1 / weth_per_usdc

# lower bound of a position that starts at 3000 USDC per WETH, on the 0.3% tier
lower = nearest_usable(price_to_tick("0.000333333", dec0=6, dec1=18), 3000)
```

`price_to_tick` returns the greatest tick whose price is <= the given price and round-trips
exactly with `tick_to_price`. `nearest_usable` snaps a tick to the tick spacing (fee tier 100 ->
1, 500 -> 10, 3000 -> 60, 10000 -> 200, or `spacing=` for other deployments), rounding halves up
like the Uniswap SDK and staying inside the usable range.

## Exact on-chain math

`get_sqrt_ratio_at_tick` and `get_tick_at_sqrt_ratio` are integer ports of Uniswap's
`TickMath.sol` and return exactly what the contract returns, including its rounding:

```python
>>> from tickmath import get_sqrt_ratio_at_tick, get_tick_at_sqrt_ratio
>>> get_sqrt_ratio_at_tick(887272)          # MAX_SQRT_RATIO
1461446703485210103287273052203988822378723970342
>>> get_tick_at_sqrt_ratio(2 ** 96)         # price 1.0
0
```

A live pool makes a good end-to-end check. `examples/check_live_pool.py` reads `slot0()` of a
mainnet pool over plain JSON-RPC and checks that the stored tick equals
`get_tick_at_sqrt_ratio(sqrtPriceX96)`:

```bash
$ python examples/check_live_pool.py
pool           0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640
tokens         USDC / WETH (6 / 18 decimals)
sqrtPriceX96   1532120860153536466420187884009850
slot0 tick     197406
computed tick  197406  (match)
price          0.00037396149 WETH per USDC  (2674.0721 USDC per WETH)
```

There is one legitimate difference. A downward swap that ends exactly on a tick boundary stores
`tick = boundary - 1` while the price equals the boundary's ratio. The script reports that as a
boundary case rather than a mismatch.

## Position amounts

`liquidity.py` ports `LiquidityAmounts.sol` from the periphery contracts: token amounts for a
given liquidity, and the liquidity that given amounts can fund, with the same integer rounding.

```bash
$ univ3-liquidity --tick 0 --lower -600 --upper 600 --liquidity 1000000000000000000
amount0   29553010879137169
amount1   29553010879137169
$ univ3-liquidity --tick 0 --lower -600 --upper 600 --amount0 1000000 --amount1 1000000
liquidity 33837499
amount0   999999
amount1   999999
```

Amounts are raw integers in each token's smallest unit. These functions round down like the
library. When minting, the pool rounds the amounts it takes up, so a mint can take one unit more.

## Precision

The `Decimal` helpers use 80 significant digits, so even the largest sqrtPriceX96 values convert
without float rounding. Pass prices as `str`, `int` or `Decimal` when exactness matters, since a
Python `float` only carries about 17 significant digits.

If a price looks upside down (0.000377 instead of 2654), the pair is the other way round,
so invert it.

## Development

```bash
python -m unittest -v
```

Release notes are in [CHANGELOG.md](CHANGELOG.md).
