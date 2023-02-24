from dividends import DividendsHandler
from options import OptionsHandler
from stocks import StocksHandler

year = 2022

stocks_handler = StocksHandler(year=year)
dividends_handler = DividendsHandler(year=year)
options_handler = OptionsHandler(year=year)

total_dividends_tax_to_paid_in_pln = dividends_handler.calculate_tax_to_pay()

total_stocks_tax_to_paid_in_pln = stocks_handler.calculate_tax_to_pay()
total_stocks_revenue_in_pln = stocks_handler.total_revenue_in_pln
total_stocks_cost_in_pln = stocks_handler.total_cost_in_pln

total_options_tax_to_paid_in_pln = options_handler.calculate_tax_to_pay()
total_options_revenue_in_pln = options_handler.total_revenue_in_pln
total_options_cost_in_pln = options_handler.total_cost_in_pln

total_tax = total_dividends_tax_to_paid_in_pln + total_stocks_tax_to_paid_in_pln + total_options_tax_to_paid_in_pln
total_revenue = total_stocks_revenue_in_pln + total_options_revenue_in_pln
total_cost = total_stocks_cost_in_pln + total_options_cost_in_pln

# dividends_handler.save_records_to_gsheet()

print("REVENUE SUMMARY:")
print(f"STK: {total_stocks_revenue_in_pln} PLN")
print(f"OPT: {total_options_revenue_in_pln} PLN")
print("---------")
print(f"SUM: {round(total_revenue, 2)} PLN")

print("")

print("COST SUMMARY:")
print(f"STK: {total_stocks_cost_in_pln} PLN")
print(f"OPT: {total_options_cost_in_pln} PLN")
print("---------")
print(f"SUM: {round(total_cost, 2)} PLN")
print("")

print("TAX SUMMARY:")
print(f"DIV: {total_dividends_tax_to_paid_in_pln} PLN")
print(f"STK: {total_stocks_tax_to_paid_in_pln} PLN")
print(f"OPT: {total_options_tax_to_paid_in_pln} PLN")
print("---------")
print(f"DIV: {total_dividends_tax_to_paid_in_pln} PLN")
print(f"STK + OPT: {total_stocks_tax_to_paid_in_pln+total_options_tax_to_paid_in_pln} PLN")
print("---------")
print(f"SUM: {round(total_tax, 2)} PLN")
