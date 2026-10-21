import json
import subprocess
import sys
import unittest
from pathlib import Path

from tickmath import price_to_tick

SCRIPT = str(Path(__file__).with_name("tickmath.py"))


def run_json(*args):
    out = subprocess.run([sys.executable, SCRIPT, *args, "--json"], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


class CliJsonTest(unittest.TestCase):
    def test_tick_to_price(self):
        self.assertEqual(run_json("tick2price", "0"), {"tick": 0, "price": "1", "inverse": "1"})

    def test_price_to_tick_with_fee_tier(self):
        out = run_json("price2tick", "2650", "--dec0", "18", "--dec1", "6", "--fee", "3000")
        self.assertEqual(out["tick"], price_to_tick("2650", 18, 6))
        self.assertEqual(out["usable_tick"] % 60, 0)

    def test_big_integers_are_strings(self):
        self.assertEqual(run_json("tick2sqrt", "887272"),
                         {"tick": 887272, "sqrt_price_x96": "1461446703485210103287273052203988822378723970342"})
        self.assertEqual(run_json("sqrt2tick", "79228162514264337593543950336")["tick"], 0)


if __name__ == "__main__":
    unittest.main()
