from unittest import TestCase
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
        self.assertTrue('USD' in first_row)
        self.assertTrue('EUR' in first_row)
        self.assertTrue('GBP' in first_row)
        self.assertTrue('CAD' in first_row)
        # add all of them
