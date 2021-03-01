#ifndef __STATUS_IMAGES_H__
#define __STATUS_IMAGES_H__

#include <Inkplate.h>


/** A type of invariable status image, as in the Python class StatusImages. */
typedef enum {
    // The initial image, as in the Python method
    // StatusImages.set_initial_image_name
    STATUS_IMAGE_INITIAL,

    // The low battery image, as in the Python method
    // StatusImages.set_low_battery_image_name
    STATUS_IMAGE_LOW_BATTERY
} StatusImageType;

/**
 * Renders the status image of the specified type.
 * @param display The 3-bit Inkplate display.
 * @param type The type.
 */
void drawStatusImageByType(Inkplate* display, StatusImageType type);

/**
 * Renders the status image with the specified ID. If there is no such status
 * image, this clears the display (i.e. fills it with white).
 * @param display The 3-bit Inkplate display.
 * @param imageId The image ID, as in the return value of the Python method
 *     ServerIO.image_id.
 */
void drawStatusImageById(Inkplate* display, char* imageId);

#endif
