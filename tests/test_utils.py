from unittest import TestCase
from datetime import datetime, timedelta
import utils
from os.path import exists


class TestUtils(TestCase):
    def test_create_csv_rates_file(self):
        path_to_file = "tests/data"
        utils.get_csv_file_with_rates("2021", path_to_file)
        self.assertTrue(exists(path_to_file))

    def test_fetch_data_from_csv_rates_file(self):
        rows = utils.get_data_from_csv_file_with_rates("2021")
        first_row = rows[0]
        self.assertTrue(isinstance(rows, list))
        self.assertTrue("date" in first_row)
        self.assertTrue("USD" in first_row)
        self.assertTrue("EUR" in first_row)
        self.assertTrue("GBP" in first_row)
        self.assertTrue("CAD" in first_row)
        self.assertTrue("AUD" in first_row)
        self.assertTrue("HKD" in first_row)
        self.assertTrue("CHF" in first_row)
        self.assertTrue("RUB" in first_row)
        self.assertTrue("CNY" in first_row)

    def test_get_previous_date(self):
        current_date = datetime.now()
        previous_date = utils.get_previous_day_from_date(current_date)
        self.assertEqual(previous_date, current_date - timedelta(days=1))
        self.assertEqual(previous_date.day, (current_date - timedelta(days=1)).day)

    def test_get_currency_rate_of_usd(self):
        date_to_test = datetime(year=2021, month=6, day=17)
        currency_rate = utils.get_currency_rate_for_date("USD", date_to_test)
        self.assertEqual(currency_rate, 3.7931)

    def test_get_currency_rate_of_gbp(self):
        date_to_test = datetime(year=2021, month=2, day=2)
        currency_rate = utils.get_currency_rate_for_date("GBP", date_to_test)
        self.assertEqual(currency_rate, 5.1069)

    def test_get_currency_rate_of_pln(self):
        date_to_test = datetime(year=2021, month=6, day=17)
        currency_rate = utils.get_currency_rate_for_date("PLN", date_to_test)
        self.assertEqual(currency_rate, 1)
