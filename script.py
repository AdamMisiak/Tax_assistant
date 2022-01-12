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

def get_dividends_from_report(report: list):
    divs_only_report = []
    for div in report:
        if div[6] in ['Dividends']:
            single_dividend = {}
            single_dividend['name'] = div[1]
            single_dividend['date'] = div[3]
            single_dividend['amount'] = div[5]
            single_dividend['currency'] = div[0]
            divs_only_report.append(single_dividend)
    return divs_only_report

def get_previous_day_from_date(date: str):
    year = date[:4]
    month = date[4:6]
    day = date[6:8]
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

    # while response.status_code == 404: #this day is holiday/weekend, take previous day 
    #     date_in_datetime_format = date_in_datetime_format - datetime.timedelta(days=1)
    #     date_in_string_format = date_in_datetime_format.strftime('%Y-%m-%d')

    #     url = settings.URL_BASE + date_in_string_format
    #     response = requests.get(url, {'format': 'api'})

    # for rate in response.json()[0]['rates']:
    #     if rate['code'] == currency:
    #         result = rate['mid']
    # return result


if __name__ == '__main__':
    report = open_csv_file()
    dividends_report = get_dividends_from_report(report)
    print(dividends_report)
    get_currency_rate("USD", get_previous_day_from_date(dividends_report[0]['date']))
    # print(get_previous_day_from_date(dividends_report[0]['date']))