import unittest

from tickmath import (MAX_SQRT_RATIO, MAX_TICK, MIN_SQRT_RATIO, MIN_TICK,
                      get_sqrt_ratio_at_tick, get_tick_at_sqrt_ratio)


class FullRangeTest(unittest.TestCase):
    """Every 997th tick from MIN_TICK to MAX_TICK, about 1,800 ticks."""

    def test_round_trip_and_boundaries(self):
        previous = MIN_SQRT_RATIO - 1
        for tick in range(MIN_TICK, MAX_TICK, 997):
            ratio = get_sqrt_ratio_at_tick(tick)
            next_ratio = get_sqrt_ratio_at_tick(tick + 1)
            self.assertGreater(ratio, previous)
            self.assertEqual(get_tick_at_sqrt_ratio(ratio), tick)
            self.assertEqual(get_tick_at_sqrt_ratio(next_ratio - 1), tick)
            if tick > MIN_TICK:
                self.assertEqual(get_tick_at_sqrt_ratio(ratio - 1), tick - 1)
            previous = ratio

    def test_neighbouring_ratios_differ_by_sqrt_one_bip(self):
        for tick in range(-800000, 800000, 99991):
            low, high = get_sqrt_ratio_at_tick(tick), get_sqrt_ratio_at_tick(tick + 1)
            self.assertAlmostEqual(high / low, 1.0001 ** 0.5, delta=1e-9)

    def test_top_of_the_range(self):
        self.assertEqual(get_sqrt_ratio_at_tick(MAX_TICK), MAX_SQRT_RATIO)
        self.assertEqual(get_tick_at_sqrt_ratio(get_sqrt_ratio_at_tick(MAX_TICK - 1)), MAX_TICK - 1)


if __name__ == "__main__":
    unittest.main()
