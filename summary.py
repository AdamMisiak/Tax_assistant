from dividends import get_summary_dividends_tax
from stocks import get_summary_stocks_tax
from options import get_summary_options_tax

total_tax_to_paid_in_pln_dividends = get_summary_dividends_tax()
total_tax_to_paid_in_pln_stocks = get_summary_stocks_tax()
total_tax_to_paid_in_pln_options = get_summary_options_tax()
print("div",total_tax_to_paid_in_pln_dividends)
print("stk",total_tax_to_paid_in_pln_stocks)
print("opt",total_tax_to_paid_in_pln_options)

# sprawdz div bo cos sie nie zgadzaja kursy (1 div w porownaniu do tych z excela i ze strony)
# calosc tez sie nie zgadza