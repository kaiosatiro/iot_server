import logging
import pytest
from unittest.mock import MagicMock

from src.logger.channel import LogChannel
from src.logger.handler import LogHandler


class TestLogHandler:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.channel = MagicMock(spec=LogChannel)
        self.handler = LogHandler(channel=self.channel)

    def test_setup_channel(self):
        self.handler.setup_channel()
        self.channel.connect.assert_called_once()
        self.channel.start.assert_called_once()

    def test_emit_channel_ready(self):
        self.handler.channel_ready = True
        self.handler.channel.status.return_value = True

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        self.handler.emit(record)

        self.channel.publish.assert_called_once_with(message="Test message")

    def test_emit_channel_not_ready(self):
        self.handler.channel_ready = False
        self.handler.channel.status.return_value = False

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        self.handler.emit(record)

        self.channel.connect.assert_called_once()
        self.channel.start.assert_called_once()
        self.channel.publish.assert_called_once_with(message="Test message")

    def test_emit_channel_error(self):
        self.handler.channel_ready = True
        self.handler.channel.status.return_value = True
        self.handler.channel.publish.side_effect = Exception("Error")

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/path/to/file",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # with pytest.raises(Exception):
        self.handler.emit(record)

        self.handler.channel_ready = False
        self.handler.channel.stop.assert_called_once()