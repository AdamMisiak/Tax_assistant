import json

from dividends import get_summary_dividends_tax
from gsheet import GoogleWorkbook
from options import get_summary_options_tax
from stocks import get_summary_stocks_tax
from utils import get_csv_file_with_rates

with open("credentials.json") as json_file:
    credentials_json = json.load(json_file)

# TODO add envs for links and credentials
google_workbook = GoogleWorkbook(credentials_json=credentials_json, sheet_url="")
sheet = google_workbook.pull_sheet("Div History")
print(sheet.sheet_data)


# total_tax_to_paid_in_pln_dividends = get_summary_dividends_tax()
# # total_tax_to_paid_in_pln_stocks = get_summary_stocks_tax()
# # total_tax_to_paid_in_pln_options = get_summary_options_tax()

# print("SUMMARY:")
# print("---" * 20)
# print(f"DIV: {total_tax_to_paid_in_pln_dividends} PLN")
# print("---" * 20)
# # print(f"STK: {total_tax_to_paid_in_pln_stocks} PLN")
# # print("---" * 20)
# # print(f"OPT: {total_tax_to_paid_in_pln_options} PLN")
# # print("---" * 20)
# print(
#     f"SUM: {round(total_tax_to_paid_in_pln_dividends+total_tax_to_paid_in_pln_stocks+total_tax_to_paid_in_pln_options, 2)} PLN"
# )
