import unittest

from PIL import Image

from eink.image import Palette


class PaletteTest(unittest.TestCase):
    """Tests the ``Palette`` class."""

    def test_is_grayscale(self):
        """Test ``Palette._is_grayscale``."""
        self.assertTrue(Palette.THREE_BIT_GRAYSCALE._is_grayscale)
        self.assertTrue(Palette.MONOCHROME._is_grayscale)
        self.assertFalse(Palette.SEVEN_COLOR._is_grayscale)

    def test_round_lookup_table_grayscale(self):
        """Test ``Palette.THREE_BIT_GRAYSCALE._round_lookup_table()``."""
        expected = (
            ([[0]] * 18) + [[0, 1]] + ([[36]] * 36) + ([[73]] * 36) +
            [[73, 109]] + ([[109]] * 36) + ([[146]] * 36) + [[146, 182]] +
            ([[182]] * 36) + ([[219]] * 36) + [[219, 255]] + ([[255]] * 18))
        actual = Palette.THREE_BIT_GRAYSCALE._round_lookup_table()
        self.assertEqual(256, len(actual))
        for expected_pixel, actual_pixel in zip(expected, actual):
            self.assertIn(actual_pixel, expected_pixel)

    def test_round_lookup_table_monochrome(self):
        """Test ``Palette.MONOCHROME._round_lookup_table()``."""
        expected = ([0] * 128) + ([255] * 128)
        actual = Palette.MONOCHROME._round_lookup_table()
        self.assertEqual(expected, actual)
