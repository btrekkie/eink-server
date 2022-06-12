import io

from PIL import Image


class ImageData:
    """Provides methods for converting an ``Image`` to image file data."""

    @staticmethod
    def _render(image, mode, colors, format_, **kwargs):
        """Convert the specified image to image file data.

        Arguments:
            image (Image): The image.
            mode (str): The mode to convert the image to prior to
                producing image data.
            colors (int): The number of palette colors to use, as in the
                ``colors`` keyword argument to ``Image.convert``. If
                ``image`` contains at most ``colors`` distinct colors,
                then the returned image will exactly match ``image``.
                This is ignored if ``mode`` is not ``'P'``.
            format_ (str): The image file format, as in the second
                argument to ``Image.save``.
            kwargs (dict<str, object>): The keyword arguments to pass to
                ``Image.save``.

        Returns:
            bytes: The image file data.
        """
        output = io.BytesIO()

        # When converting to mode 'P', the default median cut algorithm used
        # for selecting a palette should give the correct result, i.e. the
        # converted image should exactly match the original image if it only
        # contains "colors" distinct colors. We rely on this fact to ensure a
        # lossless representation of the image.
        converted_image = image.convert(
            mode, colors=colors, dither=Image.NONE, palette=Image.ADAPTIVE)

        converted_image.save(output, format_, **kwargs)
        return output.getvalue()

    @staticmethod
    def render_jpeg(image, quality):
        """Convert the specified image to RGB JPEG image file data.

        Arguments:
            image (Image): The image.
            quality (int): The compression quality. This is a number
                from 0 to 100, as in the JPEG file format.

        Returns:
            bytes: The image file data.
        """
        return ImageData._render(
            image, 'RGB', 1, 'JPEG', optimize=True, quality=quality)

    @staticmethod
    def render_png(image, palette, optimize=False):
        """Convert the specified image to PNG image file data.

        Arguments:
            image (Image): The image.
            palette (Palette): The color palette for the image. The
                image may only contain colors in this palette.
            optimize (bool): Whether to spend extra time trying to
                minimize the length of the resulting data.

        Returns:
            bytes: The image file data.
        """
        png1 = ImageData._render(image, 'L', 1, 'PNG', optimize=optimize)
        if len(palette._colors) > 256:
            # The Pillow library only supports 256 palette colors
            return png1
        else:
            png2 = ImageData._render(
                image, 'P', len(palette._colors), 'PNG', dither=Image.NONE,
                optimize=optimize)
            if len(png1) <= len(png2):
                return png1
            else:
                return png2
