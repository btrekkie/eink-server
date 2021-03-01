import io
import unittest

from eink.server.server_io import ServerIO


class ServerIOTest(unittest.TestCase):
    """Tests the ``ServerIO`` class."""

    def _check_read_write_int(self, value):
        """Test writing and then reading the specified integer."""
        output = io.BytesIO()
        ServerIO.write_int(output, value)
        input_ = io.BytesIO(output.getvalue())
        self.assertEqual(value, ServerIO.read_int(input_))

    def test_read_write_int(self):
        """Test ``ServerIO.read_int`` and ``ServerIO.write_int``."""
        self._check_read_write_int(73)
        self._check_read_write_int(0)
        self._check_read_write_int(-58)
        self._check_read_write_int(1234567890)
        self._check_read_write_int(-1098765432)
        self._check_read_write_int(2 ** 31 - 1)
        self._check_read_write_int(-2 ** 31)

    def _check_read_write_bytes(self, bytes_):
        """Test writing and then reading the specified ``bytes``.

        Test writing and then reading the specified ``bytes`` using
        ``ServerIO.write_bytes`` and ``ServerIO.read_bytes``.
        """
        output = io.BytesIO()
        ServerIO.write_bytes(output, bytes_)
        input_ = io.BytesIO(output.getvalue())
        self.assertEqual(bytes_, ServerIO.read_bytes(input_))

    def test_read_write_bytes(self):
        """Test ``ServerIO.read_bytes`` and ``ServerIO.write_bytes``."""
        self._check_read_write_bytes(b'')
        self._check_read_write_bytes(b'Hello, world!')
        self._check_read_write_bytes(b'\x2a' * 1000)
        self._check_read_write_bytes(b'\x00' * 1000)

    def _check_image_id(self, image_id):
        """Assert that the specified value is a valid image ID."""
        self.assertIsInstance(image_id, bytes)
        self.assertEqual(ServerIO.STATUS_IMAGE_ID_LENGTH, len(image_id))

    def test_image_id(self):
        """Test ``ServerIO.image_id``."""
        self._check_image_id(ServerIO.image_id('mountain'))
        self._check_image_id(ServerIO.image_id(''))
        self._check_image_id(ServerIO.image_id('foo \u00e9 bar'))
        self._check_image_id(ServerIO.image_id(' ' * 1000))
