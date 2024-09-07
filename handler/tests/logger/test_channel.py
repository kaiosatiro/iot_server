import unittest
from unittest.mock import patch

import pytest

from src.queues.log_connection import LogConnection


class TestLogConnection(unittest.TestCase):
    @pytest.mark.skip(reason="Need to mock the thread")
    @patch("pika.BlockingConnection")
    @patch("pika.PlainCredentials")
    @patch("pika.ConnectionParameters")
    def test_connect_success(
        self,
        mock_connection_parameters,
        mock_plain_credentials,
        mock_blocking_connection,
    ):
        log_channel = LogConnection()
        log_channel.connect()

        mock_plain_credentials.assert_called_once_with(
            log_channel._username, log_channel._password
        )
        mock_connection_parameters.assert_called_once_with(
            log_channel._host,
            log_channel._port,
            credentials=mock_plain_credentials.return_value,
            heartbeat=0,
        )
        mock_blocking_connection.assert_called_once_with(
            mock_connection_parameters.return_value
        )
        self.assertTrue(mock_blocking_connection.return_value.channel.called)

    @patch("pika.BlockingConnection")
    def test_status(self, mock_blocking_connection):
        log_channel = LogConnection()
        log_channel._connection = mock_blocking_connection.return_value

        mock_blocking_connection.return_value.is_open = True
        self.assertTrue(log_channel.status())

        mock_blocking_connection.return_value.is_open = False
        self.assertFalse(log_channel.status())

    @patch("pika.BlockingConnection")
    def test_publish(self, mock_blocking_connection):
        log_channel = LogConnection()
        log_channel._connection = mock_blocking_connection.return_value

        with patch.object(log_channel, "_publish") as mock_publish:
            log_channel.publish("test message")
            mock_blocking_connection.return_value.add_callback_threadsafe.assert_called_once()

    @patch("pika.BlockingConnection")
    def test_stop(self, mock_blocking_connection):
        log_channel = LogConnection()
        log_channel._connection = mock_blocking_connection.return_value

        log_channel.stop()
        self.assertFalse(log_channel.is_running)
        mock_blocking_connection.return_value.close.assert_called_once()
