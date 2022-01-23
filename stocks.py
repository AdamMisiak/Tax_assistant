import csv
import settings
import requests
from datetime import datetime, timedelta
from typing import Tuple, Union


def open_csv_file():
    rows = []
    with open(settings.STOCKS_FILE_CSV, "r") as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            rows.append(row[0].replace('"', "").split("|"))
        return rows

        
def get_relevant_data_from_report(report: list) -> Tuple[list, list]:
    stocks_report = []
    options_report = []
    for row in report:
        print(row)
        if row[1] in ["STK"]:
            record = {}
            record["name"] = row[2]
            record["date"] = row[3]
            record["amount"] = row[4]
            record["currency"] = row[0]
            record["price"] = row[5]
            record["value"] = row[6]
            stocks_report.append(record)
        elif row[1] in ["OPT"]:
            record = {}
            record["name"] = row[2]
            record["date"] = row[3]
            record["amount"] = row[4]
            record["currency"] = row[0]
            record["price"] = row[5]
            record["value"] = row[6]
            options_report.append(record)
    return stocks_report, options_report

if __name__ == "__main__":
    report = open_csv_file()
    stocks_report, options_report = get_relevant_data_from_report(report)
    print(stocks_report)
    print(options_report)