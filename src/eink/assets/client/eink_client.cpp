#include <limits.h>
#include <string.h>

#include <esp32-hal.h>
#include <WiFi.h>

#include "client_state.h"
#include "define_test_eink.h"
#include "eink_client.h"
#include "request.h"
#include "shared.h"
#include "status_images.h"

#ifdef TEST_EINK
#include <AUnit.h>
#endif

// The initial value for ClientState.checkBatteryTimer, and the value we set it
// back to whenever we check the battery
static const int CHECK_BATTERY_TIMER = 10 * 60 * 10 * 20;

// The voltage below which we display the low battery image
static const double LOW_BATTERY_VOLTAGE_THRESHOLD = 3.7;

// The multiplier for decreasing ClientState.checkBatteryTimer when the Wi-Fi
// hardware is turned on
static const int CHECK_BATTERY_MULT_WI_FI_ON = 20;

// The multiplier for decreasing ClientState.checkBatteryTimer when the Wi-Fi
// hardware is turned off, but we are not in deep or light sleep
static const int CHECK_BATTERY_MULT_WI_FI_OFF = 10;

// The multiplier for decreasing ClientState.checkBatteryTimer when we are in
// light sleep
static const int CHECK_BATTERY_MULT_LIGHT_SLEEP = 5;

// The multiplier for decreasing ClientState.checkBatteryTimer when we are in
// deep sleep
static const int CHECK_BATTERY_MULT_DEEP_SLEEP = 1;

// The minimum amount of time to sleep in light sleep, in tenths of a second
static const int MIN_LIGHT_SLEEP_TIME_DS = 50;

// The minimum amount of time to sleep in deep sleep, in tenths of a second
static const int MIN_DEEP_SLEEP_TIME_DS = 150;

// The number of milliseconds in one tenth of a second
static const int MS_PER_DS = 100;

// The number of microseconds in one tenth of a second
static const long long US_PER_DS = 100000;

// Stores the current state while we are in deep sleep
static RTC_DATA_ATTR ClientState sleepState;

/**
 * Initializes the specified ClientState, for when we first start the program.
 */
static void initClientState(ClientState* state) {
    memcpy(
        state->requestTimesDs, INITIAL_REQUEST_TIMES_DS,
        sizeof(int) * INITIAL_REQUEST_TIMES_COUNT);
    state->requestTimeCount = INITIAL_REQUEST_TIMES_COUNT;
    state->requestTimeIndex = 0;
    state->requestTimeDs = state->requestTimesDs[0];
    memset(state->screensaverId, 0, sizeof(state->screensaverId));
    state->screensaverTimeDs = INT_MAX;
    state->checkBatteryTimer = CHECK_BATTERY_TIMER;
}

/** Causes the device to idle permanently (or rather, until reset). */
static void delayForever() {
    // TODO Can we do better?
    log_i("Delaying forever");
    WiFi.mode(WIFI_OFF);
    esp_deep_sleep_start();
}

/**
 * Checks the battery level. Displays the low battery image and idles
 * permanently if the battery level is too low.
 */
static void checkBattery(Inkplate* display) {
    log_i("Checking battery level");
    if (display->readBattery() < LOW_BATTERY_VOLTAGE_THRESHOLD) {
        drawStatusImageByType(display, STATUS_IMAGE_LOW_BATTERY);
        delayForever();
    }
}

void clientSetup(ClientState* state, Inkplate* display) {
    display->begin();
    #ifdef TEST_EINK
        Serial.begin(115200);
        while (!Serial) {
            delay(20);
        }
    #else
        if (esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_TIMER) {
            memcpy(state, &sleepState, sizeof(ClientState));
        } else {
            display->setRotation(ROTATION);
            checkBattery(display);
            drawStatusImageByType(display, STATUS_IMAGE_INITIAL);
            initClientState(state);
        }
    #endif
}

/**
 * Updates state->requestTimeDs, state->screensaverTimeDs, and
 * state->checkBatteryTimer to reflect the specified amount of time elapsing.
 * @param state The client state.
 * @param timeDs The amount of time, in tenths of a second.
 * @param checkBatteryMult The multiplier for decreasing
 *     state->checkBatteryTimer.
 */
void handleTimeElapsedDs(ClientState* state, int timeDs, int checkBatteryMult) {
    if (state->requestTimeDs < INT_MAX) {
        if (state->requestTimeDs > timeDs) {
            state->requestTimeDs -= timeDs;
        } else {
            state->requestTimeDs = 0;
        }
    }

    if (state->screensaverTimeDs < INT_MAX) {
        if (state->screensaverTimeDs > timeDs) {
            state->screensaverTimeDs -= timeDs;
        } else {
            state->screensaverTimeDs = 0;
        }
    }

    if (state->checkBatteryTimer < INT_MAX) {
        if (timeDs <= INT_MAX / checkBatteryMult &&
                state->checkBatteryTimer > checkBatteryMult * timeDs) {
            state->checkBatteryTimer -= checkBatteryMult * timeDs;
        } else {
            state->checkBatteryTimer = 0;
        }
    }
}

/**
 * Idles for the specified amount of time. This may put the device in light
 * sleep or deep sleep. It makes the appropriate call to handleTimeElapsedDs
 * (with delayTimeDs as an argument).
 * @param state The client state.
 * @param delayTimeDs The amount of time to idle, in tenths of a second.
 */
static void delayDs(ClientState* state, int delayTimeDs) {
    log_d("Delaying for %d tenths of a second", delayTimeDs);
    wifi_mode_t wiFiMode = WiFi.getMode();
    if (wiFiMode != WIFI_OFF || delayTimeDs < MIN_LIGHT_SLEEP_TIME_DS) {
        delay(MS_PER_DS * delayTimeDs);

        int checkBatteryMult;
        if (wiFiMode == WIFI_OFF) {
            checkBatteryMult = CHECK_BATTERY_MULT_WI_FI_OFF;
        } else {
            checkBatteryMult = CHECK_BATTERY_MULT_WI_FI_ON;
        }
        handleTimeElapsedDs(state, delayTimeDs, checkBatteryMult);
    } else if (delayTimeDs < MIN_DEEP_SLEEP_TIME_DS) {
        log_d("Entering light sleep");
        handleTimeElapsedDs(state, delayTimeDs, CHECK_BATTERY_MULT_LIGHT_SLEEP);
        esp_sleep_enable_timer_wakeup(US_PER_DS * delayTimeDs);
        esp_light_sleep_start();
    } else {
        log_i("Entering deep sleep");
        handleTimeElapsedDs(state, delayTimeDs, CHECK_BATTERY_MULT_DEEP_SLEEP);
        memcpy(&sleepState, state, sizeof(ClientState));
        esp_sleep_enable_timer_wakeup(US_PER_DS * delayTimeDs);
        esp_deep_sleep_start();
    }
}

/**
 * Idles until we need to take our next action. This makes the appropriate call
 * to handleTimeElapsedDs.
 * @param state The client state.
 * @param isWiFiOn Whether the Wi-Fi hardware is turned on.
 * @return The amount of time we idled, in tenths of a second.
 */
static int delayToNextEvent(ClientState* state, bool isWiFiOn) {
    // We compute the next battery check time based on CHECK_BATTERY_TIMER
    // rather than state->checkBatteryTimer. This is because checking the
    // battery is not a particularly time-sensitive operation. It would be a
    // shame to refrain from entering deep sleep, per MIN_DEEP_SLEEP_TIME_DS,
    // just to do a battery check.
    int maxBatteryTimeMult =
        isWiFiOn ? CHECK_BATTERY_MULT_WI_FI_ON : CHECK_BATTERY_MULT_DEEP_SLEEP;
    int maxBatteryTimeDs =
        (CHECK_BATTERY_TIMER + maxBatteryTimeMult - 1) / maxBatteryTimeMult;

    int delayTimeDs = state->requestTimeDs;
    if (state->screensaverTimeDs < delayTimeDs) {
        delayTimeDs = state->screensaverTimeDs;
    }
    if (maxBatteryTimeDs < delayTimeDs) {
        delayTimeDs = maxBatteryTimeDs;
    }

    if (delayTimeDs <= 0) {
        return 0;
    }
    if (delayTimeDs == INT_MAX) {
        delayForever();
    } else {
        delayDs(state, delayTimeDs);
    }
    return delayTimeDs;
}

/**
 * Calls handleTimeElapsedDs based on the amount of time elapsed since some
 * moment in the past, as measured by calling esp_timer_get_time(). The idea is
 * that we (potentially) call delayDs, then perform some activity, then call
 * handleTimeElapsedDs with the amount of time that elapsed minus the amount of
 * time we delayed for. This is how we account for the duration of said
 * activity.
 * @param state The client state.
 * @param prevTimeUs The return value of esp_timer_get_time() at the moment in
 *     the past.
 * @param prevDelayTimeDs The amount of time we have delayed since the moment in
 *     the past, in tenths of a second.
 * @return The return value of esp_timer_get_time() for the present moment.
 */
static long long handleMeasuredElapsedTime(
        ClientState* state, long long prevTimeUs, int prevDelayTimeDs) {
    long long timeUs = esp_timer_get_time();
    int elapsedTimeDs;
    if (timeUs - prevTimeUs < US_PER_DS * INT_MAX) {
        elapsedTimeDs =
            (int)((timeUs - prevTimeUs + US_PER_DS / 2) / US_PER_DS);
    } else {
        elapsedTimeDs = INT_MAX;
    }
    if (elapsedTimeDs > prevDelayTimeDs) {
        // Regardless of whether the Wi-Fi is currently on, it may have been on
        // for part of the relevant activity, so pass in
        // CHECK_BATTERY_MULT_WI_FI_ON to be conservative
        handleTimeElapsedDs(
            state, elapsedTimeDs - prevDelayTimeDs,
            CHECK_BATTERY_MULT_WI_FI_ON);
    }
    return timeUs;
}

/**
 * Executes the corresponding events if state->requestTimeDs,
 * state->screensaverTimeDs, or state->checkBatteryTimer is 0. This sets those
 * fields to their new values if they were 0.
 * @param state The client state.
 * @param display The 3-bit Inkplate display.
 */
static void execEvents(ClientState* state, Inkplate* display) {
    if (state->checkBatteryTimer <= 0) {
        checkBattery(display);
        state->checkBatteryTimer = CHECK_BATTERY_TIMER;
    }

    if (state->requestTimeDs <= 0) {
        makeRequest(state, display);
    }

    if (state->screensaverTimeDs <= 0) {
        drawStatusImageById(display, state->screensaverId);
        state->screensaverTimeDs = INT_MAX;
    }
}

void clientLoop(ClientState* state, Inkplate* display) {
    #ifdef TEST_EINK
        aunit::TestRunner::run();
    #else
        long long prevTimeUs = esp_timer_get_time();
        int prevDelayTimeDs = 0;
        while (true) {
            bool isWiFiOn = WiFi.getMode() != WIFI_OFF;
            prevTimeUs = handleMeasuredElapsedTime(
                state, prevTimeUs, prevDelayTimeDs);
            prevDelayTimeDs = delayToNextEvent(state, isWiFiOn);
            execEvents(state, display);
        }
    #endif
}
