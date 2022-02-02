import csv
import os
import settings
import requests
from datetime import datetime, timedelta
from typing import Tuple, Union
from utils import get_previous_day_from_date

def get_relevant_data_from_report(report: list) -> list:
    options_report = []
    id = 0
    for row in report:
        if row[1] in ["OPT"]:
            record = {}
            record["id"] = id
            record["name"] = row[2]
            record["date"] = datetime.strptime(row[3], "%Y%m%d")
            record["amount"] = float(row[4])
            record["currency"] = row[0]
            record["price"] = round(float(row[5]), 2)
            record["value"] = round(float(row[6]), 2)
            options_report.append(record)
        id += 1
    return options_report