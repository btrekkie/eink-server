import io
import random
import unittest

from PIL import Image

from eink.image import EinkGraphics
from eink.image import Palette
from eink.image.image_data import ImageData


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

        image2 = image1.convert('RGB')
        image_data2 = ImageData.render_jpeg(image2, 20)
        Image.open(io.BytesIO(image_data2))

    def _check_render_png_image(self, image, palette):
        """Test ``ImageData.render_png(image, palette)``."""
        image_data = ImageData.render_png(image, palette)
        result = Image.open(io.BytesIO(image_data))
        self.assertEqual(image.size, result.size)
        self.assertFalse(EinkGraphics._has_alpha(result))
        self.assertEqual(
            list(image.convert('RGB').getdata()),
            list(result.convert('RGB').getdata()))

    def _check_render_png(self, palette):
        """Test ``ImageData.render_png`` with the specified ``Palette``."""
        rng = random.Random(-60722682)
        pixels1 = list(palette._colors)
        for _ in range(400 - len(palette._colors)):
            pixels1.append(rng.choice(palette._colors))
        image1 = Image.new('RGB', (20, 20))
        image1.putdata(pixels1)
        self._check_render_png_image(image1, palette)

        if palette._is_grayscale:
            pixels2 = list(pixel[0] for pixel in pixels1)
            image2 = Image.new('L', (20, 20))
            image2.putdata(pixels2)
            self._check_render_png_image(image2, palette)

        color = palette._colors[len(palette._colors) // 2]
        image3 = Image.new('RGB', (100, 100), color)
        self._check_render_png_image(image3, palette)

    def test_render_png(self):
        """Test ``ImageData.render_png``."""
        self._check_render_png(Palette.THREE_BIT_GRAYSCALE)
        self._check_render_png(Palette.MONOCHROME)
        self._check_render_png(Palette.SEVEN_COLOR)
