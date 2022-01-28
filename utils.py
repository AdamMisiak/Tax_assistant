from datetime import datetime, timedelta
from typing import Union


def get_previous_day_from_date(date: Union[str, datetime]) -> datetime:
    if isinstance(date, datetime):
        result = date - timedelta(days=1)
        return result
    elif isinstance(date, str) and not "-" in date:
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
        date_in_string_format = f"{day}-{month}-{year}"
        date_in_datetime_format = datetime.strptime(date_in_string_format, "%d-%m-%Y")
        result = date_in_datetime_format - timedelta(days=1)
        return result
    elif isinstance(date, str) and "-" in date:
        date = date.split("-")
        year = date[0]
        month = date[1]
        day = date[2]
        date_in_string_format = f"{day}-{month}-{year}"
        date_in_datetime_format = datetime.strptime(date_in_string_format, "%d-%m-%Y")
        result = date_in_datetime_format - timedelta(days=1)
        return result