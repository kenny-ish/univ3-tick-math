# Changelog

All notable changes to this project are documented in this file.

## Unreleased

- `get_sqrt_ratio_at_tick` / `get_tick_at_sqrt_ratio`: exact integer ports of `TickMath.sol`, plus `MIN_SQRT_RATIO` / `MAX_SQRT_RATIO`
- CLI: `tick2sqrt` and `sqrt2tick`
- Fixed: `price_to_tick(tick_to_price(t))` returned `t - 1` for about a third of ticks
- Prices given on the command line are parsed as exact decimals instead of through `float`

## 0.1.0 - 2026-09-24

- Conversions between ticks, sqrtPriceX96 and human prices with token decimals
- `nearest_usable` snaps a tick to a fee tier's tick spacing
- Installable with pip from GitHub; `univ3-tick` console script
