from unittest import TestCase
import utils
from os.path import exists

class TestUtils(TestCase):
    def test_create_csv_rates_file(self):
        path_to_file = "tests/data"
        utils.get_csv_file_with_rates("2021", path_to_file)
        self.assertTrue(exists(path_to_file))
