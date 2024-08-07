#include <string.h>

#if defined PALETTE_7_COLOR || defined PALETTE_BLACK_WHITE_AND_RED
    #include "Inkplate.h"
#endif
// It's improper to rely on the Pngle library, because it's not part of the
// public Inkplate API. But I don't know of a better way to draw PNGs from an
// input stream.
#include "pngle.h"

#include "draw_image.h"
#include "generated.h"


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

#ifdef PALETTE_7_COLOR
    // The number of colors in the palette
    const int PALETTE_COLOR_COUNT = 7;

    // The colors in the palette. Each color is represented as a sequence of its
    // red, green, and blue components.
    const int PALETTE_COLORS[] = {
        0, 0, 0,
        255, 255, 255,
        67, 138, 28,
        85, 94, 126,
        138, 76, 91,
        255, 243, 56,
        232, 126, 0};

    // The colors in the palette, as represented in Inkplate.drawPixel and the
    // like. The colors are in the same order as in PALETTE_COLORS.
    const int INKPLATE_COLORS[] = {
        INKPLATE_BLACK, INKPLATE_WHITE, INKPLATE_GREEN, INKPLATE_BLUE,
        INKPLATE_RED, INKPLATE_YELLOW, INKPLATE_ORANGE};
#endif


/** The drawing arguments required by drawPngDraw. */
typedef struct {
    // The Inkplate display
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
    int red = rgba[0];
    int green = rgba[1];
    int blue = rgba[2];

    int color;
    #if defined PALETTE_MONOCHROME || defined PALETTE_3_BIT_GRAYSCALE || defined PALETTE_4_BIT_GRAYSCALE
        // Compute (int)(7 * (0.299 * red + 0.587 * green + 0.114 * blue) / 255
        // + 0.5)
        int color1000 = 299 * red + 587 * green + 114 * blue;
        #ifdef PALETTE_MONOCHROME
            color = color1000 >= 255 * 1000 / 2 ? WHITE : BLACK;
        #else
            #ifdef PALETTE_3_BIT_GRAYSCALE
                int COLOR_MAX = 7;
            #else
                int COLOR_MAX = 15;
            #endif
            color = (COLOR_MAX * color1000 + 255 * 1000 / 2) / (255 * 1000);
        #endif
    #elif defined PALETTE_BLACK_WHITE_AND_RED
        if (red >= 128) {
            if (blue + green < 255) {
                color = INKPLATE2_RED;
            } else {
                color = INKPLATE2_WHITE;
            }
        } else if (red * red + green * green + blue * blue <
                (255 - red) * (255 - red) + (255 - green) * (255 - green) +
                (255 - blue) * (255 - blue)) {
            color = INKPLATE2_BLACK;
        } else {
            color = INKPLATE2_WHITE;
        }
    #else
        int bestIndex = 0;
        int bestDistance = 1000000000;
        for (int i = 0; i < PALETTE_COLOR_COUNT; i++) {
            int dr = PALETTE_COLORS[3 * i] - red;
            int dg = PALETTE_COLORS[3 * i + 1] - green;
            int db = PALETTE_COLORS[3 * i + 2] - blue;
            int distance = dr * dr + dg * dg + db * db;
            if (distance < bestDistance) {
                bestIndex = i;
                bestDistance = distance;
            }
        }
        color = INKPLATE_COLORS[bestIndex];
    #endif

    DrawPngArgs* args = (DrawPngArgs*)pngle_get_user_data(pngle);
    args->display->drawPixel(args->x + x, args->y + y, color);
}

/** Sets "args" to contain the specified field values. */
static void setDrawPngArgs(DrawPngArgs* args, Inkplate* display, int x, int y) {
    args->display = display;
    args->x = x;
    args->y = y;
}

/**
 * Implementation of drawImage for when the image is a PNG file.
 * @param display The Inkplate display.
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
