#ifndef __CLIENT_STATE_H__
#define __CLIENT_STATE_H__

#include "generated.h"


/**
 * The persistent state of the client program. All of the fields are stored by
 * value, so that the state may be persisted as an RTC_DATA_ATTR (deep sleep)
 * variable.
 */
typedef struct {
    // The amount of time between requests to the server, in tenths of a second.
    // We wait requestTimesDs[0], then query the server, then wait
    // requestTimesDs[1], then query the server again, and so on. When we reach
    // the requestTimeCount'th element of requestTimesDs, we continue to retry
    // every requestTimesDs[requestTimeCount - 1] tenths of a second. INT_MAX
    // indicates an infinite amount of time, i.e. we should not query the server
    // again.
    int requestTimesDs[MAX_REQUEST_TIMES];

    // The number of times stored in requestTimesDs
    int requestTimeCount;

    // The index in requestTimesDs for the period of time that we are currently
    // waiting to make a request to the server
    int requestTimeIndex;

    // The amount of time left until the next request to the server, in tenths
    // of a second. If we are in deep sleep, then this indicates the time left
    // when we wake.
    int requestTimeDs;

    // The ID of the screensaver image, as in the Python method
    // ServerIO.image_id. If we have not made a successful request to the
    // server, this is unspecified.
    char screensaverId[STATUS_IMAGE_ID_LENGTH];

    // The amount of time left to wait before displaying the screensaver, in
    // tenths of a second. If this is INT_MAX, then we will never display a
    // screensaver. This is set to INT_MAX whenever we display the screensaver.
    // If we are in deep sleep, then this indicates the time left when we wake.
    int screensaverTimeDs;

    // A value indicating when to check the battery level and display a low
    // battery image if it is too low. Roughly speaking, this is the number of
    // tenths of a second to wait before checking the battery at a multiplier of
    // 1. We use a higher multiplier in conditions where we expect the battery
    // is being depleted more quickly. If we are in deep sleep, then this
    // indicates the timer value for when we wake.
    int checkBatteryTimer;
} ClientState;

#endif
