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


class DividendHandler:
    def __init__(self):
        credentials_json = {
            "type": os.getenv("type"),
            "project_id": os.getenv("project_id"),
            "private_key_id": os.getenv("private_key_id"),
            "private_key": os.getenv("private_key"),
            "client_email": os.getenv("client_email"),
            "client_id": os.getenv("client_id"),
            "auth_uri": os.getenv("auth_uri"),
            "token_uri": os.getenv("token_uri"),
            "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
            "client_x509_cert_url": os.getenv("client_x509_cert_url"),
        }
        self.google_workbook = GoogleWorkbook(
            credentials_json=credentials_json,
            sheet_url=os.getenv("google_sheet_url"),
            sheet_parameters={
                "value_render_option": "FORMULA",
            },
        )
        self.sheet = self.google_workbook.pull_sheet(os.getenv("tab_name"))
        self.total_tax_to_paid_in_pln = 0
        self.tax_rate = 0.19

    def calculate_tax_to_pay(self) -> float:
        report_data = self.get_report_data()
        return self._calculate_tax_to_pay(report_data.get("dividends"), report_data.get("taxes"))

    def save_records_to_gsheet(self):
        report_data = self.get_report_data()
        return self._save_records_to_gsheet(report_data.get("dividends"))

    def get_report_data(self) -> Dict[str, List[Dict[str, Any]]]:
        report = self.get_csv_report(file_name=settings.DIVIDEND_FILE_CSV)
        return {
            "dividends": self.fetch_relevant_data(report, "Dividends"),
            "taxes": self.fetch_relevant_data(report, "Withholding Tax"),
        }

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

    def _save_records_to_gsheet(self, dividends: List[Dict[str, Any]]):
        for index, received_dividend in enumerate(dividends, 1):
            self.save_record_to_gsheet(received_dividend, index)
            self.sheet.execute_batch(value_input_option="USER_ENTERED")

    def save_record_to_gsheet(self, received_dividend: Dict[str, Any], iterator: int):
        next_row_number = self.sheet.number_of_rows + iterator
        self.sheet.batch_add_multiple_cells(
            cell_list=[
                (next_row_number, "Date", received_dividend.get("date").strftime("%d-%m-%Y")),
                (next_row_number, "Broker", "Interactive Brokers"),
                (next_row_number, "Ticker", received_dividend.get("ticker")),
                (next_row_number, "Currency", received_dividend.get("currency")),
                (next_row_number, "#", self._get_number_of_stock(received_dividend.get("ticker"))),
                (
                    next_row_number,
                    "Currency rate date - 1",
                    f"=NBP_RATE_BEFORE(E{next_row_number};A{next_row_number})",
                ),
                (next_row_number, "Div before tax [CUR]", received_dividend.get("value_usd")),
                (next_row_number, "Div before tax [PLN]", f"=G{next_row_number}*F{next_row_number}"),
                (next_row_number, "Tax required in PL [PLN]", f"=0,19*H{next_row_number}"),
                (next_row_number, "Tax paid %", "15%"),
                (next_row_number, "Tax paid [CUR]", f"=-(J{next_row_number}*G{next_row_number})"),
                (
                    next_row_number,
                    "Tax paid [PLN]",
                    f'=JEŻELI(E{next_row_number}="PLN";K{next_row_number};K{next_row_number}*F{next_row_number})',
                ),
                (next_row_number, "Div after tax [CUR]", f"=G{next_row_number}+K{next_row_number}"),
                (next_row_number, "Div after tax [PLN]", f"=H{next_row_number}+L{next_row_number}"),
                (next_row_number, "Tax paid PL %", "4%"),
                (next_row_number, "Tax paid PL [PLN]", f"=O{next_row_number}*H{next_row_number}"),
            ],
            python_dict_indexing=False,
        )

    def _get_number_of_stock(self, ticker: str) -> int:
        return int(
            next(
                filter(
                    lambda row: row["Ticker"] == ticker,
                    reversed(self.sheet.sheet_data),
                ),
                {"#": 0},
            ).get("#")
        )
