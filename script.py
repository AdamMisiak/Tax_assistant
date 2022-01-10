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

# def get_dividends_from_report(report: list):
#     for div in report:
#         single_dividend = {}
#         print(div)
#         single_dividend['name'] = div[]


if __name__ == '__main__':
    report = open_csv_file()
    # get_dividends_from_report(report)