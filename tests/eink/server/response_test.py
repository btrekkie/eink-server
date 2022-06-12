import unittest

from eink.image import Palette
from eink.image.image_data import ImageData
from eink.server.response import Response
from eink.server import Server
from eink.server.server_io import ServerIO
from PIL import Image


class ResponseTest(unittest.TestCase):
    """Tests the ``Response`` class."""

    def test_to_from_bytes(self):
        """Test ``Response.to_bytes()`` and ``Response.create_from_bytes``."""
        image = Image.new('L', (20, 20), 255)
        image_data = ImageData.render_png(image, Palette.THREE_BIT_GRAYSCALE)
        response = Response(
            image_data, [100, 500, 1000, Server._INT_MAX],
            ServerIO.image_id('mountain'), 700)
        result = Response.create_from_bytes(response.to_bytes())
        self.assertEqual(image_data, result.image_data)
        self.assertEqual(
            [100, 500, 1000, Server._INT_MAX], result.request_times_ds)
        self.assertEqual(ServerIO.image_id('mountain'), result.screensaver_id)
        self.assertEqual(700, result.screensaver_time_ds)
