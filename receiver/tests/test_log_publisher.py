# This tests need to run with a RabbitMQ server running
import pytest

from src.publishers.channels import LogChannel, get_log_channel


class TestLogPublisher:
    @pytest.fixture(autouse=True, scope='class')
    def channel(self) -> LogChannel:
        ch = get_log_channel()
        return ch
        
    def test_singleton_instance(self) -> None:
        cha = get_log_channel()
        chb = get_log_channel()
        chc = get_log_channel()

        assert cha is chb is chc, "All instances should be the same"
        assert id(cha) == id(chb) == id(chc), "All instances should be the same"
    
    def test_configure_channel(self, channel: LogChannel) -> None:
        channel.configure('logs', '', 'log.receiver', True)
        assert channel.status(), "Channel should be open"
    
    def test_publish_message(self, channel: LogChannel) -> None:
        channel.configure('logs', '', 'log.receiver', True)
        channel.publish_message('This is a test message from TestLogPublisher')
        assert channel.status(), "Channel should be open"
