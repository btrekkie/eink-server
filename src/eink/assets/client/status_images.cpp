#include <string.h>

#include <Inkplate.h>

#include "byte_array.h"
#include "draw_image.h"
#include "generated.h"
#include "status_images.h"


/**
 * Draws the status image with the ID STATUS_IMAGE_IDS[index].
 * @param display The 3-bit Inkplate display.
 * @param index the index.
 */
static void drawStatusImage(Inkplate* display, int index) {
    ByteArray image = createByteArray(
        (void*)STATUS_IMAGE_DATA[index], STATUS_IMAGE_DATA_LENGTHS[index]);
    drawImage(display, image, 0, 0);
}

void drawStatusImageByType(Inkplate* display, StatusImageType type) {
    display->clearDisplay();
    drawStatusImage(display, STATUS_IMAGES_BY_TYPE[(int)type]);
    display->display();
}

/**
 * Returns the index of the status image with the specified ID in
 * STATUS_IMAGE_IDS. Returns -1 if there is no such status image.
 * @param imageId The image ID, as in the Python method ServerIO.image_id.
 * @return The index.
 */
static int findStatusImage(char* imageId) {
    // Binary search
    int start = 0;
    int end = STATUS_IMAGE_COUNT;
    while (start < end) {
        int mid = (start + end) / 2;
        int comparison = memcmp(
            imageId, STATUS_IMAGE_IDS[mid], STATUS_IMAGE_ID_LENGTH);
        if (comparison < 0) {
            end = mid;
        } else if (comparison > 0) {
            start = mid + 1;
        } else {
            return mid;
        }
    }
    return -1;
}

void drawStatusImageById(Inkplate* display, char* imageId) {
    int index = findStatusImage(imageId);
    display->clearDisplay();
    if (index >= 0) {
        drawStatusImage(display, index);
    }
    display->display();
}
