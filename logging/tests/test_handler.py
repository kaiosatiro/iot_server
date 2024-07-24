import pytest
from unittest.mock import MagicMock
from src.handler import HandlerManager
from src.data import DBManager, DB


@pytest.fixture
def mock_db_manager():
    mock_manager = MagicMock(spec=DBManager)
    mock_manager.get_local.return_value = MagicMock(spec=DB)
    # mock_manager.get_remote.return_value = MagicMock(spec=DB)
    return mock_manager


def test_handler_manager_initialization(mock_db_manager):
    handler_manager = HandlerManager(db_manager=mock_db_manager)
    assert handler_manager.db_manager is mock_db_manager


# def test_handler_manager_initialization_failure():
#     with pytest.raises(ValueError) as exc_info:
#         handler_manager = HandlerManager(db_manager=None)
#     assert "DBManager object is required" in str(exc_info.value)


def test_handler_manager_registers_handlers_correctly(mock_db_manager):
    handler_manager = HandlerManager(db_manager=mock_db_manager)
    assert "logs_iot" in handler_manager.handlers  # TODO: rethink strongly cople with the src code!
    assert handler_manager.handlers["logs_iot"].db_local is mock_db_manager.get_local()
