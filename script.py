import csv
import settings

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


if __name__ == '__main__':
    report = open_csv_file()
    divs_only_report = get_dividends_from_report(report)
    print(divs_only_report)