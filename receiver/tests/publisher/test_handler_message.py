from unittest.mock import Mock

from src.queues.channels import MessageChannel
from src.message_handler import MessageHandler


class TestMessageHandler:
    def test_process_message(self):
        message_handler = MessageHandler()
        message_handler._channel = Mock(spec=MessageChannel)
        message_handler.process_message(1, {"message": "Hello!"})

        message_handler._channel.publish.assert_called_with(
            {'message': 'Hello!', 'device_id': 1},
            correlation_id='',
            content_type='application/json'
            )
