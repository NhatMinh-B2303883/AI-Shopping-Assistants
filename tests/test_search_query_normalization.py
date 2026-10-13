"""Quick unit tests for deterministic query normalization.

Run inside the backend container with:
  python -m unittest discover -s tests -p 'test_search_query_normalization.py'
Or copy this file to a suitable test folder and run it with Python.
"""
import unittest

from ai.search.query_normalization import normalize_search_query


class QueryNormalizationTests(unittest.TestCase):
    def test_english_hoodie_and_color(self):
        result = normalize_search_query("black hoodie")
        self.assertEqual(result["category"], "Sweatshirt")
        self.assertEqual(result["color"], "Black")
        self.assertIn("sweatshirt", result["normalized_query"].lower())
        self.assertIn("black", result["normalized_query"].lower())

    def test_vietnamese_hoodie_and_color(self):
        result = normalize_search_query("áo hoodie đen")
        self.assertEqual(result["category"], "Sweatshirt")
        self.assertEqual(result["color"], "Black")
        self.assertEqual(result["normalized_query"], "sweatshirt black")

    def test_vietnamese_tshirt_and_white(self):
        result = normalize_search_query("áo thun trắng")
        self.assertEqual(result["category"], "T-Shirt")
        self.assertEqual(result["color"], "White")

    def test_running_shoes(self):
        result = normalize_search_query("giày chạy bộ màu đen")
        self.assertEqual(result["category"], "Sports Shoes")
        self.assertEqual(result["color"], "Black")

    def test_mixed_types_do_not_force_one_category(self):
        result = normalize_search_query("black hoodie and white t-shirt")
        self.assertIsNone(result["category"])
        self.assertIsNone(result["color"])

    def test_known_out_of_scope_type(self):
        result = normalize_search_query("blue jeans")
        self.assertEqual(result["unsupported_type"], "jeans")

    def test_supported_type_takes_precedence_over_out_of_scope_context(self):
        result = normalize_search_query("black jacket to wear with jeans")
        self.assertEqual(result["category"], "Jacket")
        self.assertIsNone(result["unsupported_type"])


if __name__ == "__main__":
    unittest.main()
