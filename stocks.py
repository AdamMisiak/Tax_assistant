import csv
import os
from datetime import datetime
from typing import Any, Dict, List

from dotenv import load_dotenv

from utils import get_currency_rate_for_date, get_previous_day_from_date

# get data from: https://nbp.pl/kursy/Archiwum/archiwum_tab_a_2021.xls
load_dotenv()


# TODO create TaxHandler with some basic methods
# TODO use calculate_tax_to_pay same method in every handler,
# changing only attributes in class


class StocksHandler:
    def __init__(self):
        self.total_tax_to_paid_in_pln = 0
        self.tax_rate = 0.19
        self.year = 2022

    def calculate_tax_to_pay(self) -> float:
        report_data = self.get_report_data()
        return self._calculate_tax_to_pay(report_data)

    def get_report_data(self) -> List[Dict[str, Any]]:
        reports = self.merge_csv_report()
        return self.fetch_relevant_data(reports, "STK")

    def merge_csv_report(self):
        rows = []
        files = list(filter(lambda file: file.startswith("STOCKS"), os.listdir("data")))
        for file in files:
            rows += self.get_csv_report(f"data/{file}")
        return rows

    @staticmethod
    def get_csv_report(file_name: str) -> List[List[str]]:
        with open(file=file_name, mode="r", encoding="utf-8") as file:
            csvreader = csv.reader(file)
            return [row[0].replace('"', "").split("|") for row in csvreader]

    @staticmethod
    def fetch_relevant_data(report: List[List[str]], filtered_field: str) -> List[Dict[str, Any]]:
        results = []
        for row in report:
            if row[1] == filtered_field:
                record = {}
                record["ticker"] = row[2]
                record["date"] = datetime.strptime(row[3], "%Y%m%d")
                record["amount"] = float(row[4])
                record["currency"] = row[0]
                record["price"] = round(float(row[5]), 2)
                record["value_usd"] = round(float(row[6]), 2)
                record["currency_rate_d_1"] = get_currency_rate_for_date(
                    record["currency"], get_previous_day_from_date(record["date"])
                )
                record["value_pln"] = round(record["value_usd"] * record["currency_rate_d_1"], 2)
                results.append(record)
        return results

    def _calculate_tax_to_pay(self, stocks: List[Dict[str, Any]]) -> float:
        for transaction in stocks:
            if transaction["amount"] < 0 and transaction["date"].year == self.year:
                print(transaction)
                opening_transaction = self._find_opening_transactions(transaction, stocks)
                print(opening_transaction)
                # profit_or_loss = round(
                #     transaction["value_pln"] + opening_transaction["value_pln"], 2
                # )
                # self.total_tax_to_paid_in_pln += round(profit_or_loss * self.tax_rate, 2)

        return round(self.total_tax_to_paid_in_pln, 2)

    def _find_opening_transactions(self, closing_transaction, report):
        # Already sorted by date
        matching_transactions = list(
            filter(
                lambda transaction: transaction["ticker"] == closing_transaction["ticker"]
                and transaction["amount"] > 0,
                # and not transaction["calculated"],
                report,
            )
        )
        if abs(matching_transactions[0]["amount"]) == abs(closing_transaction["amount"]):
            matching_transactions[0]["calculated"] = True
            return matching_transactions[0]
        else:
            returned_transaction = {"amount": 0, "value_pln": 0}

            for transaction in matching_transactions:
                returned_transaction["amount"] += abs(transaction["amount"])
                returned_transaction["value_pln"] += transaction["value_pln"]
                if returned_transaction["amount"] == abs(closing_transaction["amount"]):
                    return returned_transaction


# import csv
# import os
# from datetime import datetime

# import settings
# from utils import get_currency_rate_for_date, get_previous_day_from_date


# def get_summary_stocks_tax():
#     report = merge_csv_files()
#     stocks_report = get_relevant_data_from_report(report)
#     stocks_report.sort(key=lambda row: row["date"])
#     total_tax_to_paid_in_pln = calculate_tax_to_pay(stocks_report)
#     return total_tax_to_paid_in_pln


# def merge_csv_files():
#     rows = []
#     files = list(filter(lambda file: file.startswith("STOCKS"), os.listdir("data")))
#     for file in files:
#         rows += open_csv_file(f"data/{file}")
#     return rows


# def open_csv_file(file):
#     rows = []
#     with open(file, "r") as file:
#         csvreader = csv.reader(file)
#         header = next(csvreader)
#         for row in csvreader:
#             if row[0] != settings.HEADERS_OF_CSV_FILE:
#                 rows.append(row[0].replace('"', "").split("|"))
#         return rows


# def get_relevant_data_from_report(report: list) -> list:
#     stocks_report = []
#     id = 0
#     for row in report:
#         if row[1] in ["STK"]:
#             record = {}
#             record["id"] = id
#             record["name"] = row[2]
#             record["date"] = datetime.strptime(row[3], "%Y%m%d")
#             record["amount"] = float(row[4])
#             record["currency"] = row[0]
#             record["price"] = round(float(row[5]), 2)
#             record["value_usd"] = round(float(row[6]), 2)
#             record["currency_rate_d_1"] = get_currency_rate_for_date(
#                 record["currency"], get_previous_day_from_date(record["date"])
#             )
#             record["value_pln"] = round(record["value_usd"] * record["currency_rate_d_1"], 2)
#             record["calculated"] = False
#             stocks_report.append(record)
#         id += 1
#     return stocks_report


# def calculate_tax_to_pay(stocks_report: list) -> float:
#     total_tax_to_paid_in_pln = 0
#     tax_rate = 0.19
#     # print("--" * 50)
#     # print("STOCKS:")
#     # print("--" * 50)

#     for transaction in stocks_report:
#         if transaction["amount"] < 0 and transaction["date"].year == 2021:
#             opening_transaction = find_opening_transactions(transaction, stocks_report)
#             profit_or_loss = round(transaction["value_pln"] + opening_transaction["value_pln"], 2)
#             total_tax_to_paid_in_pln += round(profit_or_loss * tax_rate, 2)

#     return round(total_tax_to_paid_in_pln, 2)


# def find_opening_transactions(closing_transaction, report):
#     # Already sorted by date
#     matching_transactions = list(
#         filter(
#             lambda transaction: transaction["name"] == closing_transaction["name"]
#             and transaction["amount"] > 0
#             and not transaction["calculated"],
#             report,
#         )
#     )
#     if abs(matching_transactions[0]["amount"]) == abs(closing_transaction["amount"]):
#         matching_transactions[0]["calculated"] = True
#         return matching_transactions[0]
#     else:
#         returned_transaction = {"amount": 0, "value_pln": 0}

#         for transaction in matching_transactions:
#             returned_transaction["amount"] += abs(transaction["amount"])
#             returned_transaction["value_pln"] += transaction["value_pln"]
#             if returned_transaction["amount"] == abs(closing_transaction["amount"]):
#                 return returned_transaction
