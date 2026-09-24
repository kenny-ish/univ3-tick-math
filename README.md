# univ3-tick-math

Uniswap v3 keeps a pool's price in three different forms. This library converts between them,
with token decimals handled for you:

| form | definition | where you meet it |
|---|---|---|
| tick | `price = 1.0001 ^ tick` | position bounds, `slot0().tick` |
| sqrtPriceX96 | `sqrt(price) * 2^96` (Q64.96 fixed point) | `slot0().sqrtPriceX96`, swap price limits |
| human price | raw price `* 10^(decimals0 - decimals1)` | UIs, logs, strategy code |

Prices are always **token1 per token0**, the order the pool stores its tokens (token0 is the
token with the lower address).

## Install

```bash
pip install git+https://github.com/kenny-ish/univ3-tick-math
```

Python 3.10+, no dependencies.

## Command line

```bash
$ univ3-tick tick2price 197480 --dec0 6 --dec1 18
price 0.0003767199631  (inverse 2654.491660)
$ univ3-tick price2tick 2650 --dec0 18 --dec1 6 --fee 3000
tick -197497
nearest usable tick for fee 3000: -197520 -> price 2643.895430
$ univ3-tick price2sqrt 1
sqrtPriceX96 79228162514264337593543950336
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

`nearest_usable(tick, fee)` snaps a tick to the fee tier's tick spacing (100 -> 1, 500 -> 10,
3000 -> 60, 10000 -> 200); positions can only be minted on those ticks.

## Precision

Everything runs on `decimal.Decimal` with 80 significant digits, so even the largest
sqrtPriceX96 values convert without float rounding. Pass prices as `str`, `int` or `Decimal`
when exactness matters; a Python `float` only carries about 17 significant digits.

If a price looks upside down (0.000377 instead of 2654), the pair is the other way round;
invert it.

## Development

```bash
python -m unittest -v
```

Release notes are in [CHANGELOG.md](CHANGELOG.md).
