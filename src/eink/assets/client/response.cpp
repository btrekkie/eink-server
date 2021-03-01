#include <esp32-hal.h>
#include <string.h>

#include "draw_image.h"
#include "generated.h"
#include "response.h"
#include "server_io.h"
#include "shared.h"
#include "status_images.h"


/**
 * Handles the case where we reach the end of the response payload while we are
 * in the middle of drawing the image with the updated content. This could
 * happen if our connection to the server is interrupted.
 */
static void handleIncompleteImage(ClientState* state, Inkplate* display) {
    log_e(
        "Prematurely reached end of server response. The connection with the "
        "server may have been interrupted. We don't have a good way of "
        "recovering from this.");
    drawStatusImageByType(display, STATUS_IMAGE_INITIAL);
    memcpy(
        state->requestTimesDs, INITIAL_REQUEST_TIMES_DS,
        sizeof(int) * INITIAL_REQUEST_TIMES_COUNT);
    state->requestTimeCount = INITIAL_REQUEST_TIMES_COUNT;
    state->requestTimeIndex = 0;
    state->requestTimeDs = INITIAL_REQUEST_TIMES_DS[0];
    state->screensaverTimeDs = INT_MAX;
}

bool execResponse(ClientState* state, Inkplate* display, Reader* reader) {
    // execResponse is careful not to leave things in a broken state if we pass
    // the EOF. This could occur if our connection to the server is interrupted.
    char header[HEADER_LENGTH];
    readBytes(reader, header, HEADER_LENGTH);
    if (readerPassedEof(reader) || memcmp(header, HEADER, HEADER_LENGTH) != 0) {
        return false;
    }

    int requestTimeCount = readInt(reader);
    if (readerPassedEof(reader)) {
        return false;
    }
    int requestTimesDs[MAX_REQUEST_TIMES];
    for (int i = 0; i < requestTimeCount; i++) {
        requestTimesDs[i] = readInt(reader);
    }

    char screensaverId[STATUS_IMAGE_ID_LENGTH];
    readBytes(reader, screensaverId, STATUS_IMAGE_ID_LENGTH);
    int screensaverTimeDs = readInt(reader);
    int imageLength = readInt(reader);

    if (readerPassedEof(reader)) {
        return false;
    }

    // We've safely read everything except the image data. Store the values in
    // "state".
    state->requestTimeCount = requestTimeCount;
    memcpy(
        state->requestTimesDs, requestTimesDs, sizeof(int) * requestTimeCount);
    state->requestTimeIndex = 0;
    state->requestTimeDs = requestTimesDs[0];
    memcpy(state->screensaverId, screensaverId, STATUS_IMAGE_ID_LENGTH);
    state->screensaverTimeDs = screensaverTimeDs;

    display->clearDisplay();
    drawPngFromReader(display, reader, imageLength, 0, 0);
    if (!readerPassedEof(reader)) {
        display->display();
        log_i("Updated content from server response");
    } else {
        handleIncompleteImage(state, display);
    }
    return true;
}
