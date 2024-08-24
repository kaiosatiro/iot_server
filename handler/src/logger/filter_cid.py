from logging import Filter
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from logging import LogRecord


def _trim_string(string: Optional[str], string_length: Optional[int]) -> Optional[str]:
    return string[:string_length] if string_length is not None and string else string


class CorrelationIdFilter(Filter):
    """Logging filter to attached correlation IDs to log records"""

    def __init__(
        self,
        name: str = "",
        uuid_length: Optional[int] = None,
        default_value: Optional[str] = None,
    ):
        super().__init__(name=name)
        self.corrid_length = uuid_length
        self.default_value = default_value

    def filter(self, record: "LogRecord") -> bool:
        corrid = record.corrid if hasattr(record, "corrid") else self.default_value
        record.correlation_id = _trim_string(corrid, self.corrid_length)
        return True
