import csv
import os
import settings
import requests
from datetime import datetime
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
    stocks_report = []
    id = 0
    for row in report:
        if row[1] in ["STK"]:
            record = {}
            record["id"] = id
            record["name"] = row[2]
            record["date"] = datetime.strptime(row[3], "%Y%m%d")
            record["amount"] = float(row[4])
            record["currency"] = row[0]
            record["price"] = round(float(row[5]), 2)
            record["value"] = round(float(row[6]), 2)
            stocks_report.append(record)
        id += 1
    return stocks_report

def calculate_tax_to_pay(opening_transaction: dict, closing_transaction: dict) -> float:
    opening_transaction_rate = get_currency_rate_for_date(opening_transaction['currency'], get_previous_day_from_date(opening_transaction['date']))
    closing_transaction_rate = get_currency_rate_for_date(closing_transaction['currency'], get_previous_day_from_date(closing_transaction['date']))

    total_tax_to_paid_in_pln = round(((closing_transaction_rate * closing_transaction['value']) - (opening_transaction_rate * opening_transaction['value'] * -1)) * 0.19, 2)
    return total_tax_to_paid_in_pln

def find_all_transactions_of_stock(closing_transaction, report):
    # and transaction["amount"] * -1 == closing_transaction["amount"]
    all_transactions = list(filter(lambda transaction: transaction["name"] == closing_transaction["name"] and transaction['amount'] > 0, report))
    
    # rule FIFO
    opening_transaction = all_transactions[0]
    return calculate_tax_to_pay(opening_transaction, closing_transaction)

if __name__ == "__main__":
    report = merge_csv_files()
    stocks_report = get_relevant_data_from_report(report)
    stocks_report.sort(key=lambda row: row['date'])
    total_tax_to_paid_in_pln = 0

    for transaction in stocks_report:
        if transaction["amount"] < 0 and transaction['date'].year == 2021 and transaction['name'] != 'GREE':
            total_tax_to_paid_in_pln += find_all_transactions_of_stock(transaction, stocks_report)
    
    total_tax_to_paid_in_pln = round(total_tax_to_paid_in_pln, 2)
    print(total_tax_to_paid_in_pln)
