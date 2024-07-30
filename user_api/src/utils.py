from datetime import datetime
import random


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


def generate_random_number(start: int, end: int) -> int:
    return random.randint(start, end)