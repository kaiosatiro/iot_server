import unittest
from unittest.mock import patch, MagicMock
from src.queues.channels import RpcChannel

class TestRpcChannel(unittest.TestCase):
    @patch('src.queues.channels.get_queue_access')
    @patch('src.queues.channels.settings')
    @patch('logging.getLogger')
    def setUp(self, mock_getLogger, mock_settings, mock_get_queue_access):
        self.mock_logger = MagicMock()
        mock_getLogger.return_value = self.mock_logger
        self.mock_settings = mock_settings
        self.mock_settings.RPC_ROUTING_KEY = 'test_routing_key'
        self.mock_settings.USERAPI_ID = 'test_userapi_id'
        self.mock_settings.RPC_TIMEOUT = 3
        self.mock_connection = MagicMock()
        mock_get_queue_access.return_value = self.mock_connection
        self.rpc_channel = RpcChannel()

    def test_connect(self):
        self.rpc_channel.connect()
        self.mock_logger.info.assert_called_with("Connecting to Queue")

    def test_status(self):
        self.rpc_channel._channel = MagicMock()
        self.rpc_channel._channel.is_open = True
        self.assertTrue(self.rpc_channel.status())

        self.rpc_channel._channel.is_open = False
        self.assertFalse(self.rpc_channel.status())

    def test_stop(self):
        self.rpc_channel._channel = MagicMock()
        self.rpc_channel.stop()
        self.rpc_channel._channel.close.assert_called_once()

    def test_setup(self):
        self.rpc_channel._connection.open_channel.return_value = MagicMock()
        self.rpc_channel._connection.open_channel.return_value.queue_declare.return_value.method.queue = 'test_queue'
        self.rpc_channel.setup()
        self.assertEqual(self.rpc_channel.callback_queue, 'test_queue')
        self.mock_logger.info.assert_called_with("rpc channel setup | queue: %s", 'test_queue')

    @patch('pika.BasicProperties')
    @patch('json.dumps')
    def test_publish(self, mock_json_dumps, mock_BasicProperties):
        self.rpc_channel._connection = MagicMock()
        self.rpc_channel._channel = MagicMock()
        mock_json_dumps.return_value = '{"key": "value"}'
        self.rpc_channel.callback_queue = 'test_callback_queue'
        self.rpc_channel.publish({"method": "test_method", "device_id": "test_device"}, "test_corr_id")
        self.mock_logger.info.assert_called_with("RPC request to %s %s", "test_method", "test_device")

    def test_on_response(self):
        self.rpc_channel.corr_id = "test_corr_id"
        mock_properties = MagicMock()
        mock_properties.correlation_id = "test_corr_id"
        self.rpc_channel.on_response(None, None, mock_properties, b'test_response')
        self.assertEqual(self.rpc_channel.response, 'test_response')
