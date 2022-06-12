import io
import unittest

from eink.image import Palette
from eink.image.image_data import ImageData
from PIL import Image


class ImageDataTest(unittest.TestCase):
    """Tests the ``ImageData`` class."""

    def test_render_jpeg(self):
        """Test ``ImageData.render_jpeg``."""
        # Test that the following doesn't raise
        pixels1 = [0, 36, 73, 109, 146, 182, 219, 255]
        image1 = Image.new('L', (4, 2))
        image1.putdata(pixels1)
        image_data1 = ImageData.render_jpeg(image1, 90)
        Image.open(io.BytesIO(image_data1))

        pixels2 = list([(color, color, color) for color in pixels1])
        image2 = Image.new('RGB', (4, 2))
        image2.putdata(pixels2)
        image_data2 = ImageData.render_jpeg(image2, 20)
        Image.open(io.BytesIO(image_data2))

    def test_render_png_grayscale(self):
        """Test ``ImageData.render_png`` with ``Palette.THREE_BIT_GRAYSCALE``.
        """
        pixels1 = [0, 36, 73, 109, 146, 182, 219, 255]
        image1 = Image.new('L', (4, 2))
        image1.putdata(pixels1)
        image_data1 = ImageData.render_png(image1, Palette.THREE_BIT_GRAYSCALE)
        result1 = Image.open(io.BytesIO(image_data1))
        self.assertEqual(pixels1, list(result1.convert('L').getdata()))

        pixels2 = list([(color, color, color) for color in pixels1])
        image2 = Image.new('RGB', (4, 2))
        image2.putdata(pixels2)
        image_data2 = ImageData.render_png(
            image2, Palette.THREE_BIT_GRAYSCALE, True)
        result2 = Image.open(io.BytesIO(image_data2))
        self.assertEqual(pixels1, list(result2.convert('L').getdata()))

        image3 = Image.new('L', (100, 100), 73)
        image_data3 = ImageData.render_png(image3, Palette.THREE_BIT_GRAYSCALE)
        result3 = Image.open(io.BytesIO(image_data3))
        self.assertEqual([73] * 10000, list(result3.convert('L').getdata()))

    def test_render_png_monochrome(self):
        """Test ``ImageData.render_png`` with ``Palette.MONOCHROME``."""
        pixels1 = [0, 255]
        image1 = Image.new('L', (1, 2))
        image1.putdata(pixels1)
        image_data1 = ImageData.render_png(image1, Palette.MONOCHROME)
        result1 = Image.open(io.BytesIO(image_data1))
        self.assertEqual(pixels1, list(result1.convert('L').getdata()))

        pixels2 = list([(color, color, color) for color in pixels1])
        image2 = Image.new('RGB', (1, 2))
        image2.putdata(pixels2)
        image_data2 = ImageData.render_png(image2, Palette.MONOCHROME, True)
        result2 = Image.open(io.BytesIO(image_data2))
        self.assertEqual(pixels1, list(result2.convert('L').getdata()))

        image3 = Image.new('L', (100, 100), 255)
        image_data3 = ImageData.render_png(image3, Palette.MONOCHROME)
        result3 = Image.open(io.BytesIO(image_data3))
        self.assertEqual([255] * 10000, list(result3.convert('L').getdata()))
