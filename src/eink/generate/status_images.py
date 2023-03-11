import os

from PIL import Image

from ..project.project import Project


class StatusImages:
    """Describes the program's "status images."

    A "status image" is a special full-screen image that is not produced
    by ``Server.render()``. It is hardcoded as part of the software on
    the client device, so that the client can render it without
    contacting the server. There are three types of status images: the
    initial image, the low battery image, and the screensaver. Each
    status image is identified by a string name.
    """

    # Private attributes:
    #
    # int _height - The height of the Inkplate display, after rotation (as in
    #     ClientConfig.set_rotation).
    # dict<str, Image> _images - A map from the names of the status images to
    #     the images.
    # str _initial_image_name - The name of the status image to display when
    #     the device is turned on.
    # str _low_battery_image_name - The name of the status image to display if
    #     the device is low on battery. When this happens, we stop trying to
    #     connect to the server.
    # dict<str, int> _quality - A map from the names of the status images to
    #     their qualities, as in the "quality" argument to set_image.
    # int _width - The width of the Inkplate display, after rotation (as in
    #     ClientConfig.set_rotation).

    def __init__(self, width, height):
        """Initialize a new ``StatusImages`` object.

        Arguments:
            width (int): The width of the Inkplate display, after
                rotation (as in ``ClientConfig.set_rotation``).
            height (int): The height of the Inkplate display, after
                rotation (as in ``ClientConfig.set_rotation``).
        """
        self._width = width
        self._height = height
        self._images = {}
        self._quality = {}
        self._initial_image_name = 'connecting'
        self._low_battery_image_name = 'low_battery'

    def set_image(self, name, image, quality=100):
        """Set (or add) the status image with the specified name.

        We automatically reduce the image to the appropriate color
        palette using ``EinkGraphics.round``.

        Arguments:
            name (str): The name of the status image.
            image (Image): The status image. This must be the same size
                as the display.
            quality (int): The compression quality to use to store the
                image. This is a number from 0 to 100, as in the JPEG
                file format. The higher the number, the more faithfully
                we will be able to reproduce the image, but the more
                memory it will require. 100 indicates perfect quality
                (or lossless).

                Normally, a quality of 100 is recommended. But if the
                status images are too numerous and large, it's possible
                that they won't fit in the client's program memory. In
                that case, a lower level of quality is required.
        """
        if image.width != self._width or image.height != self._height:
            raise ValueError(
                'A status image must be the same size as the display')
        self._images[name] = image
        self._quality[name] = quality

    def set_initial_image_name(self, name):
        """Set the name of the initial status image.

        Set the name of the status image to display when the device is
        turned on. The default is ``'connecting'``.
        """
        self._initial_image_name = name

    def set_low_battery_image_name(self, name):
        """Set the name of the low battery image.

        Set the name of the status image to display if the device is low
        on battery. When this happens, we stop trying to connect to the
        server. The default low battery image name is ``'low_battery'``.
        """
        self._low_battery_image_name = name

    def default_initial_image(self):
        """Return the "default" initial status image.

        Return the "default" status image to display when the display is
        turned on. This is a standard image that the ``eink-server``
        library provides as a default.

        Returns:
            Image: The image.
        """
        if self._width >= 320 and self._height >= 220:
            return self._default_image('connecting.png')
        else:
            return self._default_image('connecting_low_res.png')

    def default_low_battery_image(self):
        """Return the "default" low battery image.

        Return the "default" status image to display if the device is
        low on battery. This is a standard image that the
        ``eink-server`` library provides as a default.

        Returns:
            Image: The image.
        """
        if self._width >= 208 and self._height >= 130:
            return self._default_image('low_battery.png')
        else:
            return self._default_image('low_battery_low_res.png')

    @staticmethod
    def create_default(width, height):
        """Return an instance of ``StatusImages`` with "default" images.

        This uses standard images that the ``eink-server`` library
        provides as defaults. It uses the default image names.

        Arguments:
            width (int): The width of the Inkplate display, after
                rotation (as in ``ClientConfig.set_rotation``).
            height (int): The height of the Inkplate display, after
                rotation (as in ``ClientConfig.set_rotation``).
        """
        images = StatusImages(width, height)
        images.set_image('connecting', images.default_initial_image())
        images.set_image('low_battery', images.default_low_battery_image())
        return images

    def _default_image(self, filename):
        """Return a default status image from the specified image file.

        Arguments:
            filename (str): The filename of the image file, excluding
                the directory (``Project.images_dir()``).

        Returns:
            Image: The image.
        """
        image = Image.open(os.path.join(Project.images_dir(), filename))
        output = Image.new('L', (self._width, self._height), 255)
        output.paste(
            image, (
                (self._width - image.width) // 2,
                (self._height - image.height) // 2))
        return output
