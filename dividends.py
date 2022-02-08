import csv
import settings
import requests
from datetime import datetime, timedelta
from typing import Tuple, Union
from utils import get_previous_day_from_date
# get data from: https://nbp.pl/kursy/Archiwum/archiwum_tab_a_2021.xls


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
            currency_rate = get_currency_rate_for_date2(
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

def get_csv_file_with_rates(year: str):
    response = requests.get(f"https://nbp.pl/kursy/Archiwum/archiwum_tab_a_{year}.csv", allow_redirects=True)
    open('data/RATES2021.csv', 'w').write(response.content.decode("ISO-8859-2"))


def get_data_from_csv_file_with_rates():
    rows = []
    with open("data/RATES2021.csv", 'r') as file:
        csvreader = csv.reader(file, delimiter=';')
        for number, row in enumerate(csvreader):
            if number in settings.ROWS_TO_DELETE_IN_CSV:
                continue
            result = {
                "date": row[0],
                "USD": float(row[2].replace(',', '.')),
                "AUD": float(row[3].replace(',', '.')),
                "HKD": float(row[4].replace(',', '.')),
                "CAD": float(row[5].replace(',', '.')),
                "EUR": float(row[8].replace(',', '.')),
                "CHF": float(row[10].replace(',', '.')),
                "GBP": float(row[11].replace(',', '.')),
                "RUB": float(row[30].replace(',', '.')),
                "CNY": float(row[34].replace(',', '.')),
            }
            rows.append(result)
    return rows

def get_currency_rate_for_date2(currency: str, date: datetime) -> float:
    date_str_format = date.strftime("%Y%m%d")
    rates = get_data_from_csv_file_with_rates()
    index_of_proper_date = next((index for (index, row) in enumerate(rates) if row["date"] == date_str_format), None)

    while index_of_proper_date is None:
        date -= timedelta(days=1)
        date_str_format = date.strftime("%Y%m%d")
        index_of_proper_date = next((index for (index, row) in enumerate(rates) if row["date"] == date_str_format), None)
    return rates[index_of_proper_date][currency]

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
