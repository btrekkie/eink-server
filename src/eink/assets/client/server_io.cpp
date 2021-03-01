#include <stdlib.h>
#include <string.h>

#include "server_io.h"


// The initial length of Writer.data
static const int INITIAL_WRITER_LENGTH = 64;

void initWriter(Writer* writer) {
    writer->data = malloc(INITIAL_WRITER_LENGTH);
    writer->length = INITIAL_WRITER_LENGTH;
    writer->offset = 0;
}

void initReader(
        Reader* reader,
        int (*readFunc)(void* data, int length, void* context), void* context) {
    reader->readFunc = readFunc;
    reader->context = context;
    reader->passedEof = false;
}

/** Ensures that writer->length >= length. */
static void ensureWriterLength(Writer* writer, int length) {
    if (writer->length < length) {
        int newLength = 2 * length;
        void* newData = malloc(newLength);
        memcpy(newData, writer->data, writer->offset);
        free(writer->data);
        writer->data = newData;
        writer->length = newLength;
    }
}

void writeBytes(Writer* writer, void* data, int length) {
    ensureWriterLength(writer, writer->offset + length);
    memcpy(writer->data + writer->offset, data, length);
    writer->offset += length;
}

void readBytes(Reader* reader, void* data, int length) {
    if (length > 0 && !reader->passedEof) {
        int read = reader->readFunc(data, length, reader->context);
        if (read < length) {
            reader->passedEof = true;
        }
    }
}

void writeInt(Writer* writer, int value) {
    char bytes[4];
    bytes[0] = (char)value;
    bytes[1] = (char)(value >> 8);
    bytes[2] = (char)(value >> 16);
    bytes[3] = (char)(value >> 24);
    writeBytes(writer, bytes, 4);
}

int readInt(Reader* reader) {
    char bytes[4];
    readBytes(reader, bytes, 4);
    return
        (int)bytes[0] | (int)bytes[1] << 8 | (int)bytes[2] << 16 |
        (int)bytes[3] << 24;
}

void writeByteArray(Writer* writer, ByteArray data) {
    writeInt(writer, data.length);
    writeBytes(writer, data.data, data.length);
}

ByteArray readByteArray(Reader* reader) {
    ByteArray data;
    data.length = readInt(reader);
    if (data.length > 0) {
        data.data = malloc(data.length);
        readBytes(reader, data.data, data.length);
    } else {
        data.data = NULL;
        data.length = 0;
    }
    return data;
}

ByteArray finishWriter(Writer* writer) {
    ByteArray data;
    if (writer->offset > 0) {
        data.data = writer->data;
        data.length = writer->offset;
    } else {
        data.data = NULL;
        data.length = 0;
        free(writer->data);
    }
    return data;
}

bool readerPassedEof(Reader* reader) {
    return reader->passedEof;
}
