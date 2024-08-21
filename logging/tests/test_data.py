from unittest.mock import patch
from os import environ

from src.core.data import LocalData


def test_LocalData_save_method_with_LOG_INFO_LOCAL_PATH():
    data = "test_data"
    origin = "test_origin"
    test_path = "/custom/path/"
    environ["LOG_INFO_LOCAL_PATH"] = test_path
    local_data = LocalData()
    with patch.object(LocalData, "save", return_value=None) as mock_save:
        local_data.save(data, origin=origin)
        mock_save.assert_called_with(data, origin=origin)
    del environ["LOG_INFO_LOCAL_PATH"]


def test_LocalData_save_method_without_LOG_INFO_LOCAL_PATH():
    data = "test_data"
    origin = "test_origin"
    local_data = LocalData()
    with patch.object(LocalData, "save", return_value=None) as mock_save:
        local_data.save(data, origin=origin)
        mock_save.assert_called_with(data, origin=origin)


def test_LocalData_set_origin_method():
    local_data = LocalData()
    origin = "test_origin"
    local_data.set_origin(origin)
    assert local_data.origin == origin, "origin should be set to the provided value"
