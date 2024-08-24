import unittest
from unittest.mock import MagicMock, patch
import logging
from logging import LogRecord
from src.queues.channels import LogChannel
from src.logger.handler import LogHandler


class TestLogHandler(unittest.TestCase):
    def setUp(self):
        self.mock_channel = MagicMock(spec=LogChannel)
        self.handler = LogHandler(channel=self.mock_channel, level=logging.INFO)

    def test_initialization(self):
        self.assertEqual(self.handler.level, logging.INFO)
        self.assertEqual(self.handler.channel, self.mock_channel)
        self.assertFalse(self.handler.channel_ready)
        self.assertIsNone(self.handler.formatter)

    @patch('logging.getLogger')
    def test_setup_channel(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        self.mock_channel.status.return_value = True

        self.handler.setup_channel()

        self.mock_channel.connect.assert_called_once()
        self.mock_channel.setup.assert_called_once()
        self.assertTrue(self.handler.channel_ready)
        mock_logger.info.assert_any_call("Connecting Handler to Queue")
        mock_logger.info.assert_any_call("Handler Channel Ready")

    @patch('logging.getLogger')
    def test_emit(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        record = LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="test message", args=(), exc_info=None)
        self.mock_channel.status.return_value = True

        self.handler.emit(record)

        self.mock_channel.publish.assert_called_once_with(message=self.handler.format(record))

    @patch('logging.getLogger')
    def test_emit_with_exception(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        record = LogRecord(name="test", level=logging.INFO, pathname="", lineno=0, msg="test message", args=(), exc_info=None)
        self.mock_channel.status.side_effect = Exception("Channel error")

        self.handler.emit(record)

        self.assertFalse(self.handler.channel_ready)
        self.mock_channel.stop.assert_called_once()
