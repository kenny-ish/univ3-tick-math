# univ3-tick-math

Convert between the three ways Uniswap v3 expresses price:

- **tick**: `price = 1.0001 ^ tick`
- **sqrtPriceX96**: `sqrt(price) * 2^96`, what `slot0()` returns
- **human price**: adjusted for token decimals (`raw * 10^(decimals0 - decimals1)`)

```bash
python tickmath.py tick2price 200000 --dec0 6 --dec1 18
python tickmath.py price2tick 3500 --dec0 18 --dec1 6 --fee 3000
python tickmath.py sqrt2price 1461446703485210103287273052203988822378723970342 --dec0 18 --dec1 18
python tickmath.py price2sqrt 1.0
```

`--fee` snaps a tick to the nearest usable tick for that fee tier
(100 -> 1, 500 -> 10, 3000 -> 60, 10000 -> 200), which is what you need when choosing
position bounds.

Prices are always "token1 per token0", the order the pool stores. If the result looks
upside down (e.g. 0.000285 instead of 3500) your pair is the other way round; invert it.

Uses `decimal` with 80 digits of precision so large sqrtPriceX96 values round-trip exactly
enough for display.

## Tests

```bash
python -m unittest -v
```
