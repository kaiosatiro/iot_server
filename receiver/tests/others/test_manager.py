# This tests need to run with a RabbitMQ server running
import pytest

from src.publishers.manager import PublishingManager


class TestPublisherManager:
    @pytest.fixture(autouse=True)
    def conn(self) -> PublishingManager:
        self.pm = PublishingManager()

    def test_connection_status(self) -> None:
        assert self.pm.status(), "Connection should be open"

    # def test_open_channel(self) -> None:
    #     self.pm = PublishingManager()
    #     channel = self.pm.open_channel("test")
    #     assert channel.is_open, "Channel should be open"
