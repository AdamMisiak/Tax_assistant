import csv
import settings
import requests
from datetime import datetime, timedelta
from typing import Tuple, Union


def open_csv_file():
    rows = []
    with open(settings.DIVIDEND_FILE_CSV, "r") as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            rows.append(row[0].replace('"', "").split(";"))
        return rows


def get_relevant_data_from_report(report: list) -> Tuple[list, list]:
    divs_only_report = []
    taxes_only_report = []
    for row in report:
        if row[6] in ["Dividends"]:
            record = {}
            record["name"] = row[1]
            record["date"] = row[3]
            record["amount"] = row[5]
            record["currency"] = row[0]
            divs_only_report.append(record)
        elif row[6] in ["Withholding Tax"]:
            record = {}
            record["name"] = row[1]
            record["date"] = row[3]
            record["amount"] = row[5]
            record["currency"] = row[0]
            taxes_only_report.append(record)
    return divs_only_report, taxes_only_report


def get_previous_day_from_date(date: Union[str, datetime]) -> datetime:
    if isinstance(date, datetime):
        result = date - timedelta(days=1)
        return result
    elif isinstance(date, str) and not "-" in date:
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
        date_in_string_format = f"{day}-{month}-{year}"
        date_in_datetime_format = datetime.strptime(date_in_string_format, "%d-%m-%Y")
        result = date_in_datetime_format - timedelta(days=1)
        return result
    elif isinstance(date, str) and "-" in date:
        date = date.split("-")
        year = date[0]
        month = date[1]
        day = date[2]
        date_in_string_format = f"{day}-{month}-{year}"
        date_in_datetime_format = datetime.strptime(date_in_string_format, "%d-%m-%Y")
        result = date_in_datetime_format - timedelta(days=1)
        return result


def calculate_tax_to_pay(dividends_report: list, taxes_report: list) -> float:
    total_tax_to_paid_in_pln = 0

    for received_dividend in dividends_report:
        paid_withholding_tax = next(
            filter(
                lambda tax: tax["name"] == received_dividend["name"]
                and tax["date"] == received_dividend["date"],
                taxes_report,
            )
        )
        if received_dividend["currency"] != settings.PLN_CURRENCY:
            tax_rate = 0.19
            if received_dividend["name"] in settings.MLP_STOCKS:
                # 37% + 4%
                tax_rate = 0.41

            previous_date = get_previous_day_from_date(received_dividend["date"])
            currency_rate = get_currency_rate_for_date(
                received_dividend["currency"], previous_date
            )
            received_dividend_in_pln = round(
                float(received_dividend["amount"]) * currency_rate, 2
            )
            paid_withholding_tax_in_pln = round(
                float(paid_withholding_tax["amount"]) * currency_rate * -1, 2
            )
            tax_to_paid_in_pln = round(
                tax_rate * received_dividend_in_pln - paid_withholding_tax_in_pln, 2
            )
            total_tax_to_paid_in_pln += tax_to_paid_in_pln

    return total_tax_to_paid_in_pln


def get_currency_rate_for_date(currency: str, date: str) -> float:
    date = date.strftime("%Y-%m-%d")
    url = settings.URL_BASE + date
    response = requests.get(url, {"format": "api"})
    # this day is holiday/weekend, take previous day
    while response.status_code == 404:
        date = get_previous_day_from_date(date)
        date = date.strftime("%Y-%m-%d")
        url = settings.URL_BASE + date
        response = requests.get(url, {"format": "api"})
    for rate in response.json()[0]["rates"]:
        if rate["code"] == currency:
            result = rate["mid"]
    return result


if __name__ == "__main__":
    report = open_csv_file()
    dividends_report, taxes_report = get_relevant_data_from_report(report)
    total_tax_to_paid_in_pln = calculate_tax_to_pay(dividends_report, taxes_report)
    print(total_tax_to_paid_in_pln)
