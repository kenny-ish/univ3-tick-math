import unittest

from liquidity import (get_amount0_for_liquidity, get_amount1_for_liquidity,
                       get_amounts_for_liquidity, get_liquidity_for_amounts)
from tickmath import get_sqrt_ratio_at_tick

Q96 = 1 << 96
LOWER, UPPER = get_sqrt_ratio_at_tick(-600), get_sqrt_ratio_at_tick(600)


class LiquidityAmountsTest(unittest.TestCase):
    def test_known_values(self):
        # amount1 = L * (sqrtB - sqrtA) / 2^96; amount0 = L * 2^96 * (sqrtB - sqrtA) / sqrtB / sqrtA
        self.assertEqual(get_amount1_for_liquidity(Q96, 2 * Q96, 1000), 1000)
        self.assertEqual(get_amount0_for_liquidity(Q96, 2 * Q96, 1000), 500)

    def test_in_range_holds_both_tokens(self):
        amount0, amount1 = get_amounts_for_liquidity(Q96, LOWER, UPPER, 10 ** 18)
        self.assertGreater(amount0, 0)
        self.assertGreater(amount1, 0)
        # a range symmetric around price 1 holds about the same amount of each token
        self.assertAlmostEqual(amount0 / amount1, 1, delta=1e-3)

    def test_below_the_range_is_all_token0(self):
        amounts = get_amounts_for_liquidity(get_sqrt_ratio_at_tick(-1200), LOWER, UPPER, 10 ** 18)
        self.assertEqual(amounts, (get_amount0_for_liquidity(LOWER, UPPER, 10 ** 18), 0))

    def test_above_the_range_is_all_token1(self):
        amounts = get_amounts_for_liquidity(get_sqrt_ratio_at_tick(1200), LOWER, UPPER, 10 ** 18)
        self.assertEqual(amounts, (0, get_amount1_for_liquidity(LOWER, UPPER, 10 ** 18)))

    def test_round_trip_rounds_down(self):
        for liquidity in (10 ** 6, 10 ** 18, 123456789 * 10 ** 12):
            amount0, amount1 = get_amounts_for_liquidity(Q96, LOWER, UPPER, liquidity)
            back = get_liquidity_for_amounts(Q96, LOWER, UPPER, amount0, amount1)
            self.assertLessEqual(back, liquidity)
            self.assertLessEqual(liquidity - back, liquidity // 10 ** 4 + 2)

    def test_bounds_in_either_order(self):
        self.assertEqual(get_amounts_for_liquidity(Q96, UPPER, LOWER, 10 ** 18),
                         get_amounts_for_liquidity(Q96, LOWER, UPPER, 10 ** 18))

    def test_liquidity_must_fit_in_uint128(self):
        with self.assertRaises(OverflowError):
            get_liquidity_for_amounts(Q96 // 2, LOWER, UPPER, 2 ** 200, 0)


if __name__ == "__main__":
    unittest.main()
