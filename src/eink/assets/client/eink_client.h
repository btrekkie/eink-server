#ifndef __EINK_CLIENT_H__
#define __EINK_CLIENT_H__

#include <Inkplate.h>

#include "client_state.h"


/**
 * Implementation of Arduino's setup() function.
 * @param state The ClientState for the program.
 * @param display The 3-bit Inkplate display.
 */
void clientSetup(ClientState* state, Inkplate* display);

/**
 * Implementation of Arduino's loop() function.
 * @param state The ClientState for the program.
 * @param display The 3-bit Inkplate display.
 */
void clientLoop(ClientState* state, Inkplate* display);

#endif
