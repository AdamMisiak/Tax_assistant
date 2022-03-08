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
    files = list(filter(lambda file: file.startswith("STOCKS"), os.listdir("data")))
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
            record["currency_rate_d_1"] = get_currency_rate_for_date(record["currency"], get_previous_day_from_date(record["date"]))
            record["calculated"] = False
            stocks_report.append(record)
        id += 1
    return stocks_report


def calculate_tax_to_pay(opening_transaction: dict, closing_transaction: dict) -> float:
    opening_transaction_rate = get_currency_rate_for_date(
        opening_transaction["currency"],
        get_previous_day_from_date(opening_transaction["date"]),
    )
    closing_transaction_rate = get_currency_rate_for_date(
        closing_transaction["currency"],
        get_previous_day_from_date(closing_transaction["date"]),
    )

    tax_rate = 0.19
    profit_or_loss_in_pln = round(
        (
            (closing_transaction_rate * closing_transaction["value"])
            - (opening_transaction_rate * opening_transaction["value"] * -1)
        ),
        2,
    )
    total_tax_to_paid_in_pln = round(profit_or_loss_in_pln * tax_rate, 2)

    print(
        f"Open rate {opening_transaction['currency']}: {opening_transaction_rate} - Close rate {closing_transaction['currency']}: {closing_transaction_rate} - Profit/Loss PLN: {profit_or_loss_in_pln} - Tax rate: {tax_rate*100}% - Tax PLN: {total_tax_to_paid_in_pln}"
    )
    print("--" * 50)

    return total_tax_to_paid_in_pln


def get_tax_from_all_transactions_of_stock(closing_transaction, report):
    all_transactions = list(
        filter(
            lambda transaction: transaction["name"] == closing_transaction["name"]
            and transaction["amount"] > 0 and not transaction["calculated"],
            report,
        )
    )

    # rule FIFO
    # TODO: Added implementation of calculating few transactions of buy and one transaction of sell
    opening_transaction = all_transactions[0]
    if closing_transaction['amount']*-1 != opening_transaction['amount']:
        amount_of_stocks_bought = 0
        for transaction in all_transactions:
            amount_of_stocks_bought += transaction['amount']
            # print(calculate_tax_to_pay(transaction, closing_transaction))
            print(transaction)
        print(amount_of_stocks_bought)
    # print(closing_transaction['amount'])
    # print(opening_transaction['amount'])
    # if closing_transaction['amount'] != opening_transaction['amount']*-1:
    #     print('test')
    opening_transaction['calculated'] = True
    return calculate_tax_to_pay(opening_transaction, closing_transaction)


def get_summary_stocks_tax():
    report = merge_csv_files()
    stocks_report = get_relevant_data_from_report(report)
    stocks_report.sort(key=lambda row: row["date"])
    total_tax_to_paid_in_pln = 0

    # print("STOCKS:")
    # print("--" * 50)

    for transaction in stocks_report:
        print(transaction)
    #     if (
    #         transaction["amount"] < 0
    #         and transaction["date"].year == 2021
    #         # and transaction["name"] != "GREE"
    #     ):
            # print(transaction)
    #         total_tax_to_paid_in_pln += get_tax_from_all_transactions_of_stock(
    #             transaction, stocks_report
    #         )

    # total_tax_to_paid_in_pln = round(total_tax_to_paid_in_pln, 2)
    return total_tax_to_paid_in_pln
