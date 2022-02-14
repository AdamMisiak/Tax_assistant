import csv
import os
import settings
import requests
from datetime import datetime, timedelta
from typing import Tuple, Union
from utils import get_previous_day_from_date, get_currency_rate_for_date

def open_csv_file(file):
    rows = []
    with open(file, "r") as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            if row[0] != settings.HEADERS_OF_CSV_FILE:
                rows.append(row[0].replace('"', "").split("|"))
        return rows

def merge_csv_files():
    rows = []
    files = list(filter(lambda file: file.startswith('STOCKS'), os.listdir("data")))
    for file in files:
        rows += open_csv_file(f"data/{file}")
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
            record["value"] = round(float(row[6]), 2)
            options_report.append(record)
        id += 1
    return options_report

def calculate_tax_to_pay(options_report: list) -> float:
    total_tax_to_paid_in_pln = 0

    for received_options in options_report:
        previous_date = get_previous_day_from_date(received_options["date"])
        currency_rate = get_currency_rate_for_date(
            received_options["currency"], previous_date
        )
        received_option_in_pln = round(
            received_options["price"] * 100 * currency_rate, 2
        )
        tax_to_paid_in_pln = round(
            0.19 * received_option_in_pln, 2
        )
        total_tax_to_paid_in_pln += tax_to_paid_in_pln

    return total_tax_to_paid_in_pln


if __name__ == "__main__":
    report = merge_csv_files()
    options_report = get_relevant_data_from_report(report)
    total_tax_to_paid_in_pln = calculate_tax_to_pay(options_report)
    print(total_tax_to_paid_in_pln)
    
