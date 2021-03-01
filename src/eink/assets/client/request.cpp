#include <esp32-hal.h>

#include "byte_array.h"
#include "generated.h"
#include "request.h"
#include "server_io.h"
#include "wi_fi_request.h"


/** Describes a transport, i.e. a way of making requests to a server. */
typedef struct {
    // The Wi-Fi-related features of this transport
    WiFiTransport wiFi;
} Transport;

/**
 * Returns an array of the Transports to use for this program, in the order in
 * which we should try to connect to them. This has TRANSPORT_COUNT elements.
 */
static Transport* requestTransports() {
    static Transport transports[TRANSPORT_COUNT];
    static bool haveSetTransports = false;

    if (!haveSetTransports) {
        for (int i = 0; i < TRANSPORT_COUNT; i++) {
            Transport* transport = transports + i;
            transport->wiFi.url = (char*)TRANSPORT_URLS[i];
        }
    }
    return transports;
}

/** Returns the request payload to use. */
static ByteArray requestPayload() {
    Writer writer;
    initWriter(&writer);
    writeBytes(&writer, (void*)HEADER, HEADER_LENGTH);
    writeByteArray(
        &writer,
        createByteArray((void*)PROTOCOL_VERSION, PROTOCOL_VERSION_LENGTH));
    return finishWriter(&writer);
}

void makeRequest(ClientState* state, Inkplate* display) {
    log_i("Requesting content updates");
    ByteArray request = requestPayload();
    prepareForWiFiRequests();
    Transport* transports = requestTransports();
    bool success = false;
    for (int i = 0; i < TRANSPORT_COUNT; i++) {
        if (makeWiFiRequest(state, display, request, &transports[i].wiFi)) {
            success = true;
            break;
        }
    }

    free(request.data);
    if (!success) {
        log_e("Failed to obtain content updates");
        if (state->requestTimeIndex + 1 < state->requestTimeCount) {
            state->requestTimeIndex++;
        }
        state->requestTimeDs = state->requestTimesDs[state->requestTimeIndex];
    }
    handleRadioSilenceWiFi(state->requestTimeDs);
}
