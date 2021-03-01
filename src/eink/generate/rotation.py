from enum import Enum


class Rotation(Enum):
    """A rotation to use when drawing to the Inkplate device."""

    # Landscape rotation
    LANDSCAPE = 4

    # Portrait left (bottom of device on left)
    PORTRAIT_LEFT = 3

    # Portrait right (bottom of device on right)
    PORTRAIT_RIGHT = 1

    # Upside down landscape rotation
    LANDSCAPE_UPSIDE_DOWN = 2
