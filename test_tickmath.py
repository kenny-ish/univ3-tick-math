import unittest
from decimal import Decimal

from tickmath import (MAX_TICK, MIN_TICK, Q96, nearest_usable, price_to_sqrtx96,
                      price_to_tick, sqrtx96_to_price, tick_to_price, usable_tick_range)


class TickMathTest(unittest.TestCase):
    def test_tick_zero_is_price_one(self):
        self.assertEqual(tick_to_price(0), 1)
        self.assertEqual(price_to_tick(1), 0)

    def test_round_trip_is_exact(self):
        for tick in range(MIN_TICK, MAX_TICK + 1, 3001):
            self.assertEqual(price_to_tick(tick_to_price(tick)), tick)
        for tick in (-50000, -1, 1, 12345, 200000):
            self.assertEqual(price_to_tick(tick_to_price(tick, 6, 18), 6, 18), tick)

    def test_price_between_ticks_floors(self):
        p = tick_to_price(100)
        self.assertEqual(price_to_tick(p * Decimal("1.00005")), 100)
        self.assertEqual(price_to_tick(p - Decimal("1e-60")), 99)

    def test_out_of_range_prices_clamp(self):
        self.assertEqual(price_to_tick("1e-50"), MIN_TICK)
        self.assertEqual(price_to_tick("1e50"), MAX_TICK)
        with self.assertRaises(ValueError):
            price_to_tick(0)

    def test_sqrt_price_of_one(self):
        self.assertEqual(price_to_sqrtx96(1), int(Q96))
        self.assertEqual(sqrtx96_to_price(int(Q96)), 1)

    def test_decimals_shift(self):
        # WETH (18 decimals) as token0, USDC (6) as token1: 3500 USDC per WETH
        tick = price_to_tick(3500, dec0=18, dec1=6)
        self.assertLessEqual(tick_to_price(tick, 18, 6), 3500)
        self.assertGreater(tick_to_price(tick + 1, 18, 6), 3500)


class NearestUsableTest(unittest.TestCase):
    def test_snaps_to_the_fee_tier_spacing(self):
        self.assertEqual(nearest_usable(12345, 3000), 12360)
        self.assertEqual(nearest_usable(-12345, 500), -12340)

    def test_halves_round_up_like_the_sdk(self):
        self.assertEqual(nearest_usable(30, 3000), 60)
        self.assertEqual(nearest_usable(-30, 3000), 0)
        self.assertEqual(nearest_usable(-31, 3000), -60)

    def test_stays_inside_the_tick_range(self):
        self.assertEqual(usable_tick_range(60), (-887220, 887220))
        self.assertEqual(nearest_usable(MAX_TICK, 3000), 887220)
        self.assertEqual(nearest_usable(MIN_TICK, 3000), -887220)
        self.assertEqual(nearest_usable(MAX_TICK, 10000), 887200)

    def test_custom_tick_spacing(self):
        self.assertEqual(nearest_usable(1234, spacing=50), 1250)
        with self.assertRaises(ValueError):
            nearest_usable(0, spacing=0)


if __name__ == "__main__":
    unittest.main()
