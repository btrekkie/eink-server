#ifndef __DRAW_IMAGE_H__
#define __DRAW_IMAGE_H__

#include <Inkplate.h>

#include "byte_array.h"
#include "server_io.h"


/**
 * Renders the specified PNG or RGB JPEG image. This does not use dithering; see
 * the comments for the Python method EinkGraphics.dither. It ignores any PNG
 * alpha channel. This method uses an unspecified combination of the red, green,
 * and blue components of each pixel, so it's best if the image is grayscale. It
 * does not necessarily round each pixel to the nearest 3-bit color, but it does
 * map from luminosity to 3-bit colors (using a monotonically increasing
 * function).
 * @param display The 3-bit Inkplate display.
 * @param image The contents of the PNG or JPEG file.
 * @param x The x coordinate of the top-left corner at which to render the
 *     image.
 * @param y The y coordinate of the top-left corner at which to render the
 *     image.
 */
void drawImage(Inkplate* display, ByteArray image, int x, int y);

/**
 * Renders the specified PNG image. This uses rounding rather than dithering;
 * see the comments for the Python method EinkGraphics.dither. It ignores any
 * alpha channel. This method uses an unspecified combination of the red, green,
 * and blue components of each pixel, so it's best if the image is grayscale.
 * @param display The 3-bit Inkplate display.
 * @param reader The Reader from which to read the contents of the PNG file. If
 *     we reach the end of the stream before reading the entire PNG file, this
 *     method will return, but its effect on the display is unspecified.
 * @param length The number of bytes in the PNG file.
 * @param x The x coordinate of the top-left corner at which to render the
 *     image.
 * @param y The y coordinate of the top-left corner at which to render the
 *     image.
 */
void drawPngFromReader(
    Inkplate* display, Reader* reader, int length, int x, int y);

#endif
