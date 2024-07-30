import pytest

from src.utils import validate_datetime


@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("2024-07-22 13:00:44", True),
        ("2024-07-22 25:00:44", False),  # Invalid hour
        ("2024-07-22 13:60:44", False),  # Invalid minute
        ("2024-07-22 13:00:60", False),  # Invalid second
        ("2024-02-30 13:00:44", False),  # Invalid day
        ("2024-07-22", True),            # Missing time
        ("13:00:44", False),              # Missing date
        ("2024-07-22 13:00", False),      # Missing seconds
        ("2024-07-22 13:00:44.123", False), # Extra milliseconds
        ("2024/07/22 13:00:44", False),  # Wrong date separator
        ("2024-07-22T13:00:44", False),  # Wrong datetime separator
        ("2024-07-22 13:00:44 ", False), # Trailing space
        (" 2024-07-22 13:00:44", False), # Leading space
        ("2024-07-22 13:00:44Z", False),  # Timezone
        ("2024-07-22 13:00:44+03:00", False),  # Timezone
        ("fasdfgasd", False),            # Invalid
    ]
)
def test_validate_datetime(date_str, expected):
    assert validate_datetime(date_str) == expected