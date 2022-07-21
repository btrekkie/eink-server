class Device:
    """A type of e-ink device (e.g. Inkplate 6).

    Public attributes:

    int height - The height of the device in the landscape orientation,
        in pixels.
    str palette_name - The name of the ``Palette`` constant for the most
        suitable palette for the device. The palette is given by
        ``getattr(Palette, palette_name)``.
    int width - The width of the device in the landscape orientation, in
        pixels.
    """

    def __init__(self, width, height, palette_name):
        self.width = width
        self.height = height
        self.palette_name = palette_name
