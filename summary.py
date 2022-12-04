import json

from dividends import DividendHandler
from options import OptionHandler
from stocks import get_summary_stocks_tax
from utils import get_csv_file_with_rates

dividend_handler = DividendHandler()
option_handler = OptionHandler()
# total_dividends_tax_to_paid_in_pln = dividend_handler.save_records_to_gsheet()
total_options_tax_to_paid_in_pln = option_handler.calculate_tax_to_pay()

print("SUMMARY:")
# print("---" * 20)
# print(f"DIV: {total_dividends_tax_to_paid_in_pln} PLN")
# print("---" * 20)
# # print(f"STK: {total_tax_to_paid_in_pln_stocks} PLN")
# # print("---" * 20)
print(f"OPT: {total_options_tax_to_paid_in_pln} PLN")
# # print("---" * 20)
# print(
#     f"SUM: {round(total_tax_to_paid_in_pln_dividends+total_tax_to_paid_in_pln_stocks+total_tax_to_paid_in_pln_options, 2)} PLN"
# )
