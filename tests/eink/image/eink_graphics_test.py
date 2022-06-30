import random
import unittest

from PIL import Image

from eink.image import EinkGraphics
from eink.image import Palette


class EinkGraphicsTest(unittest.TestCase):
    """Tests the ``EinkGraphics`` class."""

    def _random_image(self):
        """Return a randomly generated ``Image`` with mode ``'RGB'``.

        Use a fixed seed.
        """
        rng = random.Random(247693537)
        pixels = []
        for _ in range(400):
            pixel = []
            for _ in range(3):
                pixel.append(rng.randrange(256))
            pixels.append(tuple(pixel))
        image = Image.new('RGB', (20, 20))
        image.putdata(pixels)
        return image

    def _random_grayscale_image(self):
        """Return a randomly generated ``Image`` with mode ``'L'``.

        Use a fixed seed.
        """
        rng = random.Random(649695934)
        pixels = list(rng.randrange(256) for _ in range(400))
        image = Image.new('L', (20, 20))
        image.putdata(pixels)
        return image

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

    def _check_round(self, palette):
        """Test ``EinkGraphics.round`` with the specified ``Palette``."""
        pixels = []
        expected_pixels = []
        for color in palette._colors:
            pixels.append(color)
            expected_pixels.append(color)

            pixel = []
            for component in color:
                pixel.append(
                    component + 1 if component < 255 else component - 1)
            pixels.append(tuple(pixel))
            expected_pixels.append(color)
        image1 = Image.new('RGB', (len(palette._colors), 2))
        image1.putdata(pixels)

        result1 = EinkGraphics.round(image1, palette)
        self.assertEqual(image1.size, result1.size)
        self.assertFalse(EinkGraphics._has_alpha(result1))
        actual_pixels = result1.convert('RGB').getdata()
        self.assertEqual(expected_pixels, list(actual_pixels))

        image2 = self._random_image()
        result2 = EinkGraphics.round(image2, palette)
        self.assertEqual(image2.size, result2.size)
        self.assertFalse(EinkGraphics._has_alpha(result2))
        self.assertTrue(
            self._are_pixels_in(result2.convert('RGB'), palette._colors))

        image3 = self._random_grayscale_image()
        result3 = EinkGraphics.round(image3, palette)
        self.assertEqual(image3.size, result3.size)
        self.assertFalse(EinkGraphics._has_alpha(result3))
        self.assertTrue(
            self._are_pixels_in(result3.convert('RGB'), palette._colors))

    def test_round(self):
        """Test ``EinkGraphics.round``."""
        self._check_round(Palette.THREE_BIT_GRAYSCALE)
        self._check_round(Palette.MONOCHROME)
        self._check_round(Palette.SEVEN_COLOR)

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
        self.assertEqual(image1.size, result1.size)
        self.assertFalse(EinkGraphics._has_alpha(result1))
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
        self.assertEqual(image2.size, result2.size)
        self.assertFalse(EinkGraphics._has_alpha(result2))
        self._check_pixels(
            expected_pixels, list(result2.convert('L').getdata()))

    def test_round_monochrome(self):
        """Test ``EinkGraphics.round`` with ``Palette.MONOCHROME``."""
        pixels1 = list(range(256))
        image1 = Image.new('L', (16, 16))
        image1.putdata(pixels1)
        result1 = EinkGraphics.round(image1, Palette.MONOCHROME)
        self.assertEqual(image1.size, result1.size)
        self.assertFalse(EinkGraphics._has_alpha(result1))
        expected_pixels = ([0] * 128) + ([255] * 128)
        self.assertEqual(
            expected_pixels, list(result1.convert('L').getdata()))

        pixels2 = list([(i, i, i) for i in range(256)])
        image2 = Image.new('RGB', (16, 16))
        image2.putdata(pixels2)
        result2 = EinkGraphics.round(image2, Palette.MONOCHROME)
        self.assertEqual(image2.size, result2.size)
        self.assertFalse(EinkGraphics._has_alpha(result2))
        self.assertEqual(
            expected_pixels, list(result2.convert('L').getdata()))

    def _check_dither(self, palette):
        """Test ``EinkGraphics.dither`` with the specified ``Palette``."""
        image1 = self._random_image()
        result1 = EinkGraphics.dither(image1, palette)
        self.assertEqual(image1.size, result1.size)
        self.assertFalse(EinkGraphics._has_alpha(result1))
        self.assertTrue(
            self._are_pixels_in(result1.convert('RGB'), palette._colors))

        image2 = self._random_grayscale_image()
        result2 = EinkGraphics.dither(image2, palette)
        self.assertEqual(image2.size, result2.size)
        self.assertFalse(EinkGraphics._has_alpha(result2))
        self.assertTrue(
            self._are_pixels_in(result2.convert('RGB'), palette._colors))

    def test_dither(self):
        """Test ``EinkGraphics.dither``."""
        self._check_dither(Palette.THREE_BIT_GRAYSCALE)
        self._check_dither(Palette.MONOCHROME)
        self._check_dither(Palette.SEVEN_COLOR)

    def test_dither_grayscale(self):
        """Test ``EinkGraphics.dither`` with ``Palette.THREE_BIT_GRAYSCALE``.
        """
        # Test an image that only contains pixels with luminosity between 1/7
        # and 2/7
        rng = random.Random(-1287208726)
        pixels = list([rng.randrange(36, 74) for i in range(400)])
        image = Image.new('L', (20, 20))
        image.putdata(pixels)
        result = EinkGraphics.dither(image)
        self.assertEqual(image.size, result.size)
        self.assertFalse(EinkGraphics._has_alpha(result))
        self.assertTrue(
            self._are_pixels_in(result.convert('L'), set([36, 73])))
