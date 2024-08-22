import json
from logging import Logger
from unittest.mock import MagicMock

from src.core.database.db import DB
from src.core.message_handlers import Message_Handler


def test_handle_message_with_existing_device_id():
    body = json.dumps({
        "device_id": 123,
        "data": {
            "temperature": 22.5,
            "humidity": 45
        }
    }).encode("utf-8")
    db_mock = MagicMock(spec=DB)
    db_mock.verify_device_id.return_value = True
    handler = Message_Handler()
    handler.db = db_mock

    handler.handle_message(body, corr_id="abc")

    db_mock.verify_device_id.assert_called_once_with(123)
    db_mock.save_message.assert_called_once()


def test_handle_message_with_non_existing_device_id():
    body = json.dumps({
        "device_id": 123,
        "data": {
            "temperature": 22.5,
            "humidity": 45
        }
    }).encode("utf-8")
    db_mock = MagicMock(spec=DB)
    db_mock.verify_device_id.return_value = False
    handler = Message_Handler()
    handler.db = db_mock
    handler.logger = MagicMock(spec=Logger)

    handler.handle_message(body, corr_id="abc")

    db_mock.verify_device_id.assert_called_once_with(123)
    db_mock.save_message.assert_not_called()
    handler.logger.info.assert_called_once_with("Handling message from device: %s", 123, extra={"corrid": "abc"})
    handler.logger.warning.assert_called_once_with("Device ID not found", extra={"corrid": "abc"})


def test_handle_message_with_invalid_body():
    body = b"invalid body"
    db_mock = MagicMock(spec=DB)
    handler = Message_Handler()
    handler.db = db_mock
    handler.logger = MagicMock(spec=Logger)

    handler.handle_message(body, corr_id="abc")

    db_mock.verify_device_id.assert_not_called()
    db_mock.save_message.assert_not_called()
    handler.logger.error.assert_called_once()


def test_close():
    db_mock = MagicMock(spec=DB)
    handler = Message_Handler()
    handler.db = db_mock
    handler.logger = MagicMock(spec=Logger)

    handler.close()

    db_mock.close.assert_called_once()
    handler.logger.info.assert_called_once_with("Message Handler closed")



def test_handle_rpc_request_add_device_to_cache():
    request = json.dumps({
        "method": "add",
        "device_id": 123
    }).encode("utf-8")
    db_mock = MagicMock(spec=DB)
    handler = Message_Handler()
    handler.db = db_mock
    handler.logger = MagicMock(spec=Logger)

    result = handler.handle_rpc_request("abc", request)

    db_mock.add_device_to_cache.assert_called_once_with(123)
    handler.logger.info.assert_called_with("Device added to cache: %s", 123, extra={"corrid": "abc"})
    assert result == "ok"


def test_handle_rpc_request_remove_device_from_cache():
    request = json.dumps({
        "method": "remove",
        "device_id": 123
    }).encode("utf-8")
    db_mock = MagicMock(spec=DB)
    handler = Message_Handler()
    handler.db = db_mock
    handler.logger = MagicMock(spec=Logger)

    result = handler.handle_rpc_request("abc", request)

    db_mock.remove_device_from_cache.assert_called_once_with(123)
    handler.logger.info.assert_called_with("Device removed from cache: %s", 123, extra={"corrid": "abc"})
    assert result == "ok"


def test_handle_rpc_request_invalid_request():
    request = b"invalid request"
    db_mock = MagicMock(spec=DB)
    handler = Message_Handler()
    handler.db = db_mock
    handler.logger = MagicMock(spec=Logger)

    result = handler.handle_rpc_request("abc", request)

    db_mock.add_device_to_cache.assert_not_called()
    db_mock.remove_device_from_cache.assert_not_called()
    handler.logger.error.assert_called_once()
    assert result == "ok"
