#ifndef __WI_FI_REQUEST_H__
#define __WI_FI_REQUEST_H__

#include <Inkplate.h>

#include "byte_array.h"
#include "client_state.h"


/** Describes a way of making requests to a Wi-Fi server. */
typedef struct {
    // The request URL
    char* url;
} WiFiTransport;

/**
 * Requests updated content from the specified server. If successful, applies
 * the results to the ClientState and display.
 * @param state The client state.
 * @param display The Inkplate display.
 * @param payload The request payload.
 * @param transport The server.
 * @return Whether the update was successful.
 */
bool makeWiFiRequest(
    ClientState* state, Inkplate* display, ByteArray payload,
    WiFiTransport* transport);

/** Makes any preparations required for upcoming calls to makeWiFiRequest. */
void prepareForWiFiRequests();

/**
 * Handles the fact that we will not make any requests to a Wi-Fi server for the
 * specified amount of time, in tenths of a second.
 */
void handleRadioSilenceWiFi(int timeDs);

#endif
