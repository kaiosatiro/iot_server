from unittest.mock import patch

from src.core.handlers import HandlerManager, Handler
from src.config import settings


class TestHandler:
    def test_handle_message_with_known_app_id(self):
        manager = HandlerManager()
        msg = "test_message"
        app_id = settings.HANDLER_ID
        with patch.object(
            Handler, "handle_message", return_value=None
        ) as mock_handle_message:
            manager.handle_message(msg, app_id)
            mock_handle_message.assert_called_with(msg)

    def test_handle_message_with_unknown_app_id(self):
        manager = HandlerManager()
        msg = "test_message"
        app_id = "unknown222"
        with patch.object(
            Handler, "handle_message", return_value=None
        ) as mock_handle_message:
            manager.handle_message(msg, app_id)
            mock_handle_message.assert_called_with(msg)


