from datetime import timedelta
import os
import random

from eink.image import EinkGraphics
from eink.server import Server
from PIL import Image


class SlideshowServer(Server):
    """Displays a slideshow of all of the images in a given directory.

    All available JPEG and PNG images are displayed in a random order
    (shuffle).
    """

    def __init__(
            self, image_dir, update_time=timedelta(seconds=30),
            width=800, height=600):
        """Initialize a new ``SlideshowServer``.

        Arguments:
            image_dir (str): The directory containing the images. We
                search the directory recursively for images.
            update_time (timedelta): The amount of time to show each
                image.
            width (int): The width of the display, after rotation.
            height (int): The height of the display, after rotation.
        """
        self._image_dir = image_dir
        self._update_time = update_time
        self._width = width
        self._height = height
        self._image_filenames = []

    def update_time(self):
        return self._update_time

    def screensaver_time(self):
        return None

    def render(self):
        if not self._image_filenames:
            # Locate the images
            for dir_, subdirs, subfiles in os.walk(self._image_dir):
                for subfile in subfiles:
                    if subfile.lower().endswith(('.jpeg', '.jpg', '.png')):
                        self._image_filenames.append(
                            os.path.join(dir_, subfile))

            if not self._image_filenames:
                return Image.new('L', (self._width, self._height), 255)
            random.shuffle(self._image_filenames)

        # Display the next image
        image_filename = self._image_filenames.pop()
        image = Image.open(image_filename)
        return EinkGraphics.dither(image.resize((self._width, self._height)))
