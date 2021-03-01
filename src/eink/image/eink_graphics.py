from PIL import Image


class EinkGraphics:
    """Provides static methods pertaining to 3-bit grayscale."""

    # The cached return value of _round_lookup_table()
    _round_lookup_table_cache = None

    # The cached return value of _eink_palette()
    _eink_palette_cache = None

    @staticmethod
    def _color_3_to_8(color3):
        """Return the 8-bit color value for the specified 3-bit color.

        This rounds to the nearest 8-bit color value.

        Arguments:
            color7 (int): The 3-bit color, in the range [0, 7].

        Returns:
            int: The 8-bit color, in the range [0, 255].
        """
        # Compute int((255 * color7) / 7 + 0.5) using an integer division trick
        return (2 * 255 * color3 + 7) // 14

    @staticmethod
    def _color_8_to_3(color8):
        """Return the 3-bit color value for the specified 8-bit color.

        This rounds to the nearest 3-bit color value.

        Arguments:
            color8 (int): The 8-bit color, in the range [0, 255].

        Returns:
            int: The 3-bit color, in the range [0, 7].
        """
        # Compute int((7 * color8) / 255 + 0.5) using an integer division trick
        return (14 * color8 + 255) // (2 * 255)

    @staticmethod
    def _round_lookup_table():
        """Return a lookup table for rounding to the nearest 3-bit color.

        The return value is an array of 256 elements. The (i + 1)th
        element is ``_color_3_to_8(color_8_to_3(i))``.
        """
        if EinkGraphics._round_lookup_table_cache is None:
            EinkGraphics._round_lookup_table_cache = []
            for color8 in range(256):
                color3 = EinkGraphics._color_8_to_3(color8)
                EinkGraphics._round_lookup_table_cache.append(
                    EinkGraphics._color_3_to_8(color3))
        return EinkGraphics._round_lookup_table_cache

    @staticmethod
    def _eink_palette():
        """Return an ``Image`` whose palette is all 3-bit colors.

        Return an ``Image`` of mode ``'P'`` whose palette consists of
        the 3-bit colors, i.e. of all possible return values of
        ``_color_3_to_8``.
        """
        if EinkGraphics._eink_palette_cache is None:
            palette = []
            for i in range(8):
                color8 = EinkGraphics._color_3_to_8(i)
                for j in range(3):
                    palette.append(color8)
            for i in range(3 * 8, 3 * 256):
                palette.append(0)

            EinkGraphics._eink_palette_cache = Image.new('P', (1, 1))
            EinkGraphics._eink_palette_cache.putpalette(palette)
        return EinkGraphics._eink_palette_cache

    @staticmethod
    def _has_alpha(image):
        """Return whether the specified ``Image`` has an alpha channel."""
        return image.mode[:-1] in ['A', 'a']

    @staticmethod
    def _assert_doesnt_have_alpha(image):
        """Raise a ``ValueError`` if the given ``Image`` has an alpha channel.
        """
        if EinkGraphics._has_alpha(image):
            raise ValueError('Alpha channels are not supported')

    @staticmethod
    def round(image):
        """Return the result of rounding the given image to 3-bit grayscale.

        Return the result of converting the specified ``Image`` to mode
        ``'L'`` and then rounding each pixel to the nearest 3-bit
        grayscale value (and then rounding back to an 8-bit value). This
        is a format suitable for display on an e-ink device. The image
        may not have an alpha channel.

        This does not perform dithering. See also ``dither``.
        """
        EinkGraphics._assert_doesnt_have_alpha(image)
        return image.convert('L').point(EinkGraphics._round_lookup_table())

    @staticmethod
    def dither(image):
        """Return the result of dithering the given image to 3-bit grayscale.

        Return the result of converting the specified ``Image`` to mode
        ``'L'`` and then converting each pixel to a 3-bit grayscale
        value (rounded back to an 8-bit value) using dithering. This is
        a format suitable for display on an e-ink device. The image may
        not have an alpha channel.

        Instead of simply rounding each pixel to the nearest 3-bit
        color, we use dithering, which represents a region that is in
        between two 3-bit colors by coloring its pixels using a
        combination of those two colors. See
        https://en.wikipedia.org/wiki/Dither .

        Dithering gives the result a speckled appearance that tends to
        look closer to the original image, especially from a distance.
        However, in some cases, a more flatly shaded look might be
        preferable. For example, dithering might be undesirable for
        icons that have large areas of solid shading.
        """
        EinkGraphics._assert_doesnt_have_alpha(image)

        # First convert to grayscale, in order to apply the luminosity
        # transform function L = 0.299 * R + 0.587 * G + 0.114 * B
        grayscale_image = image.convert('L')

        # Now convert to RGB, since the palette is RGB
        rgb_image = grayscale_image.convert('RGB')

        return rgb_image.quantize(
            dither=Image.FLOYDSTEINBERG, palette=EinkGraphics._eink_palette())
