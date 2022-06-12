#ifndef __RESPONSE_H__
#define __RESPONSE_H__

#include <Inkplate.h>

#include "client_state.h"
#include "server_io.h"


/**
 * Applies the content updates in a server response payload to the ClientState
 * and display. If we detect that the response payload is not correctly
 * formatted, this has no effect.
 * @param state The client state.
 * @param display The Inkplate display.
 * @param reader A reader containing the response payload.
 * @return Whether we were successful, meaning we did not detect that the
 *     response payload was incorrectly formatted.
 */
bool execResponse(ClientState* state, Inkplate* display, Reader* reader);

#endif
