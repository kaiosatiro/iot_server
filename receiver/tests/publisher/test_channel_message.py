# This tests need to run with a RabbitMQ server running
from unittest.mock import MagicMock

import pytest

from src.queues.channels import MessageChannel


class TestMessagePublisher:
    @pytest.fixture(autouse=True)
    def channelfix(self) -> MessageChannel:
        self.channel = MessageChannel()

    def test_configure_channel(self) -> None:
        assert self.channel.status(), "Channel should be open"

    # @pytest.mark.asyncio
    def test_publish(self):
        message_channel = MessageChannel()
        message_channel._connection.publish = MagicMock()
        message_channel.publish("Hello!", correlation_id="f9g80asd7fg", content_type="text/plain")
        message_channel._connection.publish.assert_called_once_with(
            message_channel._channel.basic_publish(
                exchange=message_channel._exchange,
                routing_key=message_channel._routing_key,
                body="Hello!",
                properties=MagicMock(),
                mandatory=True,
            )
        )
