# pylint: disable=W0640
# cell-var-from-loop

import csv
import os
from datetime import datetime
from typing import Any, Dict, List

from dotenv import load_dotenv

import settings
from gsheet import GoogleWorkbook
from utils import get_currency_rate_for_date, get_previous_day_from_date

# get data from: https://nbp.pl/kursy/Archiwum/archiwum_tab_a_2021.xls
load_dotenv()


# TODO create TaxHandler with some basic methods
# TODO use calculate_tax_to_pay same method in every handler,
# changing only attributes in class


class OptionHandler:
    def __init__(self):
        self.total_tax_to_paid_in_pln = 0
        self.tax_rate = 0.19

    def calculate_tax_to_pay(self) -> float:
        report_data = self.get_report_data()
        # return self._calculate_tax_to_pay(report_data.get("dividends"), report_data.get("taxes"))

    def get_report_data(self) -> Dict[str, List[Dict[str, Any]]]:
        reports = self.merge_csv_files()
        print(reports)
        # return {
        #     "dividends": self.fetch_relevant_data(report, "Dividends"),
        #     "taxes": self.fetch_relevant_data(report, "Withholding Tax"),
        # }

    def merge_csv_files(self):
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
            if row[5] == filtered_field:
                record = {}
                record["ticker"] = row[1]
                record["date"] = datetime.strptime(row[3].split(";")[0], "%Y%m%d")
                record["value_usd"] = float(row[4])
                record["currency"] = row[0]
                record["currency_rate_d_1"] = get_currency_rate_for_date(
                    record["currency"], get_previous_day_from_date(record["date"])
                )
                record["value_pln"] = round(record["value_usd"] * record["currency_rate_d_1"], 2)
                results.append(record)
        return results

    def _calculate_tax_to_pay(self, dividends: List[Dict[str, Any]], taxes: List[Dict[str, Any]]) -> float:
        for received_dividend in dividends:
            matching_paid_tax = self.get_matching_paid_tax(
                received_dividend["ticker"], received_dividend["date"], taxes
            )
            tax_to_paid_in_pln = round(
                self.tax_rate * received_dividend["value_pln"] + matching_paid_tax["value_pln"],
                2,
            )
            self.total_tax_to_paid_in_pln += tax_to_paid_in_pln
        return round(self.total_tax_to_paid_in_pln, 2)

    @staticmethod
    def get_matching_paid_tax(ticker: str, date: datetime, taxes: List[Dict[str, Any]]) -> Dict[str, Any]:
        return next(
            filter(
                lambda paid_tax: paid_tax["ticker"] == ticker and paid_tax["date"] == date,
                taxes,
            ),
            {"value_pln": 0},
        )


# import csv
# import os
# import settings
# from datetime import datetime
# from utils import get_previous_day_from_date, get_currency_rate_for_date


# def get_summary_options_tax():
#     report = merge_csv_files()
#     options_report = get_relevant_data_from_report(report)
#     total_tax_to_paid_in_pln = calculate_tax_to_pay(options_report)
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
#     options_report = []
#     id = 0
#     for row in report:
#         if row[1] in ["OPT"]:
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
#             record["value_pln"] = round(
#                 record["value_usd"] * record["currency_rate_d_1"], 2
#             )
#             options_report.append(record)
#         id += 1
#     return options_report


# def calculate_tax_to_pay(options_report: list) -> float:
#     total_tax_to_paid_in_pln = 0
#     tax_rate = 0.19
#     # print("--" * 50)
#     # print("OPTIONS:")
#     # print("--" * 50)

#     for option in options_report:
#         if option["amount"] < 0:
#             tax_to_paid_in_pln = round(tax_rate * option["value_pln"], 2)
#             total_tax_to_paid_in_pln += tax_to_paid_in_pln
#             # TODO: check option which was sold and then bought again - only some values in sold ones - example 2021 BYSI stocks

# return round(total_tax_to_paid_in_pln, 2)
