import csv
import settings
import requests
from datetime import datetime, timedelta

def open_csv_file():
    rows = []
    with open(settings.DIVIDEND_FILE_CSV, 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            rows.append(row[0].replace('"', "").split(';'))
        return rows

def get_relevant_data_from_report(report: list):
    divs_only_report = []
    taxes_only_report = []
    for row in report:
        if row[6] in ['Dividends']:
            record = {}
            record['name'] = row[1]
            record['date'] = row[3]
            record['amount'] = row[5]
            record['currency'] = row[0]
            divs_only_report.append(record)
        elif row[6] in ['Withholding Tax']:
            record = {}
            record['name'] = row[1]
            record['date'] = row[3]
            record['amount'] = row[5]
            record['currency'] = row[0]
            taxes_only_report.append(record)
    return divs_only_report, taxes_only_report

# TODO: Add type hints to `date`
def get_previous_day_from_date(date):
    if isinstance(date, datetime):
        result = date - timedelta(days=1)
        return result
    elif isinstance(date, str) and not '-' in date:
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
        date_in_string_format = f"{day}-{month}-{year}"
        date_in_datetime_format = datetime.strptime(date_in_string_format, '%d-%m-%Y')
        result = date_in_datetime_format - timedelta(days=1)
        return result
    elif isinstance(date, str) and '-' in date:
        date = date.split("-")
        year = date[0]
        month = date[1]
        day = date[2]
        date_in_string_format = f"{day}-{month}-{year}"
        date_in_datetime_format = datetime.strptime(date_in_string_format, '%d-%m-%Y')
        result = date_in_datetime_format - timedelta(days=1)
        return result


def calculate_tax_to_pay(dividends_report: list):
    pass

def get_currency_rate(currency: str, date: str):
    date = date.strftime('%Y-%m-%d')
    url = settings.URL_BASE + date
    response = requests.get(url, {'format': 'api'})
    while response.status_code == 404: #this day is holiday/weekend, take previous day 
        date = get_previous_day_from_date(date)
        date = date.strftime('%Y-%m-%d')
        url = settings.URL_BASE + date
        response = requests.get(url, {'format': 'api'})
        # get_currency_rate(currency, previous_date)
    for rate in response.json()[0]['rates']:
        if rate['code'] == currency:
            result = rate['mid']
    return result


if __name__ == '__main__':
    report = open_csv_file()
    dividends_report, taxes_report = get_relevant_data_from_report(report)
    print(taxes_report)
    for div in dividends_report:
        print(div)
        previous_date = get_previous_day_from_date(div['date'])
        # print(previous_date)
        if div['currency'] != settings.PLN_CURRENCY:
            currency_rate = get_currency_rate(div['currency'], previous_date)
            div_in_pln = round(float(div['amount']) * currency_rate, 2)
            print(div_in_pln)