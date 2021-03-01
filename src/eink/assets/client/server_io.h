#ifndef __SERVER_IO_H__
#define __SERVER_IO_H__

#include "byte_array.h"


/** A binary stream that accumulates data into a byte array. */
typedef struct {
    // The byte array storing the current data
    void* data;

    // The number of bytes in "data". "data" consists of "offset" used bytes
    // followed by length - offset unused bytes.
    int length;

    // The number of bytes of information we have stored at the beginning of
    // "data" so far
    int offset;
} Writer;

/**
 * Streams binary data from an input source. Unless otherwise specified, for all
 * reader methods, if we attempt to read an incorrectly encoded value or we
 * reach the end of the input stream before reading the desired value, the
 * behavior is unspecified, but it will not error.
 *
 * This is similar to Arduino's Stream class, but it suits our needs better. In
 * particular, it makes it possible to distinguish between when we are waiting
 * for more data and when we have passed the end of the stream.
 */
typedef struct {
    // Reads data from the input source, as in the readFunc argument to
    // initReader
    int (*readFunc)(void* data, int length, void* context);

    // A context value to pass to readFunc
    void* context;

    // Whether we have attempted to read past the end of the input stream
    bool passedEof;
} Reader;

/** Initializes "writer" to be a new Writer object. */
void initWriter(Writer* writer);

/**
 * Initializes "reader" to be a new Reader object.
 * @param reader The Reader object to initialize.
 * @param readFunc A function that reads data from the input source. This reads
 *     as many bytes as possible, up to "length" bytes, and stores them in
 *     "data". It receives "context" as its third argument. It returns the
 *     number of bytes that were read (possibly 0).
 * @param context The content argument to readFunc. readFunc is free to
 *     interpret the argument however it wants.
 */
void initReader(
    Reader* reader, int (*readFunc)(void* data, int length, void* context),
    void* context);

/**
 * Writes the specified bytes. All other Writer methods ultimately call this.
 * Contrast with writeByteArray. This is the inverse of readBytes.
 * @param writer The writer to write to.
 * @param data The bytes.
 * @param length The number of bytes to write.
 */
void writeBytes(Writer* writer, void* data, int length);

/**
 * Reads bytes from the specified reader. All other Reader methods ultimately
 * call this. Contrast with readByteArray. This is the inverse of writeBytes.
 * @param reader The reader.
 * @param data The buffer in which to store the bytes.
 * @param length The number of bytes to read. If we cannot read this number of
 *     bytes, then we read as many as we can.
 */
void readBytes(Reader* reader, void* data, int length);

/**
 * Writes the specified integer value to the specified writer. This is the
 * inverse of readInt. It duplicates the Python method ServerIO.write_int.
 */
void writeInt(Writer* writer, int value);

/**
 * Reads an integer value from the specified reader. This is the inverse of
 * writeInt. It duplicates the Python method ServerIO.read_int.
 */
int readInt(Reader* reader);

/**
 * Writes the specified ByteArray to the specified writer. Unlike writeBytes,
 * this does not assume prior knowledge of the number of bytes. It writes the
 * ByteArray so that the length can be reconstructed later. This is the inverse
 * of readByteArray. It duplicates the Python method ServerIO.write_bytes.
 */
void writeByteArray(Writer* writer, ByteArray data);

/**
 * Reads a ByteArray from the specified reader. Unlike readBytes, this does not
 * assume prior knowledge of the number of bytes. This is the inverse of
 * writeByteArray. It duplicates the Python method ServerIO.read_bytes.
 */
ByteArray readByteArray(Reader* reader);

/**
 * Returns the bytes written to the specified Writer and destroys the writer.
 */
ByteArray finishWriter(Writer* writer);

/**
 * Returns whether we have attempted to read past the end of the specified input
 * stream.
 */
bool readerPassedEof(Reader* reader);

#endif
