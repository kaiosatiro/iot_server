from datetime import datetime


def validate_datetime(date_str):
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for format in formats:
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            continue
    return False
