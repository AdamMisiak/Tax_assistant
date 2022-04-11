from unittest import TestCase
import dividends

class TestDividends(TestCase):
    def test_open_csv_file(self):
        rows = dividends.open_csv_file()
        self.assertTrue(isinstance(rows, list))
        self.assertEqual(rows[0][0], 'USD')
