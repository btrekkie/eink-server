import unittest

from eink.generate import StatusImages


class StatusImagesTest(unittest.TestCase):
    """Tests the ``StatusImages`` class."""

    def test_default_images(self):
        """Test ``StatusImages.default_*_image``."""
        status_images = StatusImages(20, 20)
        default_images = [
            status_images.default_initial_image(),
            status_images.default_low_battery_image()]
        for image in default_images:
            self.assertEqual(20, image.width)
            self.assertEqual(20, image.height)
