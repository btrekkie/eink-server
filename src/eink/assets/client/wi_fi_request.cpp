#include <string.h>

#include <esp32-hal.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <WiFiClient.h>

#include "generated.h"
#include "response.h"
#include "server_io.h"
#include "wi_fi_request.h"


// The maximum number of microseconds to spend attempting to connect to a given
// Wi-Fi network
static const long long WI_FI_CONNECT_TIMEOUT_US = 20 * 1000000LL;

// The threshold for turning off the Wi-Fi hardware. If we will not make a web
// request for at least WI_FI_OFF_TIME_DS tenths of a second, then we turn it
// off to save energy.
static const int WI_FI_OFF_TIME_DS = 60 * 10;

// The value of WI_FI_NETWORK_COUNT at or above which we scan for networks and
// only attempt to connect to those identified in the scan. Otherwise, we
// indiscriminately attempt to connect to networks in WI_FI_SSIDS.
static const int WI_FI_SCAN_THRESHOLD = 2;

// The maximum number of Wi-Fi networks to try to connect to each time we try to
// connect
#define WI_FI_MAX_NETWORKS_TO_TRY 3

/**
 * Attempts to connect to the specified Wi-Fi network.
 * @param ssid The network's SSID.
 * @param password The network's password. NULL indicates no password.
 * @return Whether we were successful.
 */
static bool connectToWiFiNetwork(const char* ssid, const char* password) {
    long long startTime = esp_timer_get_time();
    if (password != NULL) {
        WiFi.begin(ssid, password);
    } else {
        WiFi.begin(ssid);
    }

    while (esp_timer_get_time() - startTime < WI_FI_CONNECT_TIMEOUT_US) {
        if (WiFi.status() == WL_CONNECTED) {
            return true;
        }
        delay(200);
    }
    return WiFi.status() == WL_CONNECTED;
}

/**
 * Returns the index in WI_FI_NETWORK_INDICES of the first SSID in strcmp order
 * that is greater than or equal to "ssid". A return value of
 * WI_FI_NETWORK_COUNT indicates that "ssid" is greater than all of the SSIDs in
 * WI_FI_SSID.
 */
static int findWiFiNetworkIndex(char* ssid) {
    // Binary search
    int start = 0;
    int end = WI_FI_NETWORK_COUNT;
    while (start < end) {
        int mid = (start + end) / 2;
        if (strcmp(ssid, WI_FI_SSIDS[WI_FI_NETWORK_INDICES[mid]]) <= 0) {
            end = mid;
        } else {
            start = mid + 1;
        }
    }
    return start;
}

/**
 * Returns whether "index" is among the first "length" elements of "indices".
 */
static bool containsWiFiNetworkIndex(int* indices, int length, int index) {
    for (int i = 0; i < length; i++) {
        if (indices[i] == index) {
            return true;
        }
    }
    return false;
}

/**
 * Adds the specified index to "indices". "indices" is a sorted array consisting
 * of up to WI_FI_MAX_NETWORKS_TO_TRY values. (Note that if "indices" has
 * WI_FI_MAX_NETWORKS_TO_TRY values that are less than "index", then this will
 * have no effect.)
 * @param indices The indices. This must have a length of
 *     WI_FI_MAX_NETWORKS_TO_TRY.
 * @param length The number of elements currently in "indices".
 * @param index The value to add to "indices".
 * @return The resulting number of elements in "indices", i.e. the smaller of
 *     length + 1 and WI_FI_MAX_NETWORKS_TO_TRY.
 */
static int insertWiFiNetworkIndex(int* indices, int length, int index) {
    int i;
    for (i = length - 1; i >= 0; i--) {
        if (index > indices[i]) {
            break;
        }
        if (i + 1 < WI_FI_MAX_NETWORKS_TO_TRY) {
            indices[i + 1] = indices[i];
        }
    }
    if (i + 1 < WI_FI_MAX_NETWORKS_TO_TRY) {
        indices[i + 1] = index;
    }

    if (length < WI_FI_MAX_NETWORKS_TO_TRY) {
        return length + 1;
    } else {
        return WI_FI_MAX_NETWORKS_TO_TRY;
    }
}

/**
 * Sets "indices" to be an array of the indices in WI_FI_SSIDS of the Wi-Fi
 * networks we should attempt to connect to, in order.
 * @param indices The indices. This must have a length of
 *     WI_FI_MAX_NETWORKS_TO_TRY.
 * @return The maximum number of Wi-Fi networks we should attempt to connect to.
 */
static int wiFiNetworksToTry(int* indices) {
    if (WI_FI_NETWORK_COUNT < WI_FI_SCAN_THRESHOLD) {
        int i;
        for (i = 0; i < WI_FI_NETWORK_COUNT && i < WI_FI_MAX_NETWORKS_TO_TRY;
                i++) {
            indices[i] = i;
        }
        return i;
    }

    int length = 0;
    int scannedNetworks = WiFi.scanNetworks();
    for (int i = 0; i < scannedNetworks; i++) {
        String ssidStr = WiFi.SSID(i);
        char* ssid = (char*)ssidStr.c_str();
        int start = findWiFiNetworkIndex(ssid);
        for (int j = start; j < WI_FI_NETWORK_COUNT; j++) {
            int index = WI_FI_NETWORK_INDICES[j];
            if (strcmp(WI_FI_SSIDS[index], ssid) != 0 ||
                    // Handle duplicate SSID in scan results
                    (j == start &&
                        containsWiFiNetworkIndex(indices, length, index))) {
                break;
            }
            length = insertWiFiNetworkIndex(indices, length, index);
        }
    }
    return length;
}

/**
 * Attempts to connect to a Wi-Fi network, if we are not already connected.
 * @return Whether we were successful.
 */
static bool connectToWiFi() {
    if (WiFi.status() == WL_CONNECTED) {
        return true;
    }

    log_i("Connecting to Wi-Fi");

    // This appears to be needed to clear out the WIFI_REASON_AUTH_EXPIRE state
    // if the Wi-Fi connection is lost
    WiFi.disconnect();

    int indices[WI_FI_MAX_NETWORKS_TO_TRY];
    int length = wiFiNetworksToTry(indices);
    for (int i = 0; i < length; i++) {
        int index = indices[i];
        if (connectToWiFiNetwork(WI_FI_SSIDS[index], WI_FI_PASSWORDS[index])) {
            return true;
        }
    }
    log_e("Failed to connect to Wi-Fi");
    return false;
}

/**
 * readFunc function for initReader for reading the response payload from a
 * WiFiClient. "context" is a pointer to the WiFiClient.
 */
static int readWiFi(void* data, int length, void* context) {
    WiFiClient* wiFi = (WiFiClient*)context;
    int offset = 0;
    while (offset < length) {
        int read = wiFi->read((uint8_t*)(data + offset), length - offset);
        if (read < 0) {
            return offset;
        }
        offset += read;
        if (!wiFi->connected()) {
            return offset;
        }
    }
    return length;
}

bool makeWiFiRequest(
        ClientState* state, Inkplate* display, ByteArray payload,
        WiFiTransport* transport) {
    if (WiFi.status() != WL_CONNECTED) {
        return false;
    }

    HTTPClient http;
    if (!http.begin(transport->url)) {
        return false;
    }

    int status = http.POST((uint8_t*)payload.data, payload.length);
    if (status < 200 || status >= 300) {
        http.end();
        return false;
    }

    WiFiClient* wiFi = http.getStreamPtr();
    Reader reader;
    initReader(&reader, readWiFi, wiFi);
    bool success = execResponse(state, display, &reader);
    http.end();
    return success;
}

void prepareForWiFiRequests() {
    connectToWiFi();
}

void handleRadioSilenceWiFi(int timeDs) {
    if (timeDs >= WI_FI_OFF_TIME_DS) {
        log_i("Turning Wi-Fi off to save energy");
        WiFi.mode(WIFI_OFF);
    }
}
