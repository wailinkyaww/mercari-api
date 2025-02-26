import unittest
from ..url import construct_products_search_url


class TestConstructMercariProductSearchUrl(unittest.TestCase):

    def test_full_parameters(self):
        params = {
            "search_keyword": "leather shorts",
            "item_origin": "Japan",
            "condition": "like new",
            "price_min": 1000,
            "price_max": 5000,
            "free_shipping": True
        }
        expected_url = "https://www.mercari.com/search/?keyword=leather%20shorts&countrySources=2&itemConditions=2&minPrice=1000&maxPrice=5000&shippingPayerIds=2"
        self.assertEqual(construct_products_search_url(params), expected_url)

    def test_minimal_parameters(self):
        params = {
            "search_keyword": "wallet"
        }
        expected_url = "https://www.mercari.com/search/?keyword=wallet"
        self.assertEqual(construct_products_search_url(params), expected_url)

    def test_no_condition(self):
        params = {
            "search_keyword": "jacket",
            "item_origin": "USA",
            "price_min": 200
        }
        expected_url = "https://www.mercari.com/search/?keyword=jacket&countrySources=1&minPrice=200"
        self.assertEqual(construct_products_search_url(params), expected_url)

    def test_no_origin(self):
        params = {
            "search_keyword": "shoes",
            "condition": "good",
            "price_max": 3000
        }
        expected_url = "https://www.mercari.com/search/?keyword=shoes&itemConditions=3&maxPrice=3000"
        self.assertEqual(construct_products_search_url(params), expected_url)

    def test_free_shipping_only(self):
        params = {
            "search_keyword": "hat",
            "free_shipping": True
        }
        expected_url = "https://www.mercari.com/search/?keyword=hat&shippingPayerIds=2"
        self.assertEqual(construct_products_search_url(params), expected_url)

    def test_invalid_condition(self):
        params = {
            "search_keyword": "watch",
            "condition": "excellent"
        }

        # should ignore the invalid condition
        expected_url = "https://www.mercari.com/search/?keyword=watch"
        self.assertEqual(construct_products_search_url(params), expected_url)

    def test_empty_params(self):
        params = {}
        expected_url = "https://www.mercari.com/search/?"
        self.assertEqual(construct_products_search_url(params), expected_url)


if __name__ == "__main__":
    unittest.main()
