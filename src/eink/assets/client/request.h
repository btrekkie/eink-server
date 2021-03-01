#ifndef __REQUEST_H__
#define __REQUEST_H__

#include <Inkplate.h>

#include "client_state.h"


/**
 * Requests updated content from the server(s). If successful, applies the
 * results to the ClientState and display. In any event, this sets
 * state->requestTimeDs to the time until the next request.
 * @param state The client state.
 * @param display The 3-bit Inkplate display.
 */
void makeRequest(ClientState* state, Inkplate* display);

#endif
