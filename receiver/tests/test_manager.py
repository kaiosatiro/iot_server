# This tests need to run with a RabbitMQ server running
import pytest

from src.publishers.manager import get_queue_access, PublishingManager


class TestPublisherManager:
    @pytest.fixture(autouse=True, scope='class')
    def conn(self) -> PublishingManager:
        pm = get_queue_access()
        return pm
        
    def test_singleton_instance(self) -> None:
        pm = get_queue_access()
        dm = get_queue_access()
        am = get_queue_access()

        assert pm is dm is am, "All instances should be the same"
        assert id(pm) == id(dm) == id(am), "All instances should be the same"

    def test_connection_status(self, conn: PublishingManager) -> None:
        assert conn.status(), "Connection should be open"

    def test_open_channel(self, conn: PublishingManager) -> None:
        channel = conn.open_channel("test")
        assert channel.is_open, "Channel should be open"
