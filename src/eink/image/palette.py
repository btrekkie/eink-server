from PIL import Image


class Palette:
    """A color palette for an e-ink device.

    The following palettes are supported:

    * ``Palette.THREE_BIT_GRAYSCALE``: 3-bit grayscale, i.e. eight
      shades of gray.
    * ``Palette.MONOCHROME``: Black and white.
    """

    # Private attributes:
    #
    # list<tuple<int, int, int>> _colors - The colors in the palette. Each
    #     color is represented as a tuple of the red, green, and blue
    #     components, in the range [0, 255].
    # Image _image_cache - The cached return value of _image().
    # string _name - A string identifying the palette in client code. This
    #     consists exclusively of underscores and uppercase letters.
    # list<int> _round_lookup_table_cache - The cached return value of
    #     _round_lookup_table().

    def __init__(self, colors, name):
        """Private initializer.

        For now, only grayscale palettes are supported.
        """
        self._colors = colors
        self._name = name
        self._round_lookup_table_cache = None
        self._image_cache = None

    def _round_lookup_table(self):
        """Return a lookup table for rounding to the nearest color.

        The return value is an array of 256 elements. The (i + 1)th
        element is the red, green, and blue component of the palette
        color nearest to the color (i, i, i) (with ties broken
        arbitrarily).
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
            palette.extend(self._colors[0] * (256 - len(self._colors)))

            self._image_cache = Image.new('P', (1, 1))
            self._image_cache.putpalette(palette)
        return self._image_cache


Palette.THREE_BIT_GRAYSCALE = Palette(
    [
        (0, 0, 0), (36, 36, 36), (73, 73, 73), (109, 109, 109),
        (146, 146, 146), (182, 182, 182), (219, 219, 219), (255, 255, 255)],
    '3_BIT_GRAYSCALE')

Palette.MONOCHROME = Palette([(0, 0, 0), (255, 255, 255)], 'MONOCHROME')
