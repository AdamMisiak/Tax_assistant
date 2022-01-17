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
    total_tax_to_paid_in_pln = 0
    for received_dividend in dividends_report:
        print(received_dividend)
        paid_withholding_tax = next(filter(lambda tax: tax['name'] == received_dividend['name'] and tax['date'] == received_dividend['date'], taxes_report))
        print(paid_withholding_tax)
        previous_date = get_previous_day_from_date(received_dividend['date'])
        if received_dividend['currency'] != settings.PLN_CURRENCY:
            tax_rate = 0.19
            if received_dividend['name'] in settings.MLP_STOCKS:
                # TODO: check how to calculate MLP taxes, right now it is 0pln - 0.37 change to 0.42?
                tax_rate = 0.37
            currency_rate = get_currency_rate(received_dividend['currency'], previous_date)
            received_dividend_in_pln = round(float(received_dividend['amount']) * currency_rate, 2)
            print(received_dividend_in_pln)
            paid_withholding_tax_in_pln = round(float(paid_withholding_tax['amount']) * currency_rate * -1, 2)
            print(paid_withholding_tax_in_pln)
            tax_to_paid_in_pln = round(tax_rate * received_dividend_in_pln - paid_withholding_tax_in_pln, 2)
            print(tax_to_paid_in_pln)
            total_tax_to_paid_in_pln += tax_to_paid_in_pln
    print(total_tax_to_paid_in_pln)