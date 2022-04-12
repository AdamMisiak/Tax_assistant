from unittest import TestCase
import dividends

class TestDividends(TestCase):
    def test_get_summary_dividends_tax(self):
        tax_to_paid = dividends.get_summary_dividends_tax()
        self.assertTrue(isinstance(tax_to_paid, float))

    def test_open_csv_file(self):
        rows = dividends.open_csv_file()
        self.assertTrue(isinstance(rows, list))
        self.assertEqual(rows[0][0], 'USD')

    def test_get_relevant_data_from_report(self):
        report = dividends.open_csv_file()
        dividends_report, taxes_report = dividends.get_relevant_data_from_report(report)
        self.assertTrue(isinstance(dividends_report, list))
        self.assertTrue(isinstance(taxes_report, list))
        # TODO Add more tests for content of reports


