from unittest import TestCase
import dividends
from datetime import datetime


class TestDividends(TestCase):
    def test_get_summary_dividends_tax(self):
        tax_to_paid = dividends.get_summary_dividends_tax()
        self.assertTrue(isinstance(tax_to_paid, float))

    def test_open_csv_file(self):
        rows = dividends.open_csv_file()
        self.assertTrue(isinstance(rows, list))
        self.assertEqual(rows[0][0], "USD")

    def test_get_relevant_data_from_report(self):
        report = dividends.open_csv_file()
        dividends_report, taxes_report = dividends.get_relevant_data_from_report(report)
        self.assertTrue(isinstance(dividends_report, list))
        self.assertTrue(isinstance(taxes_report, list))
        self.assertTrue(isinstance(dividends_report[0], dict))
        self.assertTrue(isinstance(dividends_report[0], dict))
        self.assertTrue(isinstance(taxes_report[0], dict))
        self.assertTrue("currency_rate_d_1" in dividends_report[0])
        self.assertTrue("currency_rate_d_1" in taxes_report[0])
        self.assertTrue("value_pln" in dividends_report[0])
        self.assertTrue("value_pln" in taxes_report[0])
        self.assertTrue(isinstance(dividends_report[0]["date"], datetime))
        self.assertTrue(isinstance(taxes_report[0]["date"], datetime))

    def test_calculate_tax_to_pay(self):
        report = dividends.open_csv_file()
        dividends_report, taxes_report = dividends.get_relevant_data_from_report(report)
        tax = dividends.calculate_tax_to_pay(dividends_report, taxes_report)
        self.assertTrue(isinstance(tax, float))
