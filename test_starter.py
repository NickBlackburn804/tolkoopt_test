import unittest
from decimal import Decimal

from starter import recommend_price


class TestRecommendPrice(unittest.IsolatedAsyncioTestCase):
    async def test_normal_calculation(self):
        async def fetch_offers():
            return {
                "status": "success",
                "offers": [
                    {
                        "seller": "MYSHOP",
                        "price": Decimal("4300.00"),
                        "delivery_days": 2,
                    },
                    {
                        "seller": "PARTS",
                        "price": Decimal("4800.00"),
                        "delivery_days": 3,
                    },
                    {
                        "seller": "SLOW",
                        "price": Decimal("4700.00"),
                        "delivery_days": 8,
                    },
                ],
            }

        result = await recommend_price(
            fetch_offers,
            current_price=Decimal("4900.00"),
            min_price=Decimal("4500.00"),
        )

        self.assertEqual(result["price"], Decimal("4728.00"))
        self.assertEqual(result["decision"], "APPLY")

    async def test_no_eligible_offers(self):
        async def fetch_offers():
            return {
                "status": "success",
                "offers": [
                    {
                        "seller": "MYSHOP",
                        "price": Decimal("4000.00"),
                        "delivery_days": 2,
                    },
                    {
                        "seller": "PARTS",
                        "price": Decimal("4200.00"),
                        "delivery_days": 8,
                    },
                    {
                        "seller": "OTHER",
                        "price": Decimal("4100.00"),
                        "delivery_days": None,
                    },
                ],
            }

        result = await recommend_price(
            fetch_offers,
            current_price=Decimal("4400.00"),
            min_price=Decimal("4500.00"),
        )

        self.assertEqual(result["price"], Decimal("4400.00"))
        self.assertEqual(result["decision"], "HOLD")


if __name__ == "__main__":
    unittest.main()
