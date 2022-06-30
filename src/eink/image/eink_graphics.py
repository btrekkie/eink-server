from PIL import Image

from .palette import Palette


class EinkGraphics:
    """Provides static methods for reducing images to e-ink display palettes.
    """
    @staticmethod
    def _has_alpha(image):
        """Return whether the specified ``Image`` has an alpha channel."""
        return image.mode[-1] in ['A', 'a']

    @staticmethod
    def _assert_doesnt_have_alpha(image):
        """Raise a ``ValueError`` if the given ``Image`` has an alpha channel.
        """
        if EinkGraphics._has_alpha(image):
            raise ValueError('Alpha channels are not supported')

    @staticmethod
    def round(image, palette=Palette.THREE_BIT_GRAYSCALE):
        """Return the result of rounding the given image to the given palette.

        Return the result of rounding each pixel in the specified
        ``Image`` to roughly the nearest color in the specified
        ``Palette``. This is a format suitable for display on an e-ink
        device. The image may not have an alpha channel.

        This does not perform dithering. See also ``dither``.
        """
        EinkGraphics._assert_doesnt_have_alpha(image)
        if palette._is_grayscale:
            # First convert to grayscale, in order to apply the luminosity
            # transform function L = 0.299 * R + 0.587 * G + 0.114 * B
            grayscale_image = image.convert('L')

            # At time of writing, the "quantize" method rounds each component
            # down to the nearest multiple of four before rounding a pixel to
            # the nearest palette color. We can round pixels more accurately by
            # calling "point" instead.
            return grayscale_image.point(palette._round_lookup_table())
        else:
            return image.convert('RGB').quantize(
                dither=Image.Dither.NONE, palette=palette._image())

    @staticmethod
    def dither(image, palette=Palette.THREE_BIT_GRAYSCALE):
        """Return the result of dithering the given image to the given palette.

        Return the result of converting each pixel in the specified
        ``Image`` to a color in the specified ``Palette`` using
        dithering. This is a format suitable for display on an e-ink
        device. The image may not have an alpha channel.

        Instead of simply rounding each pixel to the nearest color in
        the palette, we use dithering, which represents a region that is
        in between two palette colors by coloring its pixels using a
        combination of those two colors. See
        https://en.wikipedia.org/wiki/Dither .

        Dithering gives the result a speckled appearance that tends to
        look closer to the original image, especially from a distance.
        However, in some cases, a more flatly shaded look might be
        preferable. For example, dithering might be undesirable for
        icons that have large areas of solid shading.
        """
        EinkGraphics._assert_doesnt_have_alpha(image)
        if palette._is_grayscale:
            # First convert to grayscale, in order to apply the luminosity
            # transform function L = 0.299 * R + 0.587 * G + 0.114 * B
            image = image.convert('L')
        return image.convert('RGB').quantize(
            dither=Image.Dither.FLOYDSTEINBERG, palette=palette._image())
