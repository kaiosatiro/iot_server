# The tests in the FIRST class need to run with a RabbitMQ server running.
# On the other hand, the tests in the SECOND class are Mocked.
import logging
from logging import LogRecord
from unittest.mock import MagicMock

import pytest

from src.logger.handler import LogHandler
from src.publishers.abs import ABSQueueChannel
from src.publishers.channels import LogChannel
from src.logger.handler import LogHandler


class TestLogHandler:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.handler = LogHandler(
            channel=LogChannel(),
            level=0,
            formatter=None,
            exchange='logs',
            queue='logs',
            routing_key=None,
            content_type='text/plain',
            declare_exchange=True
            )

    def test_handler_channel(self):
        assert isinstance(self.handler.channel, ABSQueueChannel)
        assert self.handler.channel.status()
    
    def test_emission(self):
        try:
            self.handler.emit(LogRecord(
                name='test',
                level=0,
                pathname='test.py',
                lineno=1,
                msg='test',
                args=None,
                exc_info=None
            ))
        except Exception as e:
            assert None, "Emission failed"
        finally:
            assert True, "Emission successful"


class TestLogHandlerB:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.channel = MagicMock()
        self.handler = LogHandler(
            channel=self.channel,
            level=logging.NOTSET,
            formatter=None,
            exchange='logs',
            queue='logs',
            routing_key=None,
            content_type='text/plain',
            declare_exchange=True
        )

    def test_emit_calls_setup_channel_if_channel_not_ready(self):
        self.channel.status.return_value = False
        self.handler.setup_channel = MagicMock()

        record = logging.LogRecord(
            name='test',
            level=0,
            pathname='test.py',
            lineno=1,
            msg='test',
            args=None,
            exc_info=None
        )

        self.handler.emit(record)

        self.handler.setup_channel.assert_called_once()

    def test_emit_calls_publish_message_with_formatted_record(self):
        self.channel.status.return_value = True
        self.handler.format = MagicMock(return_value='formatted')
        self.handler.channel.publish_message = MagicMock()

        record = logging.LogRecord(
            name='test',
            level=0,
            pathname='test.py',
            lineno=1,
            msg='test',
            args=None,
            exc_info=None
        )

        self.handler.emit(record)

        self.handler.format.assert_called_once_with(record)
        self.handler.channel.publish_message.assert_called_once_with(message='formatted')

    def test_emit_handles_exception_and_calls_handle_error(self):
        self.channel.status.return_value = True
        self.handler.format = MagicMock(side_effect=Exception)
        self.handler.handleError = MagicMock()

        record = logging.LogRecord(
            name='test',
            level=0,
            pathname='test.py',
            lineno=1,
            msg='test',
            args=None,
            exc_info=None
        )

        self.handler.emit(record)

        self.handler.handleError.assert_called_once_with(record)
