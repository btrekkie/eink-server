import os

from eink.image import EinkGraphics
from eink.server import Server
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class MyServer(Server):
    """The e-ink server for this project."""

    # The display's dimensions
    WIDTH = $width
    HEIGHT = $height

    # The singleton instance of MyServer
    _instance = None

    def update_time(self):
        return None

    def screensaver_time(self):
        return None

    def render(self):
        # Load the fonts
        dir_ = os.path.dirname(os.path.abspath(__file__))
        font_filename = os.path.join(dir_, 'assets', 'GentiumPlus-R.ttf')
        header_font = ImageFont.truetype(font_filename, 80)
        text_font = ImageFont.truetype(font_filename, 36)

        # Render the header text
        image = Image.new('L', (MyServer.WIDTH, MyServer.HEIGHT), 255)
        draw = ImageDraw.Draw(image)
        x = MyServer.WIDTH // 2 - 260
        y = MyServer.HEIGHT // 2 - 144
        draw.text(
            (x + 250, y), 'Hello, world!', anchor='mt', fill=0,
            font=header_font)

        # Render a circle
        circle = self._render_circle(64, 64)
        image.paste(circle, (x + 218, y + 103, x + 282, y + 167))

        # Render the body text
        draw.multiline_text(
            (x, y + 194),
            'If you can read this, then you have\n'
            'successfully set up your server.',
            fill=0, font=text_font)
        return image

    def _render_circle(self, width, height):
        """Return a shaded circle ``Image`` with the specified size."""
        circle = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, width - 1, height - 1), 0)

        white = Image.new('L', (width, height), 255)
        gradient = Image.linear_gradient('L').resize((width, height))
        rotated_gradient = gradient.transpose(Image.ROTATE_90)
        shaded_circle = Image.composite(white, rotated_gradient, circle)
        return EinkGraphics.dither(shaded_circle)

    @staticmethod
    def instance():
        """Return the singleton instance of ``MyServer``."""
        if MyServer._instance is None:
            MyServer._instance = MyServer()
        return MyServer._instance
