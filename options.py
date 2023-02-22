import os
from datetime import datetime
from typing import Any, Dict, List

from dotenv import load_dotenv

from utils import TaxHandler

# get data from: https://nbp.pl/kursy/Archiwum/archiwum_tab_a_2021.xls
load_dotenv()


class OptionsHandler(TaxHandler):
    def calculate_tax_to_pay(self) -> float:
        report_data = self.get_report_data()
        return self._calculate_tax_to_pay(report_data)

    def get_report_data(self) -> List[Dict[str, Any]]:
        reports = self.merge_csv_report()
        return self.fetch_relevant_data(reports, "OPT")

    def merge_csv_report(self):
        rows = []
        files = list(filter(lambda file: file.startswith("STOCKS"), os.listdir("data")))
        for file in files:
            rows += self.get_csv_report(f"data/{file}")
        return rows

    def fetch_relevant_data(self, report: List[List[str]], filtered_field: str) -> List[Dict[str, Any]]:
        results = []
        for row in report:
            if row[1] == filtered_field:
                record = {}
                record["ticker"] = row[2]
                record["date"] = datetime.strptime(row[3], "%Y%m%d")
                record["amount"] = float(row[4])
                record["currency"] = row[0]
                record["price"] = round(float(row[5]), 2)
                record["premium_usd"] = round(float(row[6]), 2)
                record["currency_rate_d_1"] = self.get_currency_rate_for_date(
                    record["currency"], self.get_previous_day_from_date(record["date"])
                )
                record["premium_pln"] = round(record["premium_usd"] * record["currency_rate_d_1"], 2)
                results.append(record)
        return results

    def _calculate_tax_to_pay(self, options: List[Dict[str, Any]]) -> float:
        for option in options:
            if option["date"].year == self.year:
                tax_to_paid_in_pln = round(self.tax_rate * option["premium_pln"], 2)
                self.total_tax_to_paid_in_pln += tax_to_paid_in_pln
        return round(self.total_tax_to_paid_in_pln, 2)
