# This tests need to run with a RabbitMQ server running

from time import sleep

import pytest

from src.core.publisher import get_queue_access, ABSQueueChannel


class TestPublisherManager:
    @pytest.fixture(autouse=True)
    def conn(self) -> ABSQueueChannel:
        pm = get_queue_access()
        sleep(5)
        return pm
        
    def test_singleton_instance(self) -> None:
        pm = get_queue_access()
        dm = get_queue_access()
        am = get_queue_access()

        assert pm is dm is am, "All instances should be the same"
        assert id(pm) == id(dm) == id(am), "All instances should be the same"

    def test_connection_status(self, conn: ABSQueueChannel) -> None:
        assert conn.get_connection_status(), "Connection should be open"

    def test_open_channel(self, conn: ABSQueueChannel) -> None:
        channel = conn.open_channel("test")
        assert channel.is_opening, "Channel should be open"
        sleep(5)
        assert channel.is_open, "Channel should be open"
    
    def test_close_connection(self, conn: ABSQueueChannel) -> None:
        conn.close_connection()
        sleep(5)
        assert not conn.get_connection_status(), "Connection should be closed"