import unittest

from eink.server.request import Request


class RequestTest(unittest.TestCase):
    """Tests the ``Request`` class."""

    def test_to_from_bytes(self):
        """Test ``Request.to_bytes()`` and ``Request.create_from_bytes``."""
        self.assertIsInstance(
            Request.create_from_bytes(Request().to_bytes()), Request)
