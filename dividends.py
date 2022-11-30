# pylint: disable=W0640
# cell-var-from-loop
import csv
import os
from datetime import datetime
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv

import settings
from gsheet import GoogleWorkbook
from utils import get_currency_rate_for_date, get_previous_day_from_date

# get data from: https://nbp.pl/kursy/Archiwum/archiwum_tab_a_2021.xls
load_dotenv()

# class DividendHandler():

#     def __init__(self) -> None:


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

    for index, received_dividend in enumerate(dividends_report, 1):
        # TODO maybe try except with some print to notify user?
        paid_withholding_tax = next(
            filter(
                lambda paid_tax: paid_tax["name"] == received_dividend["name"]
                and paid_tax["date"] == received_dividend["date"],
                taxes_report,
            ),
            {"value_pln": 0},
        )

        save_record_to_gsheet(received_dividend, index)
        sheet.execute_batch(value_input_option="USER_ENTERED")

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


def save_record_to_gsheet(received_dividend, iterator):
    print(received_dividend)
    next_row_number = sheet.number_of_rows + iterator
    sheet.batch_add_multiple_cells(
        cell_list=[
            (next_row_number, "Date", received_dividend.get("date").strftime("%d-%m-%Y")),
            (next_row_number, "Broker", "Interactive Brokers"),
            (next_row_number, "Ticker", received_dividend.get("name")),
            (next_row_number, "Currency", received_dividend.get("currency")),
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
    # value_input_option="USER_ENTERED" fix for single quote issue
    # sheet.execute_batch(value_input_option="USER_ENTERED")
    print("SAVED ROW NR", next_row_number)

    # TODO how to get number of stocks - maybe some formula in ghseet?
