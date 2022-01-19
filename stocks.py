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
            rows.append(row[0].replace('"', "").split(";"))
        return rows

if __name__ == "__main__":
    report = open_csv_file()
    print(report)