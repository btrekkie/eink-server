#include <Inkplate.h>

#include "client_state.h"
#include "eink_client.h"


// The ClientState for the program
ClientState clientState;

// The Inkplate object for the program
Inkplate display(INKPLATE_3BIT);

void setup() {
    clientSetup(&clientState, &display);
}

void loop() {
    clientLoop(&clientState, &display);
}
