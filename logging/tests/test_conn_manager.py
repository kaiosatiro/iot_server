import pytest
from unittest.mock import patch, MagicMock

from src.core.manager import ConnectionManager


@pytest.fixture
def connection_manager():
    return ConnectionManager()


@pytest.mark.skip
def test_connection_manager_connect(connection_manager):
    with patch('src.core.manager.SelectConnection') as mock_select_connection:
        connection_manager.connect()
        mock_select_connection.assert_called_once_with(
            connection_manager.parameters,
            on_open_callback=connection_manager.on_connection_open,
            on_open_error_callback=connection_manager.on_connection_open_error,
            on_close_callback=connection_manager.on_connection_closed,
        )


def test_connection_manager_on_connection_open(connection_manager):
    with patch('src.core.manager.ConnectionManager.open_channel') as mock_open_channel:
        connection_manager.on_connection_open(MagicMock())
        mock_open_channel.assert_called_once()


def test_connection_manager_on_connection_open_error(connection_manager):
    with patch('src.core.manager.ConnectionManager.reconnect') as mock_reconnect:
        connection_manager.on_connection_open_error(MagicMock(), Exception())
        mock_reconnect.assert_called_once()


def test_connection_manager_on_connection_closed(connection_manager):
    with patch('src.core.manager.ConnectionManager.reconnect') as mock_reconnect:
        connection_manager.on_connection_closed(MagicMock(), Exception())
        mock_reconnect.assert_called_once()


def test_connection_manager_reconnect(connection_manager):
    connection_manager.stop = MagicMock()
    connection_manager.reconnect()
    assert connection_manager.should_reconnect is True
    connection_manager.stop.assert_called_once()


@pytest.mark.skip
def test_connection_manager_open_channel(connection_manager):
    with patch('src.core.manager.ConnectionManager.on_channel_open') as mock_on_channel_open:
        connection_manager.open_channel()
        connection_manager._connection.channel.assert_called_once_with(
            on_open_callback=mock_on_channel_open
        )


def test_connection_manager_on_channel_open(connection_manager):
    with patch('src.core.manager.ConnectionManager.setup_exchange') as mock_setup_exchange:
        connection_manager.on_channel_open(MagicMock())
        mock_setup_exchange.assert_called_once()


def test_connection_manager_on_channel_closed(connection_manager):
    with patch('src.core.manager.ConnectionManager.close_connection') as mock_close_connection:
        connection_manager.on_channel_closed(MagicMock(), Exception())
        mock_close_connection.assert_called_once()


def test_connection_manager_setup_exchange(connection_manager):
    with patch('src.core.manager.ConnectionManager.on_exchange_declareok') as mock_on_exchange_declareok:
        connection_manager.setup_exchange()
        connection_manager._channel.exchange_declare.assert_called_once_with(
            exchange=connection_manager.EXCHANGE,
            exchange_type=connection_manager.EXCHANGE_TYPE,
            durable=True,
            callback=mock_on_exchange_declareok,
        )


def test_connection_manager_on_exchange_declareok(connection_manager):
    with patch('src.core.manager.ConnectionManager.setup_queue') as mock_setup_queue:
        connection_manager.on_exchange_declareok(MagicMock())
        mock_setup_queue.assert_called_once()


def test_connection_manager_setup_queue(connection_manager):
    with patch('src.core.manager.ConnectionManager.on_queue_declareok') as mock_on_queue_declareok:
        connection_manager.setup_queue()
        connection_manager._channel.queue_declare.assert_called_once_with(
            queue=connection_manager.QUEUE,
            durable=True,
            callback=mock_on_queue_declareok,
        )


def test_connection_manager_on_queue_declareok(connection_manager):
    with patch('src.core.manager.ConnectionManager.on_bindok') as mock_on_bindok:
        connection_manager.on_queue_declareok(MagicMock())
        connection_manager._channel.queue_bind.assert_called_once_with(
            exchange=connection_manager.EXCHANGE,
            queue=connection_manager.QUEUE,
            routing_key=connection_manager.ROUTING_KEY,
            callback=mock_on_bindok,
        )


def test_connection_manager_on_bindok(connection_manager):
    with patch('src.core.manager.ConnectionManager.on_basic_qos_ok') as mock_on_basic_qos_ok:
        connection_manager.on_bindok(MagicMock())
        connection_manager._channel.basic_qos.assert_called_once_with(
            prefetch_count=connection_manager._prefetch_count,
            callback=mock_on_basic_qos_ok,
        )


def test_connection_manager_on_basic_qos_ok(connection_manager):
    with patch('src.core.manager.ConnectionManager.start_consuming') as mock_start_consuming:
        connection_manager.on_basic_qos_ok(MagicMock())
        mock_start_consuming.assert_called_once()


def test_connection_manager_start_consuming(connection_manager):
    with patch('src.core.manager.ConnectionManager.on_consumer_cancelled') as mock_on_consumer_cancelled:
        with patch('src.core.manager.ConnectionManager.on_message') as mock_on_message:
            connection_manager.start_consuming()
            connection_manager._channel.add_on_cancel_callback.assert_called_once_with(
                mock_on_consumer_cancelled
            )
            connection_manager._channel.basic_consume.assert_called_once_with(
                queue=connection_manager.QUEUE,
                on_message_callback=mock_on_message,
            )


@pytest.mark.skip
def test_connection_manager_on_consumer_cancelled(connection_manager):
    with patch('src.core.manager.ConnectionManager.close_connection') as mock_close_connection:
        connection_manager.on_consumer_cancelled(MagicMock())
        mock_close_connection.assert_called_once()


@pytest.mark.skip
def test_connection_manager_on_message(connection_manager):
    with patch('src.core.manager.ConnectionManager.logger') as mock_logger:
        connection_manager.on_message(MagicMock(), MagicMock(), MagicMock(), MagicMock())
        connection_manager._channel.basic_ack.assert_called_once()
        mock_logger.info.assert_called_once()


@pytest.mark.skip
def test_connection_manager_stop(connection_manager):
    connection_manager.stop_consuming = MagicMock()
    connection_manager._connection.ioloop.start = MagicMock()
    connection_manager._connection.ioloop.stop = MagicMock()
    connection_manager.stop()
    assert connection_manager._closing is True
    connection_manager.stop_consuming.assert_called_once()
    connection_manager._connection.ioloop.start.assert_called_once()
    connection_manager._connection.ioloop.stop.assert_called_once()


def test_connection_manager_stop_consuming(connection_manager):
    with patch('src.core.manager.ConnectionManager.on_cancelok') as mock_on_cancelok:
        connection_manager.stop_consuming()
        connection_manager._channel.basic_cancel.assert_called_once_with(
            connection_manager._consumer_tag,
            callback=mock_on_cancelok,
        )


def test_connection_manager_on_cancelok(connection_manager):
    connection_manager._channel.close = MagicMock()
    connection_manager.on_cancelok(MagicMock())
    assert connection_manager._consuming is False
    connection_manager._channel.close.assert_called_once()


@pytest.mark.skip
def test_connection_manager_run(connection_manager):
    connection_manager.connect = MagicMock()
    connection_manager._connection.ioloop.start = MagicMock()
    connection_manager.run()
    connection_manager.connect.assert_called_once()
    connection_manager._connection.ioloop.start.assert_called_once()
