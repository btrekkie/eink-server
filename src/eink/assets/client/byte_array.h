#ifndef __BYTE_ARRAY_H__
#define __BYTE_ARRAY_H__

/**
 * An arbitrary block of data, starting at "data" and continuing for "length"
 * bytes.
 *
 * "data" is NULL if and only if "length" is 0. NULL data may signify what a
 * NULL value normally signifies (e.g. nothing or not applicable), or it may
 * indicate a zero-length buffer.
 */
typedef struct {
    void* data;
    int length;
} ByteArray;

/** Returns a ByteArray with the specified data and length. */
ByteArray createByteArray(void* data, int length);

#endif
