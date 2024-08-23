import unittest
from unittest.mock import patch, MagicMock
from src.queue.channels import RpcChannel


class TestRpcChannel(unittest.TestCase):
    @patch('src.queue.manager.get_queue_access')
    @patch('src.core.config.settings')
    def setUp(self, mock_settings, mock_get_queue_access):
        self.mock_settings = mock_settings
        self.mock_get_queue_access = mock_get_queue_access
        self.mock_connection = MagicMock()
        self.mock_channel = MagicMock()
        self.mock_get_queue_access.return_value = self.mock_connection
        self.mock_connection.open_channel.return_value = self.mock_channel
        self.mock_channel.queue_declare.return_value.method.queue = 'callback_queue'
        self.rpc_channel = RpcChannel()

    def test_init(self):
        self.assertIsNotNone(self.rpc_channel._connection)
        self.assertEqual(self.rpc_channel.callback_queue, 'callback_queue')

    def test_connect(self):
        self.rpc_channel.connect()
        self.mock_get_queue_access.assert_called_once()

    def test_status_open(self):
        self.mock_channel.is_open = True
        self.assertTrue(self.rpc_channel.status())

    def test_status_closed(self):
        self.mock_channel.is_open = False
        self.assertFalse(self.rpc_channel.status())

    def test_stop(self):
        self.rpc_channel.stop()
        self.mock_channel.close.assert_called_once()

    def test_setup(self):
        self.rpc_channel.setup()
        self.mock_channel.queue_declare.assert_called_with(queue='', exclusive=True)
        self.mock_channel.basic_consume.assert_called_with(
            queue='callback_queue',
            on_message_callback=self.rpc_channel.on_response,
            auto_ack=True
        )

    @patch('pika.BasicProperties')
    @patch('json.dumps')
    def test_publish(self, mock_json_dumps, mock_basic_properties):
        mock_json_dumps.return_value = '{"method": "test", "device_id": "123"}'
        self.mock_settings.RPC_TIMEOUT = 3
        self.mock_settings.USERAPI_ID = 'userapi_id'
        self.mock_settings.RPC_ROUTING_KEY = 'routing_key'
        
        response = self.rpc_channel.publish({"method": "test", "device_id": "123"}, "corr_id")
        
        self.assertIsNone(response)

    def test_on_response(self):
        self.rpc_channel.corr_id = "corr_id"
        mock_properties = MagicMock()
        mock_properties.correlation_id = "corr_id"
        self.rpc_channel.on_response(None, None, mock_properties, b'response')
        self.assertEqual(self.rpc_channel.response, 'response')
