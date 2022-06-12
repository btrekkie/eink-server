#include <Inkplate.h>

#include "client_state.h"
#include "eink_client.h"
#include "generated.h"


// The ClientState for the program
ClientState clientState;

// The Inkplate object for the program
#ifdef PALETTE_3_BIT_GRAYSCALE
    Inkplate display(INKPLATE_3BIT);
#elif defined PALETTE_MONOCHROME
    Inkplate display(INKPLATE_1BIT);
#else
    #error "Unknown palette"
#endif

void setup() {
    clientSetup(&clientState, &display);
}

void loop() {
    clientLoop(&clientState, &display);
}
