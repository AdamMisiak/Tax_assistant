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
        return sorted(self.fetch_relevant_data(reports, "STK"), key=lambda row: row["date"])

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
                record["already_used_in_calculations"] = False
                results.append(record)
        return results

    def _calculate_tax_to_pay(self, stocks: List[Dict[str, Any]]) -> float:
        for transaction in stocks:
            if transaction["amount"] < 0 and transaction["date"].year == self.year:
                opening_transaction = self._find_opening_transactions(transaction, stocks)
                profit_or_loss = round(transaction["value_pln"] + opening_transaction["value_pln"], 2)
                self.total_tax_to_paid_in_pln += round(profit_or_loss * self.tax_rate, 2)

        return round(self.total_tax_to_paid_in_pln, 2)

    def _find_opening_transactions(
        self, closing_transaction: Dict[str, Any], stocks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        matching_transactions = list(
            filter(
                lambda transaction: transaction["ticker"] == closing_transaction["ticker"]
                and transaction["amount"] > 0
                and not transaction["already_used_in_calculations"],
                stocks,
            )
        )
        earliest_opening_transaction = matching_transactions[0]
        if abs(earliest_opening_transaction["amount"]) == abs(closing_transaction["amount"]):
            earliest_opening_transaction["already_used_in_calculations"] = True
            return earliest_opening_transaction

        opening_mixed_transaction = {"amount": 0, "value_pln": 0}

        for transaction in matching_transactions:
            opening_mixed_transaction["amount"] += abs(transaction["amount"])
            opening_mixed_transaction["value_pln"] += transaction["value_pln"]
            if opening_mixed_transaction["amount"] == abs(closing_transaction["amount"]):
                return opening_mixed_transaction
