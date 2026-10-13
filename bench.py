"""Micro-benchmarks for the functions that sit in hot loops.

  python bench.py
"""
import random
import timeit

from tickmath import (MAX_TICK, MIN_TICK, get_sqrt_ratio_at_tick, get_tick_at_sqrt_ratio,
                      price_to_tick, tick_to_price)

random.seed(7)
TICKS = [random.randint(MIN_TICK, MAX_TICK - 1) for _ in range(2000)]
RATIOS = [get_sqrt_ratio_at_tick(t) + 1 for t in TICKS]
PRICES = [tick_to_price(t) for t in TICKS[:200]]

CASES = [
    ("get_sqrt_ratio_at_tick", lambda: [get_sqrt_ratio_at_tick(t) for t in TICKS], len(TICKS)),
    ("get_tick_at_sqrt_ratio", lambda: [get_tick_at_sqrt_ratio(r) for r in RATIOS], len(RATIOS)),
    ("tick_to_price", lambda: [tick_to_price(t) for t in TICKS[:200]], 200),
    ("price_to_tick", lambda: [price_to_tick(p) for p in PRICES], len(PRICES)),
]

if __name__ == "__main__":
    for name, fn, n in CASES:
        best = min(timeit.repeat(fn, number=1, repeat=5)) / n
        print(f"{name:<24} {best * 1e6:8.2f} us/call")
