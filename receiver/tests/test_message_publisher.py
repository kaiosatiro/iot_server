# This tests need to run with a RabbitMQ server running
from unittest.mock import MagicMock

import pytest

from src.publishers.channels import MessageChannel, get_message_channel


class TestMessagePublisher:
    @pytest.fixture(autouse=True, scope='class')
    def channel(self) -> MessageChannel:
        ch = get_message_channel()
        return ch
        
    def test_singleton_instance(self) -> None:
        cha = get_message_channel()
        chb = get_message_channel()
        chc = get_message_channel()

        assert cha is chb is chc, "All instances should be the same"
        assert id(cha) == id(chb) == id(chc), "All instances should be the same"
    
    def test_configure_channel(self, channel: MessageChannel) -> None:
        assert channel.status(), "Channel should be open"
    
    def test_publish_message(self, channel: MessageChannel) -> None:
        # channel.configure('logs', 'logs', 'logs.receiver', True)
        channel.publish_message('This is a test message from TestMessagePublisher')
        assert channel.status(), "Channel should be open"

    def test_publish_messageB(self):
        message_channel = MessageChannel()
        message_channel._connection.publish = MagicMock()
        message_channel.publish_message("Hello!")
        message_channel._connection.publish.assert_called_once_with(
            message_channel._channel.basic_publish(
                exchange=message_channel._exchange,
                routing_key=message_channel._routing_key,
                body="Hello!",
                properties=MagicMock(),
                mandatory=True,
            )
        )