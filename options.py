import csv
import os
import settings
from datetime import datetime
from utils import get_previous_day_from_date, get_currency_rate_for_date

def get_summary_options_tax():
    report = merge_csv_files()
    options_report = get_relevant_data_from_report(report)
    total_tax_to_paid_in_pln = calculate_tax_to_pay(options_report)
    return total_tax_to_paid_in_pln

def merge_csv_files():
    rows = []
    files = list(filter(lambda file: file.startswith("STOCKS"), os.listdir("data")))
    for file in files:
        rows += open_csv_file(f"data/{file}")
    return rows

def open_csv_file(file):
    rows = []
    with open(file, "r") as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            if row[0] != settings.HEADERS_OF_CSV_FILE:
                rows.append(row[0].replace('"', "").split("|"))
        return rows

def get_relevant_data_from_report(report: list) -> list:
    options_report = []
    id = 0
    for row in report:
        if row[1] in ["OPT"]:
            record = {}
            record["id"] = id
            record["name"] = row[2]
            record["date"] = datetime.strptime(row[3], "%Y%m%d")
            record["amount"] = float(row[4])
            record["currency"] = row[0]
            record["price"] = round(float(row[5]), 2)
            record["value_usd"] = round(float(row[6]), 2)
            record["currency_rate_d_1"] = get_currency_rate_for_date(record["currency"], get_previous_day_from_date(record["date"]))
            record["value_pln"] = round(record["value_usd"]*record["currency_rate_d_1"], 2)
            options_report.append(record)
        id += 1
    return options_report


def calculate_tax_to_pay(options_report: list) -> float:
    total_tax_to_paid_in_pln = 0
    tax_rate = 0.19
    # print("--" * 50)
    # print("OPTIONS:")
    # print("--" * 50)

    for option in options_report:
        if option['amount'] < 0:
            tax_to_paid_in_pln = round(tax_rate * option['value_pln'], 2)
            total_tax_to_paid_in_pln += tax_to_paid_in_pln
            # TODO: check option which was sold and then bought again - only some values in sold ones - example 2021 BYSI stocks

    return round(total_tax_to_paid_in_pln, 2)
