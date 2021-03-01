#include "define_test_eink.h"

#ifdef TEST_EINK

#include <string.h>

#include <AUnit.h>

#include "byte_array.h"
#include "server_io.h"

using namespace aunit;


/**
 * Context to use for test readers, as in the third argument to initReader. For
 * testing, we read the data directly from a provided buffer.
 */
typedef struct {
    // The data the reader returns
    void* data;

    // The number of bytes the reader returns
    int length;

    // The number of bytes we have read
    int offset;
} TestReaderContext;

test(Writer) {
    Writer writer;
    initWriter(&writer);
    ByteArray result1 = finishWriter(&writer);
    assertEqual(result1.data, NULL);
    assertEqual(result1.length, 0);

    char* data1 = (char*)"Hello, world!";
    char data2[1000];
    memset(data2, 42, 1000);

    initWriter(&writer);
    writeBytes(&writer, data1, 0);
    writeBytes(&writer, data1, 13);
    writeBytes(&writer, data2, 1000);
    ByteArray result2 = finishWriter(&writer);
    assertEqual(result2.length, 1013);
    assertEqual(memcmp(result2.data, data1, 13), 0);
    assertEqual(memcmp(result2.data + 13, data2, 1000), 0);
    free(result2.data);

    initWriter(&writer);
    for (int i = 0; i < 100; i++) {
        writeBytes(&writer, data1, 13);
    }
    ByteArray result3 = finishWriter(&writer);
    assertEqual(result3.length, 1300);
    for (int i = 0; i < 100; i++) {
        assertEqual(memcmp(result3.data + 13 * i, data1, 13), 0);
    }
    free(result3.data);
}

/**
 * The read function for test readers, as in the second argument to initReader.
 */
static int testReaderReadFunc(void* data, int length, void* context) {
    TestReaderContext* testReaderContext = (TestReaderContext*)context;
    int read;
    if (length <= testReaderContext->length - testReaderContext->offset) {
        read = length;
    } else {
        read = testReaderContext->length - testReaderContext->offset;
    }
    memcpy(data, testReaderContext->data + testReaderContext->offset, read);
    testReaderContext->offset += read;
    return read;
}

/**
 * Initializes "reader" to be a new test Reader object.
 * @param reader The Reader object to initialize.
 * @param testReaderContext The TestReaderContext object to use as context.
 * @param data The data the reader returns.
 * @param length The number of bytes the reader returns.
 */
static void initTestReader(
        Reader* reader, TestReaderContext* testReaderContext,
        void* data, int length) {
    testReaderContext->data = data;
    testReaderContext->length = length;
    testReaderContext->offset = 0;
    initReader(reader, testReaderReadFunc, testReaderContext);
}

test(Reader) {
    Reader reader;
    TestReaderContext testReaderContext;
    initTestReader(&reader, &testReaderContext, NULL, 0);
    assertFalse(readerPassedEof(&reader));
    char result1[10];
    memset(result1, 123, 10);
    readBytes(&reader, result1, 10);
    assertTrue(readerPassedEof(&reader));
    char data1[10];
    memset(data1, 123, 10);
    assertEqual(memcmp(result1, data1, 10), 0);
    readBytes(&reader, result1, 1);
    assertTrue(readerPassedEof(&reader));
    assertEqual(memcmp(result1, data1, 10), 0);

    char* data2 = (char*)"Hello, world!";

    char data3[1013];
    memcpy(data3, data2, 13);
    memset(data3 + 13, 42, 1000);
    initTestReader(&reader, &testReaderContext, data3, 1013);
    char result2[1013];
    readBytes(&reader, result2, 1013);
    assertEqual(memcmp(result2, data3, 1013), 0);
    assertFalse(readerPassedEof(&reader));
    readBytes(&reader, result2, 1);
    assertTrue(readerPassedEof(&reader));
    assertEqual(memcmp(result2, data3, 1013), 0);
    readBytes(&reader, result2, 500);
    assertTrue(readerPassedEof(&reader));
    assertEqual(memcmp(result2, data3, 1013), 0);

    char data4[1300];
    for (int i = 0; i < 100; i++) {
        memcpy(data4 + 13 * i, data2, 13);
    }
    initTestReader(&reader, &testReaderContext, data4, 1300);
    char result3[1170];
    readBytes(&reader, result3, 1170);
    for (int i = 0; i < 90; i++) {
        assertEqual(memcmp(result3 + 13 * i, data2, 13), 0);
    }
    assertFalse(readerPassedEof(&reader));
    readBytes(&reader, result3, 130);
    assertFalse(readerPassedEof(&reader));
    readBytes(&reader, result3, 1);
    assertTrue(readerPassedEof(&reader));
    readBytes(&reader, result3, 42);
    assertTrue(readerPassedEof(&reader));
}

/**
 * Tests writing and then reading the specified integer.
 * @param value The value.
 * @return Whether the test passed.
 */
static bool checkReadWriteInt(int value) {
    Writer writer;
    initWriter(&writer);
    writeInt(&writer, value);
    ByteArray byteArray = finishWriter(&writer);
    Reader reader;
    TestReaderContext testReaderContext;
    initTestReader(
        &reader, &testReaderContext, byteArray.data, byteArray.length);
    int result = readInt(&reader);
    if (byteArray.data != NULL) {
        free(byteArray.data);
    }
    return !readerPassedEof(&reader) && result == value;
}

test(readWriteInt) {
    assertTrue(checkReadWriteInt(73));
    assertTrue(checkReadWriteInt(0));
    assertTrue(checkReadWriteInt(-58));
    assertTrue(checkReadWriteInt(1234567890));
    assertTrue(checkReadWriteInt(-1098765432));
    assertTrue(checkReadWriteInt(INT_MAX));
    assertTrue(checkReadWriteInt(INT_MIN));
}

/**
 * Tests writing and then reading createByteArray(data, length).
 * @param data The data for the byte array.
 * @param length The length of the data for the byte array.
 * @return Whether the test passed.
 */
static bool checkReadWriteByteArray(void* data, int length) {
    Writer writer;
    initWriter(&writer);
    writeByteArray(&writer, createByteArray(data, length));
    ByteArray writerByteArray = finishWriter(&writer);
    Reader reader;
    TestReaderContext testReaderContext;
    initTestReader(
        &reader, &testReaderContext,
        writerByteArray.data, writerByteArray.length);
    ByteArray result = readByteArray(&reader);
    if (writerByteArray.data != NULL) {
        free(writerByteArray.data);
    }

    bool success;
    if (readerPassedEof(&reader)) {
        success = false;
    } else if (result.length != length) {
        success = false;
    } else if ((result.data == NULL) != (data == NULL)) {
        success = false;
    } else {
        success = memcmp(result.data, data, length) == 0;
    }

    if (result.data != NULL) {
        free(result.data);
    }
    return success;
}

test(readWriteByteArray) {
    assertTrue(checkReadWriteByteArray(NULL, 0));
    const char* data1 = "Hello, world!";
    assertTrue(checkReadWriteByteArray((void*)data1, 13));
    char data2[1000];
    memset(data2, 42, 1000);
    assertTrue(checkReadWriteByteArray(data2, 1000));
    assertTrue(checkReadWriteByteArray(data2, 1));
    memset(data2, 0, 1000);
    assertTrue(checkReadWriteByteArray(data2, 1000));
    assertTrue(checkReadWriteByteArray(data2, 1));
}

// Test that reading a value that is potentially invalidly encoded doesn't
// result in an error.
test(readNoErrors) {
    Reader reader;
    TestReaderContext testReaderContext;
    initTestReader(&reader, &testReaderContext, NULL, 0);
    readInt(&reader);
    initTestReader(&reader, &testReaderContext, NULL, 0);
    readByteArray(&reader);
    char data = 123;
    initTestReader(&reader, &testReaderContext, &data, 1);
    readInt(&reader);
    initTestReader(&reader, &testReaderContext, &data, 1);
    readByteArray(&reader);
}

#endif
