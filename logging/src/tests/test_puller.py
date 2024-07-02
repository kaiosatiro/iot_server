import unittest
from unittest.mock import MagicMock
from puller import puller

class TestPuller(unittest.TestCase):
    def test_puller(self):
        # Create a mock message handler
        msg_handler = MagicMock()

        # Call the puller function
        puller(msg_handler)

        # Assert that the handle_message method of the message handler was called
        msg_handler.handle_message.assert_called_once()

if __name__ == '__main__':
    unittest.main()