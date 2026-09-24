import unittest

from tickmath import (Q96, nearest_usable, price_to_sqrtx96, price_to_tick,
                      sqrtx96_to_price, tick_to_price)


class TickMathTest(unittest.TestCase):
    def test_tick_zero_is_price_one(self):
        self.assertEqual(tick_to_price(0), 1)
        self.assertEqual(price_to_tick(1.0), 0)

    def test_round_trip(self):
        for tick in (-50000, -1, 1, 12345, 200000):
            p = tick_to_price(tick)
            self.assertEqual(price_to_tick(float(p) * 1.00000001), tick)

    def test_sqrt_price_of_one(self):
        self.assertEqual(price_to_sqrtx96(1.0), int(Q96))
        self.assertAlmostEqual(float(sqrtx96_to_price(int(Q96))), 1.0)

    def test_decimals_shift(self):
        # USDC (6) / WETH (18): raw price 1e-12 * 3500 human
        raw_tick = price_to_tick(3500, dec0=18, dec1=6)
        self.assertAlmostEqual(float(tick_to_price(raw_tick, 18, 6)), 3500, delta=3500 * 1e-4)

    def test_usable_tick(self):
        self.assertEqual(nearest_usable(12345, 3000), 12360)
        self.assertEqual(nearest_usable(-12345, 500), -12340)


if __name__ == "__main__":
    unittest.main()
