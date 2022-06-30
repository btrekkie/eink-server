import io

from PIL import Image


class ImageData:
    """Provides methods for converting an ``Image`` to image file data."""

    @staticmethod
    def _render(image, format_, **kwargs):
        """Convert the specified image to image file data.

        Arguments:
            image (Image): The image.
            format_ (str): The image file format, as in the second
                argument to ``Image.save``.
            kwargs (dict<str, object>): The keyword arguments to pass to
                ``Image.save``.

        Returns:
            bytes: The image file data.
        """
        output = io.BytesIO()
        image.save(output, format_, **kwargs)
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
            image.convert('RGB'), 'JPEG', optimize=True, quality=quality)

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
        p_image = image.convert('RGB').quantize(
            dither=Image.Dither.NONE, palette=palette._image())
        return ImageData._render(p_image, 'PNG', optimize=optimize)
