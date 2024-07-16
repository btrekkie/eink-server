from PIL import Image


class Palette:
    """A color palette for an e-ink device.

    The following palettes are supported:

    * ``Palette.THREE_BIT_GRAYSCALE``: 3-bit grayscale, i.e. eight
      shades of gray.
    * ``Palette.FOUR_BIT_GRAYSCALE``: 4-bit grayscale, i.e. 16
      shades of gray.
    * ``Palette.MONOCHROME``: Black and white.
    * ``Palette.BLACK_WHITE_AND_RED``: Black, white, and red.
    * ``Palette.SEVEN_COLOR``: The palette for color Inkplate devices.
      This has the following seven colors: black, white, red, green,
      blue, yellow, and orange.
    """

    # Private attributes:
    #
    # list<tuple<int, int, int>> _colors - The colors in the palette. Each
    #     color is represented as a tuple of the red, green, and blue
    #     components, in the range [0, 255].
    # Image _image_cache - The cached return value of _image().
    # bool _is_grayscale - Whether the palette consists exclusively of
    #     grayscale colors.
    # string _name - A string identifying the palette in client code. This
    #     consists exclusively of underscores and uppercase letters.
    # list<int> _round_lookup_table_cache - The cached return value of
    #     _round_lookup_table().

    def __init__(self, colors, name):
        """Private initializer."""
        if len(colors) > 256:
            raise ValueError('Palette only supports up to 256 colors')

        self._colors = colors
        self._name = name
        self._round_lookup_table_cache = None
        self._image_cache = None

        self._is_grayscale = True
        for color in colors:
            if color[0] != color[1] or color[0] != color[2]:
                self._is_grayscale = False
                break

    def _round_lookup_table(self):
        """Return a lookup table for rounding to the nearest grayscale color.

        Assume that ``_is_grayscale`` is true. The return value is an
        array of 256 integers. The (i + 1)th element is the red, green,
        and blue component of the palette color nearest to the color
        ``(i, i, i)`` (with ties broken arbitrarily).
        """
        if self._round_lookup_table_cache is None:
            self._round_lookup_table_cache = []
            sorted_colors = sorted([color[0] for color in self._colors])
            index = 0
            for color in range(256):
                if (index + 1 < len(sorted_colors) and
                        sorted_colors[index + 1] - color <
                        color - sorted_colors[index]):
                    index += 1
                self._round_lookup_table_cache.append(sorted_colors[index])
        return self._round_lookup_table_cache

    def _image(self):
        """Return an ``Image`` whose palette is the colors of this palette.

        Return an ``Image`` of mode ``'P'`` whose palette consists of
        the colors of this palette.
        """
        if self._image_cache is None:
            palette = []
            for color in self._colors:
                palette.extend(color)
            self._image_cache = Image.new('P', (1, 1))
            self._image_cache.putpalette(palette)
        return self._image_cache


Palette.THREE_BIT_GRAYSCALE = Palette(
    [(round(255 * color / 7),) * 3 for color in range(8)], '3_BIT_GRAYSCALE')
Palette.FOUR_BIT_GRAYSCALE = Palette(
    [(round(255 * color / 15),) * 3 for color in range(16)], '4_BIT_GRAYSCALE')
Palette.MONOCHROME = Palette([(0, 0, 0), (255, 255, 255)], 'MONOCHROME')
Palette.BLACK_WHITE_AND_RED = Palette(
    [(0, 0, 0), (255, 255, 255), (255, 0, 0)], 'BLACK_WHITE_AND_RED')
Palette.SEVEN_COLOR = Palette(
    [
        (0, 0, 0), (255, 255, 255), (67, 138, 28), (85, 94, 126),
        (138, 76, 91), (255, 243, 56), (232, 126, 0)],
    '7_COLOR')
