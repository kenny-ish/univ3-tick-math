import unittest
from decimal import Decimal

from tickmath import (MAX_SQRT_RATIO, MAX_TICK, MIN_SQRT_RATIO, MIN_TICK,
                      get_sqrt_ratio_at_tick, get_tick_at_sqrt_ratio)


class GetSqrtRatioAtTickTest(unittest.TestCase):
    def test_matches_the_constants_in_tickmath_sol(self):
        self.assertEqual(get_sqrt_ratio_at_tick(MIN_TICK), MIN_SQRT_RATIO)
        self.assertEqual(get_sqrt_ratio_at_tick(MAX_TICK), MAX_SQRT_RATIO)
        self.assertEqual(get_sqrt_ratio_at_tick(0), 2 ** 96)

    def test_rejects_ticks_outside_the_range(self):
        for tick in (MIN_TICK - 1, MAX_TICK + 1):
            with self.assertRaises(ValueError):
                get_sqrt_ratio_at_tick(tick)

    def test_close_to_the_real_value(self):
        for tick in (-887272, -400000, -60, -1, 1, 60, 400000, 887272):
            exact = Decimal("1.0001").sqrt() ** tick * Decimal(2) ** 96
            error = abs(Decimal(get_sqrt_ratio_at_tick(tick)) - exact)
            # one unit of the Q64.96 result, plus the library's own relative error, which grows to
            # ~3e-20 near MAX_TICK where the Q128.128 intermediate keeps only ~64 significant bits
            self.assertLessEqual(error, 1 + exact * Decimal("1e-18"), tick)

    def test_strictly_increasing(self):
        ratios = [get_sqrt_ratio_at_tick(t) for t in range(MIN_TICK, MAX_TICK + 1, 9973)]
        self.assertEqual(ratios, sorted(set(ratios)))


class GetTickAtSqrtRatioTest(unittest.TestCase):
    def test_bounds_from_tickmath_sol(self):
        self.assertEqual(get_tick_at_sqrt_ratio(MIN_SQRT_RATIO), MIN_TICK)
        self.assertEqual(get_tick_at_sqrt_ratio(MIN_SQRT_RATIO + 1), MIN_TICK)
        self.assertEqual(get_tick_at_sqrt_ratio(MAX_SQRT_RATIO - 1), MAX_TICK - 1)

    def test_rejects_prices_outside_the_range(self):
        for value in (MIN_SQRT_RATIO - 1, MAX_SQRT_RATIO):
            with self.assertRaises(ValueError):
                get_tick_at_sqrt_ratio(value)

    def test_inverse_at_and_just_below_each_tick(self):
        for tick in (-887271, -200000, -1, 0, 1, 12345, 887271):
            ratio = get_sqrt_ratio_at_tick(tick)
            self.assertEqual(get_tick_at_sqrt_ratio(ratio), tick)
            self.assertEqual(get_tick_at_sqrt_ratio(ratio - 1), tick - 1)


if __name__ == "__main__":
    unittest.main()
