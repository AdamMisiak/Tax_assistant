from dividends import get_summary_dividends_tax
from stocks import get_summary_stocks_tax
from options import get_summary_options_tax

total_tax_to_paid_in_pln_dividends = get_summary_dividends_tax()
total_tax_to_paid_in_pln_stocks = get_summary_stocks_tax()
total_tax_to_paid_in_pln_options = get_summary_options_tax()

print("DIV:",total_tax_to_paid_in_pln_dividends)
print("STK:",total_tax_to_paid_in_pln_stocks)
print("OPT:",total_tax_to_paid_in_pln_options)
print("SUMMARY:",round(total_tax_to_paid_in_pln_dividends+total_tax_to_paid_in_pln_stocks+total_tax_to_paid_in_pln_options,2))

# TODO SPRAWDZIC OPCJE CZY TAK DUZO WYSZLO