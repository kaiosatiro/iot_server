from unittest.mock import Mock

from src.publishers.channels import MessageChannel
from src.message_handler import MessageHandler


class TestMessageHandler:
    def test_process_message(self):
        message_handler = MessageHandler()
        message_handler._channel = Mock(MessageChannel)
        message_handler.process_message(1, {"message": "Hello!"})

        message_handler._channel.publish_message.assert_called_once_with(
            {"device_id": 1, "request_id": ""},
            {"message": "Hello!"},
            content_type="application/json"
        )
