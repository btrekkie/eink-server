import unittest

from eink.image import EinkGraphics
from eink.image import Palette
from PIL import Image


class EinkGraphicsTest(unittest.TestCase):
    """Tests the ``EinkGraphics`` class."""

    def _check_pixels(self, expected_pixels, actual_pixels):
        """Check whether ``actual_pixels`` matches ``expected_pixels``.

        Check whether the pixels in ``actual_pixels`` match those in
        ``expected_pixels``. We say they match if ``actual_pixels[i] in
        expected_pixels[i]`` for all ``i``.
        """
        self.assertEqual(len(expected_pixels), len(actual_pixels))
        for expected_pixel, actual_pixel in (
                zip(expected_pixels, actual_pixels)):
            self.assertIn(actual_pixel, expected_pixel)

    def test_round_grayscale(self):
        """Test ``EinkGraphics.round`` with ``Palette.THREE_BIT_GRAYSCALE``."""
        pixels1 = list(range(256))
        image1 = Image.new('L', (16, 16))
        image1.putdata(pixels1)
        result1 = EinkGraphics.round(image1)
        expected_pixels = (
            ([[0]] * 18) + [[0, 1]] + ([[36]] * 36) + ([[73]] * 36) +
            [[73, 109]] + ([[109]] * 36) + ([[146]] * 36) + [[146, 182]] +
            ([[182]] * 36) + ([[219]] * 36) + [[219, 255]] + ([[255]] * 18))
        self._check_pixels(
            expected_pixels, list(result1.convert('L').getdata()))

        pixels2 = list([(i, i, i) for i in range(256)])
        image2 = Image.new('RGB', (16, 16))
        image2.putdata(pixels2)
        result2 = EinkGraphics.round(image2)
        self._check_pixels(
            expected_pixels, list(result2.convert('L').getdata()))

    def test_round_monochrome(self):
        """Test ``EinkGraphics.round`` with ``Palette.MONOCHROME``."""
        pixels1 = list(range(256))
        image1 = Image.new('L', (16, 16))
        image1.putdata(pixels1)
        result1 = EinkGraphics.round(image1, Palette.MONOCHROME)
        expected_pixels = ([0] * 128) + ([255] * 128)
        self.assertEqual(
            expected_pixels, list(result1.convert('L').getdata()))

        pixels2 = list([(i, i, i) for i in range(256)])
        image2 = Image.new('RGB', (16, 16))
        image2.putdata(pixels2)
        result2 = EinkGraphics.round(image2, Palette.MONOCHROME)
        self.assertEqual(
            expected_pixels, list(result2.convert('L').getdata()))

    def _are_pixels_in(self, image, values):
        """Return whether all pixels in ``image.getdata()`` are in ``values``.

        Arguments:
            image (Image): The image.
            values (set): The values.

        Return:
            bool: The result.
        """
        for pixel in image.getdata():
            if pixel not in values:
                return False
        return True

    def test_dither_grayscale(self):
        """Test ``EinkGraphics.dither`` with ``Palette.THREE_BIT_GRAYSCALE``.
        """
        # Test an image that only contains pixels with luminosity between 1/7
        # and 2/7
        pixels1 = list([36 + (i % 38) for i in range(400)])
        image1 = Image.new('L', (20, 20))
        image1.putdata(pixels1)
        result1 = EinkGraphics.dither(image1)
        self.assertTrue(
            self._are_pixels_in(result1.convert('L'), set([36, 73])))

        pixels2 = []
        for y in range(17):
            for x in range(16):
                pixels2.append(8 * (x + y) + (x % 8))
        image2 = Image.new('L', (16, 17))
        image2.putdata(pixels2)
        result2 = EinkGraphics.dither(image2)
        rounded_colors = set([0, 36, 73, 109, 146, 182, 219, 255])
        self.assertTrue(
            self._are_pixels_in(result2.convert('L'), rounded_colors))

        pixels3 = list([(color, color, color) for color in pixels2])
        image3 = Image.new('RGB', (16, 17))
        image3.putdata(pixels3)
        result3 = EinkGraphics.dither(image3)
        self.assertTrue(
            self._are_pixels_in(result3.convert('L'), rounded_colors))

    def test_dither_monochrome(self):
        """Test ``EinkGraphics.dither`` with ``Palette.MONOCHROME``."""
        pixels1 = []
        for y in range(17):
            for x in range(16):
                pixels1.append(8 * (x + y) + (x % 8))
        image1 = Image.new('L', (16, 17))
        image1.putdata(pixels1)
        result1 = EinkGraphics.dither(image1, Palette.MONOCHROME)
        colors = set([0, 255])
        self.assertTrue(self._are_pixels_in(result1.convert('L'), colors))

        pixels2 = list([(color, color, color) for color in pixels1])
        image2 = Image.new('RGB', (16, 17))
        image2.putdata(pixels2)
        result2 = EinkGraphics.dither(image2, Palette.MONOCHROME)
        self.assertTrue(self._are_pixels_in(result2.convert('L'), colors))
