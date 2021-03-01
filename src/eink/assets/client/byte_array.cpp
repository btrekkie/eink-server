#include "byte_array.h"


ByteArray createByteArray(void* data, int length) {
    ByteArray result;
    result.data = data;
    result.length = length;
    return result;
}
