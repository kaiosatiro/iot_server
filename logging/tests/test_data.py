import pytest
from unittest.mock import patch, mock_open
from src.data import DataManager, LocalData, RemoteData, get_db_manager
from os import environ
from datetime import datetime


def test_data_manager_factory_methods():
    manager = DataManager()
    assert isinstance(manager.get_local(), LocalData), "get_local should return an instance of LocalData"
    assert isinstance(manager.get_remote(), RemoteData), "get_remote should return an instance of RemoteData"


def test_get_db_manager():
    assert isinstance(get_db_manager(), DataManager), "get_db_manager should return an instance of DataManager"


def test_LocalData_path_dir_method():
    test_path = "/custom/path/"
    environ["LOG_INFO_LOCAL_PATH"] = test_path
    local_data = LocalData()
    assert local_data.path == test_path, "path should be set to LOG_INFO_LOCAL_PATH"

    del environ["LOG_INFO_LOCAL_PATH"]
    local_data = LocalData()
    assert local_data.path == "/tmp/", "path should be set to /tmp/"


def test_LocalSaver_save_method_with_LOG_INFO_LOCAL_PATH():
    data = "test_data"
    origin = "test_origin"
    test_path = "/custom/path/"
    environ["LOG_INFO_LOCAL_PATH"] = test_path
    local_saver = LocalData()
    with patch.object(LocalData, 'save', return_value=None) as mock_save:
        local_saver.save(data, origin=origin)
        mock_save.assert_called_with(data, origin=origin)
    del environ["LOG_INFO_LOCAL_PATH"]


def test_LocalSaver_save_method_without_LOG_INFO_LOCAL_PATH():
    data = "test_data"
    origin = "test_origin"
    local_saver = LocalData()
    with patch.object(LocalData, 'save', return_value=None) as mock_save:
        local_saver.save(data, origin=origin)
        mock_save.assert_called_with(data, origin=origin)


@pytest.fixture
def mock_file():
    with patch("builtins.open", new_callable=mock_open) as mock_file:
        yield mock_file


def test_LocalData_save_method_with_different_file_name(mock_file):
    data = "test_data"
    origin = "test_origin"
    test_path = "/custom/path/"
    environ["LOG_INFO_LOCAL_PATH"] = test_path
    local_data = LocalData(origin=origin)

    current_date = datetime.now().strftime("%Y-%m-%d")

    local_data.save(data)

    expected_file_name = f"{test_path}{current_date}_{origin}.log"

    mock_file.assert_called_once_with(expected_file_name, "a")
    del environ["LOG_INFO_LOCAL_PATH"]


def test_LocalData_set_current_date_method():
    local_data = LocalData()
    local_data.set_current_date()
    assert local_data.current_date == datetime.now().strftime("%Y-%m-%d"), "current_date should be updated to the current date"


def test_LocalData_set_origin_method():
    local_data = LocalData()
    origin = "test_origin"
    local_data.set_origin(origin)
    assert local_data.origin == origin, "origin should be set to the provided value"  # Test LocalData.save method
