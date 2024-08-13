# This tests need to run with a RabbitMQ server running
import pytest

from src.publishers.channels import LogChannel, get_log_channel


class TestLogPublisher:
    @pytest.fixture(autouse=True)
    def channelfix(self) -> LogChannel:
        self.channel = get_log_channel()

    def test_configure_channel(self) -> None:
        self.channel.configure('logs', '', 'log.receiver', True)
        assert self.channel.status(), "Channel should be open"

    def test_publish_message(self) -> None:
        self.channel.configure('logs', '', 'log.receiver', True)
        self.channel.publish_message('This is a test message from TestLogPublisher')
        assert self.channel.status(), "Channel should be open"
