#include "define_test_eink.h"

#ifdef TEST_EINK

#include <limits.h>

#include <AUnit.h>

#include "client_state.h"

using namespace aunit;


void handleTimeElapsedDs(ClientState* state, int timeDs, int checkBatteryMult);

test(handleTimeElapsedDs) {
    ClientState state;
    state.requestTimeDs = 12000;
    state.screensaverTimeDs = INT_MAX;
    state.checkBatteryTimer = 300000;
    handleTimeElapsedDs(&state, 100, 10);
    assertEqual(state.requestTimeDs, 11900);
    assertEqual(state.screensaverTimeDs, INT_MAX);
    assertEqual(state.checkBatteryTimer, 299000);

    state.requestTimeDs = INT_MAX;
    state.screensaverTimeDs = 700;
    state.checkBatteryTimer = INT_MAX;
    handleTimeElapsedDs(&state, 300, 5);
    assertEqual(state.requestTimeDs, INT_MAX);
    assertEqual(state.screensaverTimeDs, 400);
    assertEqual(state.checkBatteryTimer, INT_MAX);

    state.requestTimeDs = 0;
    state.screensaverTimeDs = 40;
    state.checkBatteryTimer = 700;
    handleTimeElapsedDs(&state, 100, 10);
    assertEqual(state.requestTimeDs, 0);
    assertEqual(state.screensaverTimeDs, 0);
    assertEqual(state.checkBatteryTimer, 0);

    // Test overflow and near overflow
    state.checkBatteryTimer = 10000;
    handleTimeElapsedDs(&state, 100000000, 30);
    assertEqual(state.checkBatteryTimer, 0);
    state.checkBatteryTimer = 2147483646;
    handleTimeElapsedDs(&state, 214748364, 10);
    assertEqual(state.checkBatteryTimer, 6);
    state.checkBatteryTimer = 2147483646;
    handleTimeElapsedDs(&state, 214748365, 10);
    assertEqual(state.checkBatteryTimer, 0);
    state.checkBatteryTimer = 2147483646;
    handleTimeElapsedDs(&state, 357913940, 6);
    assertEqual(state.checkBatteryTimer, 6);
    state.checkBatteryTimer = 2147483646;
    handleTimeElapsedDs(&state, 357913941, 6);
    assertEqual(state.checkBatteryTimer, 0);
    state.checkBatteryTimer = 2147483646;
    handleTimeElapsedDs(&state, 357913942, 6);
    assertEqual(state.checkBatteryTimer, 0);
}

#endif
