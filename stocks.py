import csv
import os
import settings
import requests
from datetime import datetime, timedelta
from typing import Tuple, Union
from utils import get_previous_day_from_date


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
        
def get_relevant_data_from_report(report: list) -> Tuple[list, list]:
    stocks_report = []
    options_report = []
    for row in report:
        if row[1] in ["STK"]:
            record = {}
            record["name"] = row[2]
            record["date"] = row[3]
            record["amount"] = row[4]
            record["currency"] = row[0]
            record["price"] = row[5]
            record["value"] = row[6]
            stocks_report.append(record)
        elif row[1] in ["OPT"]:
            record = {}
            record["name"] = row[2]
            record["date"] = row[3]
            record["amount"] = row[4]
            record["currency"] = row[0]
            record["price"] = row[5]
            record["value"] = row[6]
            options_report.append(record)
    return stocks_report, options_report

def get_currency_rate_for_date(currency: str, date: str) -> float:
    date = date.strftime("%Y-%m-%d")
    url = settings.URL_BASE + date
    response = requests.get(url, {"format": "api"})
    # this day is holiday/weekend, take previous day
    while response.status_code == 404:
        date = get_previous_day_from_date(date)
        date = date.strftime("%Y-%m-%d")
        url = settings.URL_BASE + date
        response = requests.get(url, {"format": "api"})
    for rate in response.json()[0]["rates"]:
        if rate["code"] == currency:
            result = rate["mid"]
    print(date, result)
    return result

def calculate_tax_to_pay(opening_transaction: dict, closing_transaction: dict) -> float:
    opening_transaction_rate = get_currency_rate_for_date(opening_transaction['currency'], get_previous_day_from_date(opening_transaction['date']))
    closing_transaction_rate = get_currency_rate_for_date(closing_transaction['currency'], get_previous_day_from_date(closing_transaction['date']))
    print(opening_transaction, closing_transaction)
    print(opening_transaction_rate, closing_transaction_rate)
    # need currency rates

    # return total_tax_to_paid_in_pln

def find_all_transactions_of_stock(closing_transaction, report):
    all_transactions = list(filter(lambda transaction: transaction["name"] == closing_transaction["name"] and int(transaction['amount']) > 0, report))

    # rule FIFO
    opening_transaction = all_transactions[0]
    calculate_tax_to_pay(opening_transaction, closing_transaction)

if __name__ == "__main__":
    report = merge_csv_files()
    stocks_report, options_report = get_relevant_data_from_report(report)
    stocks_report.sort(key=lambda row: datetime.strptime(row['date'], "%Y%m%d"))

    # print(options_report)
    for transaction in stocks_report:
        if float(transaction["amount"]) < 0 and transaction['date'].startswith("2021"):
            find_all_transactions_of_stock(transaction, stocks_report)