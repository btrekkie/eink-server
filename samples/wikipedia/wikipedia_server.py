from datetime import timedelta
import os
import subprocess
import tempfile

from eink.image import EinkGraphics
from eink.image import Palette
from eink.server import Server
from PIL import Image


class WikipediaServer(Server):
    """Displays the Wikipedia homepage.

    This can easily be modified to show another webpage. It requires the
    ``google-chrome`` command to be present in the path.
    """

    # The URL to display
    _URL = 'https://en.wikipedia.org/'

    def __init__(
            self, width=800, height=600, palette=Palette.THREE_BIT_GRAYSCALE):
        """Initialize a new ``WikipediaServer``.

        Arguments:
            width (int): The width of the display, after rotation.
            height (int): The height of the display, after rotation.
            palette (Palette): The palette to use. This must be a
                palette that the e-ink device supports.
        """
        self._width = width
        self._height = height
        self._palette = palette

    def update_time(self):
        return timedelta(hours=1)

    def screensaver_time(self):
        return timedelta(days=2)

    def palette(self):
        return self._palette

    def render(self):
        handle, temp_filename = tempfile.mkstemp(
            '.png', 'eink-server-wikipedia')
        try:
            try:
                # Render the URL to temp_filename
                subprocess.check_output([
                    'google-chrome', '--headless',
                    '--screenshot={:s}'.format(temp_filename),
                    '--window-size={:d}x{:d}'.format(
                        self._width, self._height),
                    '--hide-scrollbars', WikipediaServer._URL])
            finally:
                os.close(handle)

            return EinkGraphics.dither(
                Image.open(temp_filename).convert('RGB'), self._palette)
        finally:
            if os.path.isfile(temp_filename):
                os.remove(temp_filename)
