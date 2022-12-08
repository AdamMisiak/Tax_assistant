import json

from dividends import DividendsHandler
from options import OptionsHandler
from stocks import StocksHandler
from utils import get_csv_file_with_rates

stocks_handler = StocksHandler()
dividends_handler = DividendsHandler()
options_handler = OptionsHandler()
total_stocks_tax_to_paid_in_pln = stocks_handler.calculate_tax_to_pay()
total_dividends_tax_to_paid_in_pln = dividends_handler.calculate_tax_to_pay()
total_options_tax_to_paid_in_pln = options_handler.calculate_tax_to_pay()

print("SUMMARY:")
# print("---" * 20)
print(f"DIV: {total_dividends_tax_to_paid_in_pln} PLN")
# print("---" * 20)
print(f"STK: {total_stocks_tax_to_paid_in_pln} PLN")
# # print("---" * 20)
print(f"OPT: {total_options_tax_to_paid_in_pln} PLN")
# # print("---" * 20)
# print(
#     f"SUM: {round(total_tax_to_paid_in_pln_dividends+total_tax_to_paid_in_pln_stocks+total_tax_to_paid_in_pln_options, 2)} PLN"
# )
