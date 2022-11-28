# pylint: disable=W0640
# cell-var-from-loop
import csv
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv

import settings
from gsheet import GoogleWorkbook
from utils import get_currency_rate_for_date, get_previous_day_from_date

# get data from: https://nbp.pl/kursy/Archiwum/archiwum_tab_a_2021.xls

load_dotenv()

with open("credentials.json") as json_file:
    credentials_json = json.load(json_file)
google_workbook = GoogleWorkbook(
    credentials_json=credentials_json,
    sheet_url=os.getenv("google_sheet_url"),
    sheet_parameters={
        "value_render_option": "FORMULA",
    },
)
sheet = google_workbook.pull_sheet("Div History")

# TODO create class here for divs only


def get_summary_dividends_tax() -> float:
    report = open_csv_file()
    dividends_report, taxes_report = get_relevant_data_from_report(report)
    total_tax_to_paid_in_pln = calculate_tax_to_pay(dividends_report, taxes_report)
    return total_tax_to_paid_in_pln


def open_csv_file():
    rows = []
    with open(file=settings.DIVIDEND_FILE_CSV, mode="r", encoding="utf-8") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            rows.append(row[0].replace('"', "").split("|"))
        return rows


def get_relevant_data_from_report(report: list) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    dividends_report = []
    taxes_report = []
    for row in report:
        if row[5] in ["Dividends"]:
            record = {}
            record["name"] = row[1]
            record["date"] = datetime.strptime(row[3].split(";")[0], "%Y%m%d")
            record["value_usd"] = float(row[4])
            record["currency"] = row[0]
            record["currency_rate_d_1"] = get_currency_rate_for_date(
                record["currency"], get_previous_day_from_date(record["date"])
            )
            record["value_pln"] = round(record["value_usd"] * record["currency_rate_d_1"], 2)
            dividends_report.append(record)
        elif row[5] in ["Withholding Tax"]:
            record = {}
            record["name"] = row[1]
            record["date"] = datetime.strptime(row[3].split(";")[0], "%Y%m%d")
            record["value_usd"] = float(row[4])
            record["currency"] = row[0]
            record["currency_rate_d_1"] = get_currency_rate_for_date(
                record["currency"], get_previous_day_from_date(record["date"])
            )
            record["value_pln"] = round(record["value_usd"] * record["currency_rate_d_1"], 2)
            taxes_report.append(record)
    return dividends_report, taxes_report


def calculate_tax_to_pay(dividends_report: List[Dict[str, Any]], taxes_report: List[Dict[str, Any]]) -> float:
    total_tax_to_paid_in_pln = 0
    tax_rate = 0.19

    for received_dividend in dividends_report:
        # TODO maybe try except with some print to notify user?
        paid_withholding_tax = next(
            filter(
                lambda paid_tax: paid_tax["name"] == received_dividend["name"]
                and paid_tax["date"] == received_dividend["date"],
                taxes_report,
            ),
            {"value_pln": 0},
        )

        save_record_to_gsheet(received_dividend)
        break

        # if received_dividend["currency"] != settings.PLN_CURRENCY:
        if received_dividend["name"] in settings.MLP_STOCKS:
            # 37% + 4%
            tax_rate = 0.41

        tax_to_paid_in_pln = round(
            tax_rate * received_dividend["value_pln"] + paid_withholding_tax["value_pln"],
            2,
        )
        total_tax_to_paid_in_pln += tax_to_paid_in_pln

    return round(total_tax_to_paid_in_pln, 2)


def save_record_to_gsheet(received_dividend):
    print(received_dividend)
    sheet.batch_add_multiple_cells(
        cell_list=[
            (sheet.number_of_rows - 1, sheet.headers[0], received_dividend.get("date").strftime("%d-%m-%Y")),
            (sheet.number_of_rows - 1, sheet.headers[1], "Interactive Brokers"),
            (sheet.number_of_rows - 1, sheet.headers[2], received_dividend.get("name")),
            (sheet.number_of_rows - 1, sheet.headers[4], received_dividend.get("currency")),
            (
                sheet.number_of_rows - 1,
                sheet.headers[5],
                f"=NBP_RATE_BEFORE(E{sheet.number_of_rows+1};A{sheet.number_of_rows+1})",
            ),
            (sheet.number_of_rows - 1, sheet.headers[6], received_dividend.get("value_usd")),
            (sheet.number_of_rows - 1, sheet.headers[7], f"=G{sheet.number_of_rows+1}*F{sheet.number_of_rows+1}"),
        ]
    )
    # print(sheet.sheet_data[-1])
    # last row to copy from
    # value_input_option="USER_ENTERED" fix for single quote issue
    sheet.execute_batch(value_input_option="USER_ENTERED")
    print("SAVED ROW NR", sheet.number_of_rows - 1)

    # TODO how to get number of stocks - maybe some formula in ghseet?

    # TODO change header[0] to name? refactor this to iterate over some dict?

    # TODO add coping formulas in next steps?
    # https://stackoverflow.com/questions/41992091/how-to-copy-a-formula-from-one-gsheet-to-another-using-python
