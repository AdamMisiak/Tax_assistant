import csv
import re
from datetime import datetime, timedelta
from os.path import exists
from typing import Any, Dict, List, Optional

import requests

from settings import PLN_CURRENCY


class TaxHandler:
    def __init__(self, year):
        self.total_tax_to_paid_in_pln = 0
        self.tax_rate = 0.19
        self.year: str = year

    @staticmethod
    def get_csv_report(file_name: str) -> List[List[str]]:
        with open(file=file_name, mode="r", encoding="utf-8") as file:
            csvreader = csv.reader(file)
            return [row[0].replace('"', "").split("|") for row in csvreader if len(row) > 0]

    @staticmethod
    def get_previous_day_from_date(date: datetime) -> datetime:
        if isinstance(date, datetime):
            return date - timedelta(days=1)
        return date

    def get_currency_rate_for_date(self, currency: str, date: datetime) -> float:
        if currency == PLN_CURRENCY:
            return 1
        start_year = date.year
        date_str_format = date.strftime("%Y%m%d")
        rates = self.get_data_from_csv_file_with_rates(date.year)
        index_of_correct_date = self.get_index_of_correct_date(rates, date_str_format)

        while index_of_correct_date is None:
            date -= timedelta(days=1)
            date_str_format = date.strftime("%Y%m%d")
            if date.year != start_year:
                rates = self.get_data_from_csv_file_with_rates(date.year)
            index_of_correct_date = self.get_index_of_correct_date(rates, date_str_format)
        return rates[index_of_correct_date][currency]

    @staticmethod
    def get_data_from_csv_file_with_rates(year: str) -> List[Dict[str, Any]]:
        rows = []
        with open(f"data/RATES{year}.csv", "r", encoding="utf-8") as file:
            csvreader = csv.reader(file, delimiter=";")
            for row in csvreader:
                if len(row) == 0 or not re.match(r"^([\d]+)$", row[0]):
                    continue
                result = {
                    "date": row[0],
                    "USD": float(row[2].replace(",", ".")),
                    "AUD": float(row[3].replace(",", ".")),
                    "HKD": float(row[4].replace(",", ".")),
                    "CAD": float(row[5].replace(",", ".")),
                    "EUR": float(row[8].replace(",", ".")),
                    "CHF": float(row[10].replace(",", ".")),
                    "GBP": float(row[11].replace(",", ".")),
                    "CNY": float(row[34].replace(",", ".")),
                }
                if row[30]:
                    result["RUB"] = float(row[30].replace(",", "."))
                rows.append(result)
        return rows

    @staticmethod
    def get_index_of_correct_date(rates: List[Dict[str, Any]], date_str_format: str) -> Optional[int]:
        return next((index for (index, row) in enumerate(rates) if row["date"] == date_str_format), None)

    @staticmethod
    def get_csv_file_with_rates(year: str):
        response = requests.get(f"https://nbp.pl/kursy/Archiwum/archiwum_tab_a_{year}.csv", allow_redirects=True)
        if not exists(f"data/RATES{year}.csv"):
            with open(file=f"data/RATES{year}.csv", mode="x", encoding="utf-8") as file:
                file.write(response.content.decode("ISO-8859-2"))
