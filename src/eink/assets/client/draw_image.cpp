#include <string.h>

// It's improper to rely on the Pngle library, because it's not part of the
// public Inkplate API. But I don't know of a better way to draw PNGs from an
// input stream.
#include "pngle.h"

#include "draw_image.h"


// The bytes that always appear at the beginning of a PNG file
static const char PNG_HEADER[] =
    {0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a};

// The bytes that always appear at the beginning of a JPEG file
static const char JPEG_HEADER[] = {0xff, 0xd8};

// The bytes that always appear at the end of a JPEG file
static const char JPEG_FOOTER[] = {0xff, 0xd9};

// The number of bytes for drawPngFromReader to use to store bytes from the PNG
// file
#define READ_PNG_BUFFER_SIZE 4096


/** The drawing arguments required by drawPngDraw. */
typedef struct {
    // The 3-bit Inkplate display
    Inkplate* display;

    // The x coordinate of the top-left corner at which we are rendering the
    // image
    int x;

    // The y coordinate of the top-left corner at which we are rendering the
    // image
    int y;
} DrawPngArgs;

/**
 * Returns this program's shared instance of pngle_t. The pngle_t object's state
 * is reset, as in pngle_reset.
 *
 * An instance of pngle_t uses about 30 KB, which is sizable compared to total
 * available memory. If we were to create them on demand, each time we did so,
 * there would be a risk that the relevant call to malloc would fail. Better to
 * use a shared instance, so that we only incur this risk once during the whole
 * life of the program.
 */
static pngle_t* drawImagePngle() {
    static pngle_t* pngle = NULL;
    if (pngle == NULL) {
        pngle = pngle_new();
    } else {
        pngle_reset(pngle);
    }
    return pngle;
}

/**
 * The Pngle draw callback for a call to drawPngFromReader or equivalent. The
 * user data (as in pngle_get_user_data) must be an instance of DrawPngleArgs.
 * We render the pixel "directly" by calling Inkplate.drawPixel.
 */
static void drawPngDraw(
        pngle_t* pngle, uint32_t x, uint32_t y, uint32_t width, uint32_t height,
        uint8_t rgba[4]) {
    // Use the green component, since we're free to use any combination of the
    // color components
    int color8 = rgba[1];

    // Compute (int)((7 * color8) / 255 + 0.5) using an integer division trick
    int color3 = (14 * color8 + 255) / (2 * 255);

    DrawPngArgs* args = (DrawPngArgs*)pngle_get_user_data(pngle);
    args->display->drawPixel(args->x + x, args->y + y, color3);
}

/** Sets "args" to contain the specified field values. */
static void setDrawPngArgs(DrawPngArgs* args, Inkplate* display, int x, int y) {
    args->display = display;
    args->x = x;
    args->y = y;
}

/**
 * Implementation of drawImage for when the image is a PNG file.
 * @param display The 3-bit Inkplate display.
 * @param data The contents of the PNG file.
 * @param length The number of bytes in the PNG file.
 * @param x The x coordinate of the top-left corner at which to render the
 *     image.
 * @param y The y coordinate of the top-left corner at which to render the
 *     image.
 */
static void drawPngFromBuffer(
        Inkplate* display, uint8_t* data, int32_t length, int x, int y) {
    DrawPngArgs args;
    setDrawPngArgs(&args, display, x, y);

    pngle_t* pngle = drawImagePngle();
    pngle_set_user_data(pngle, &args);
    pngle_set_draw_callback(pngle, drawPngDraw);
    pngle_feed(pngle, data, length);
}

void drawImage(Inkplate* display, ByteArray image, int x, int y) {
    void* data = image.data;
    int length = image.length;
    if (length >= sizeof(PNG_HEADER) &&
            memcmp(data, PNG_HEADER, sizeof(PNG_HEADER)) == 0) {
        drawPngFromBuffer(display, (uint8_t*)data, length, x, y);
    } else if (length >= sizeof(JPEG_HEADER) + sizeof(JPEG_FOOTER) &&
            memcmp(data, JPEG_HEADER, sizeof(JPEG_HEADER)) == 0 &&
            memcmp(
                data + length - sizeof(JPEG_FOOTER), JPEG_FOOTER,
                sizeof(JPEG_FOOTER)) == 0) {
        display->drawJpegFromBuffer((uint8_t*)data, length, x, y, false, false);
    }
}

void drawPngFromReader(
        Inkplate* display, Reader* reader, int length, int x, int y) {
    DrawPngArgs args;
    setDrawPngArgs(&args, display, x, y);

    pngle_t* pngle = drawImagePngle();
    pngle_set_user_data(pngle, &args);
    pngle_set_draw_callback(pngle, drawPngDraw);

    char buffer[READ_PNG_BUFFER_SIZE];
    int remaining = length;
    while (remaining > READ_PNG_BUFFER_SIZE) {
        readBytes(reader, buffer, READ_PNG_BUFFER_SIZE);
        if (readerPassedEof(reader) ||
                pngle_feed(pngle, buffer, READ_PNG_BUFFER_SIZE) < 0) {
            return;
        }
        remaining -= READ_PNG_BUFFER_SIZE;
    }
    readBytes(reader, buffer, remaining);
    if (!readerPassedEof(reader)) {
        pngle_feed(pngle, buffer, remaining);
    }
}
