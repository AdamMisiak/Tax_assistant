import csv
import os
import settings
import requests
from datetime import datetime, timedelta
from typing import Tuple, Union


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
    # moze dodac t212
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

def find_all_transactions_of_stock(closing_transaction, report):
    print(closing_transaction)
    all_transactions = list(filter(lambda transaction: transaction["name"] == closing_transaction["name"] and int(transaction['amount']) > 0, report))

    print(all_transactions)
    opening_transaction = all_transactions[0]

if __name__ == "__main__":
    report = merge_csv_files()
    stocks_report, options_report = get_relevant_data_from_report(report)
    stocks_report.sort(key=lambda row: datetime.strptime(row['date'], "%Y%m%d"))
    
    # print(options_report)
    for transaction in stocks_report:
        if float(transaction["amount"]) < 0 and transaction['date'].startswith("2021"):
            find_all_transactions_of_stock(transaction, stocks_report)