import unittest

from src.utils import format_currency, format_date, safe_get, safe_json_loads


class TestUtils(unittest.TestCase):
    def test_format_date_old_format(self):
        self.assertEqual(format_date("2026-05-15"), "May 15, 2026")

    def test_format_date_new_format(self):
        # We need to make sure format_date works with the new T00:00:00 format
        self.assertEqual(format_date("2026-05-15T00:00:00"), "May 15, 2026")

    def test_format_date_invalid(self):
        self.assertEqual(format_date("invalid-date"), "invalid-date")

    def test_format_currency(self):
        self.assertEqual(format_currency(45.5), "$45.50")
        self.assertEqual(format_currency(45), "$45.00")

    def test_safe_get(self):
        data = {"a": {"b": {"c": 1}}}
        self.assertEqual(safe_get(data, "a", "b", "c"), 1)
        self.assertEqual(safe_get(data, "a", "x", "c", default=2), 2)

    def test_safe_json_loads(self):
        self.assertEqual(safe_json_loads('{"a": 1}'), {"a": 1})
        self.assertEqual(safe_json_loads("invalid", default={"b": 2}), {"b": 2})


if __name__ == "__main__":
    unittest.main()
