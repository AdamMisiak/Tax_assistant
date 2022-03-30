import csv
import settings
from typing import Tuple
from utils import get_previous_day_from_date, get_currency_rate_for_date
from datetime import datetime

# get data from: https://nbp.pl/kursy/Archiwum/archiwum_tab_a_2021.xls

def get_summary_dividends_tax():
    report = open_csv_file()
    dividends_report, taxes_report = get_relevant_data_from_report(report)
    total_tax_to_paid_in_pln = calculate_tax_to_pay(dividends_report, taxes_report)
    return total_tax_to_paid_in_pln

def open_csv_file():
    rows = []
    with open(settings.DIVIDEND_FILE_CSV, "r") as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            rows.append(row[0].replace('"', "").split("|"))
        return rows


def get_relevant_data_from_report(report: list) -> Tuple[list, list]:
    divs_only_report = []
    taxes_only_report = []
    for row in report:
        if row[6] in ["Dividends"]:
            record = {}
            record["name"] = row[1]
            record["date"] = datetime.strptime(row[3], "%Y%m%d")
            record["value_usd"] = float(row[5])
            record["currency"] = row[0]
            record["currency_rate_d_1"] = get_currency_rate_for_date(record["currency"], get_previous_day_from_date(record["date"]))
            record["value_pln"] = round(record["value_usd"]*record["currency_rate_d_1"], 2)
            divs_only_report.append(record)
        elif row[6] in ["Withholding Tax"]:
            record = {}
            record["name"] = row[1]
            record["date"] = datetime.strptime(row[3], "%Y%m%d")
            record["value_usd"] = float(row[5])
            record["currency"] = row[0]
            record["currency_rate_d_1"] = get_currency_rate_for_date(record["currency"], get_previous_day_from_date(record["date"]))
            record["value_pln"] = round(record["value_usd"]*record["currency_rate_d_1"], 2)
            taxes_only_report.append(record)
    return divs_only_report, taxes_only_report


def calculate_tax_to_pay(dividends_report: list, taxes_report: list) -> float:
    total_tax_to_paid_in_pln = 0
    tax_rate = 0.19
    # print("--" * 50)
    # print("DIVIDENDS:")
    # print("--" * 50)

    for received_dividend in dividends_report:
        paid_withholding_tax = next(
            filter(
                lambda tax: tax["name"] == received_dividend["name"]
                and tax["date"] == received_dividend["date"],
                taxes_report,
            )
        )
        
        if received_dividend["currency"] != settings.PLN_CURRENCY:
            tax_rate = 0.19
            if received_dividend["name"] in settings.MLP_STOCKS:
                # 37% + 4%
                tax_rate = 0.41

            tax_to_paid_in_pln = round(
                tax_rate * received_dividend['value_pln'] + paid_withholding_tax['value_pln'], 2
            )
            total_tax_to_paid_in_pln += tax_to_paid_in_pln

    return round(total_tax_to_paid_in_pln, 2)

