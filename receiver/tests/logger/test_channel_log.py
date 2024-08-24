import unittest
from unittest.mock import MagicMock, patch

from pika.channel import Channel

from src.queues.channels import LogChannel
from src.queues.manager import PublishingManager
from src.config import settings


class TestLogChannel(unittest.TestCase):
    def setUp(self):
        self.mock_connection = MagicMock(spec=PublishingManager)
        self.mock_channel = MagicMock(spec=Channel)
        self.log_channel = LogChannel()
        self.log_channel._connection = self.mock_connection
        self.log_channel._channel = self.mock_channel

    @patch('src.queues.channels.get_queue_access')
    def test_connect(self, mock_get_queue_access):
        mock_get_queue_access.return_value = self.mock_connection
        self.mock_connection.open_channel.return_value = self.mock_channel

        self.log_channel.connect()

        mock_get_queue_access.assert_called_once()
        self.mock_connection.open_channel.assert_called_once_with(tag='LogChannel')
        self.assertEqual(self.log_channel._channel, self.mock_channel)

    def test_status(self):
        self.mock_channel.is_open = True
        self.assertTrue(self.log_channel.status())

        self.mock_channel.is_open = False
        self.assertFalse(self.log_channel.status())

    def test_stop(self):
        self.log_channel.stop()
        self.mock_channel.close.assert_called_once()

    def test_setup(self):
        self.log_channel.setup()
        self.mock_channel.exchange_declare.assert_called_once_with(
            exchange=self.log_channel._exchange,
            exchange_type="topic",
            durable=True,
        )
        self.mock_channel.queue_declare.assert_called_once_with(
            queue=self.log_channel._queue,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )
        self.mock_channel.queue_bind.assert_called_once_with(
            exchange=self.log_channel._exchange,
            queue=self.log_channel._queue,
            routing_key=self.log_channel._routing_key,
        )

    @patch('pika.BasicProperties')
    def test_publish(self, mock_basic_properties):
        message = "test message"
        content_type = "text/plain"
        mock_properties = MagicMock()
        mock_basic_properties.return_value = mock_properties

        self.log_channel.publish(message, content_type)

        mock_basic_properties.assert_called_once_with(
            app_id=settings.RECEIVER_ID,
            content_type=content_type,
            delivery_mode=2,
        )
        self.mock_channel.basic_publish.assert_called_once_with(
            exchange=self.log_channel._exchange,
            routing_key=self.log_channel._routing_key,
            body=message,
            properties=mock_properties,
            mandatory=True,
        )
