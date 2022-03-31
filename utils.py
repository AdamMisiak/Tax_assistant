from datetime import datetime, timedelta
import csv
import settings
import requests
import re
from settings import PLN_CURRENCY

def get_csv_file_with_rates(year: str, path: str):
    response = requests.get(
        f"https://nbp.pl/kursy/Archiwum/archiwum_tab_a_{year}.csv", allow_redirects=True
    )
    file = open(f"{path}/RATES{year}.csv", "x")
    file.write(response.content.decode("ISO-8859-2"))
    file.close()


def get_data_from_csv_file_with_rates(year: str):
    rows = []
    with open(f"data/RATES{year}.csv", "r") as file:
        csvreader = csv.reader(file, delimiter=";")
        for number, row in enumerate(csvreader):
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
                "RUB": float(row[30].replace(",", ".")),
                "CNY": float(row[34].replace(",", ".")),
            }
            rows.append(result)
    return rows


def get_previous_day_from_date(date: datetime) -> datetime:
    if isinstance(date, datetime):
        result = date - timedelta(days=1)
        return result
    # elif isinstance(date, str) and not "-" in date:
    #     year = date[:4]
    #     month = date[4:6]
    #     day = date[6:8]
    #     date_in_string_format = f"{day}-{month}-{year}"
    #     date_in_datetime_format = datetime.strptime(date_in_string_format, "%d-%m-%Y")
    #     result = date_in_datetime_format - timedelta(days=1)
    #     return result
    # elif isinstance(date, str) and "-" in date:
    #     date = date.split("-")
    #     year = date[0]
    #     month = date[1]
    #     day = date[2]
    #     date_in_string_format = f"{day}-{month}-{year}"
    #     date_in_datetime_format = datetime.strptime(date_in_string_format, "%d-%m-%Y")
    #     result = date_in_datetime_format - timedelta(days=1)
    # return result


def get_currency_rate_for_date(currency: str, date: datetime) -> float:
    if currency == PLN_CURRENCY:
        return 1
    start_year = date.year
    date_str_format = date.strftime("%Y%m%d")
    rates = get_data_from_csv_file_with_rates(date.year)
    index_of_proper_date = next(
        (index for (index, row) in enumerate(rates) if row["date"] == date_str_format),
        None,
    )
    while index_of_proper_date is None:
        date -= timedelta(days=1)
        date_str_format = date.strftime("%Y%m%d")
        if date.year != start_year:
            rates = get_data_from_csv_file_with_rates(date.year)
        index_of_proper_date = next(
            (
                index
                for (index, row) in enumerate(rates)
                if row["date"] == date_str_format
            ),
            None,
        )
    return rates[index_of_proper_date][currency]


# not used in divs
def get_currency_rate_for_date_api(currency: str, date: str) -> float:
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
