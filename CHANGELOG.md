# Changelog

All notable changes to this project are documented in this file.

## Unreleased

- `get_sqrt_ratio_at_tick` / `get_tick_at_sqrt_ratio`: exact integer ports of `TickMath.sol`, plus `MIN_SQRT_RATIO` / `MAX_SQRT_RATIO`
- CLI: `tick2sqrt` and `sqrt2tick`
- Fixed: `price_to_tick(tick_to_price(t))` returned `t - 1` for about a third of ticks
- Prices given on the command line are parsed as exact decimals instead of through `float`
- Fixed: `nearest_usable` rounds halves up like the Uniswap SDK and never leaves the usable tick range
- `nearest_usable(tick, spacing=...)` for tick spacings outside the standard fee tiers, and `usable_tick_range(spacing)`
- CLI: `--spacing`
- `liquidity` module: port of `LiquidityAmounts.sol` (token amounts for liquidity and liquidity for amounts, same integer rounding)
- `univ3-liquidity` console script
- `examples/check_live_pool.py`: reads `slot0()` of a live pool over JSON-RPC and checks it against `get_tick_at_sqrt_ratio`

## 0.1.0 - 2026-09-24

- Conversions between ticks, sqrtPriceX96 and human prices with token decimals
- `nearest_usable` snaps a tick to a fee tier's tick spacing
- Installable with pip from GitHub; `univ3-tick` console script
