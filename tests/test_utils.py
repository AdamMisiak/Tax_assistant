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
        self.assertTrue('date' in first_row)
        self.assertTrue('USD' in first_row)
        self.assertTrue('EUR' in first_row)
        self.assertTrue('GBP' in first_row)
        self.assertTrue('CAD' in first_row)
        self.assertTrue('AUD' in first_row)
        self.assertTrue('HKD' in first_row)
        self.assertTrue('CHF' in first_row)
        self.assertTrue('RUB' in first_row)
        self.assertTrue('CNY' in first_row)

    def test_get_previous_date(self):
        current_date = datetime.now()
        previous_date = utils.get_previous_day_from_date(current_date)
        self.assertEqual(previous_date, current_date - timedelta(days=1))
        self.assertEqual(previous_date.day, (current_date - timedelta(days=1)).day)