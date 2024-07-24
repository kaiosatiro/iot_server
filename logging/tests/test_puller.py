import pytest
from unittest.mock import patch, MagicMock


class MockHandler:
    def handle_message(self, body, properties):
        pass


@pytest.fixture
def mock_handler():
    return MockHandler()


@pytest.fixture
def mock_pika():
    with patch('puller.pika') as mock:
        mock.BlockingConnection.return_value = MagicMock()
        yield mock

# def test_puller_connects_to_rabbitmq(mock_pika, mock_handler):
#     puller(mock_handler)
#     mock_pika.BlockingConnection.assert_called_once_with(
#         pika.ConnectionParameters(
#             host='rabbitmq', port=5672,
#             credentials=pika.PlainCredentials('guest', 'guest')
#         )
#     )

# def test_puller_handles_message(mock_pika, mock_handler):
#     connection_mock = mock_pika.BlockingConnection.return_value
#     channel_mock = connection_mock.channel.return_value
#     channel_mock.basic_consume.assert_called_once()
#     consume_callback = channel_mock.basic_consume.call_args[0][0]
#     consume_callback(channel_mock, MagicMock(), MagicMock(), b'test message')
#     assert mock_handler.handle_message.call_count == 1
#     args, _ = mock_handler.handle_message.call_args
#     assert args[0] == b'test message'

# def test_puller_acknowledges_message(mock_pika, mock_handler):
#     connection_mock = mock_pika.BlockingConnection.return_value
#     channel_mock = connection_mock.channel.return_value
#     channel_mock.basic_consume.assert_called_once()
#     consume_callback = channel_mock.basic_consume.call_args[0][0]
#     method_mock = MagicMock()
#     consume_callback(channel_mock, method_mock, MagicMock(), b'test message')
#     channel_mock.basic_ack.assert_called_once_with(delivery_tag=method_mock.delivery_tag)
