import hashlib
import struct


class ServerIO:
    """Provides static methods and fields pertaining to client communication.

    Unless otherwise specified, for all read methods, if we attempt to
    read an incorrectly encoded value or we reach the end of the file
    before reading the desired value, the behavior is unspecified.
    """

    # The bytes at the beginning of every payload sent to or from the server.
    # We use this as a crude way of checking whether we are dealing with a
    # correctly formatted payload.
    HEADER = b'\x89INK{\x98 $\x97\xaf\x80d'

    # Bytes identifying the version of the protocol that this program uses to
    # communicate with the client. Whenever the protocol changes, we should
    # change the version.
    PROTOCOL_VERSION = b'2021-02-27T23:07:41Z'

    # The length of the return value of ``image_id()``
    STATUS_IMAGE_ID_LENGTH = 32

    @staticmethod
    def write_int(output, value):
        """Write the specified 32-bit signed integer value to ``output``.

        This is the inverse of ``read_int``. It duplicates the C++
        method ``writeInt``.

        Arguments:
            output (file): The file to write the value to.
            value (int): The value to write.
        """
        output.write(struct.pack('<i', value))

    @staticmethod
    def read_int(input_):
        """Read a 32-bit signed integer value from the specified file.

        This is the inverse of ``write_int``. It duplicates the C++
        method ``readInt``.

        Arguments:
            input_ (file): The file to read the value from.

        Returns:
            int: The value.
        """
        bytes_ = input_.read(4)
        if len(bytes_) >= 4:
            return struct.unpack('<i', bytes_)[0]
        else:
            return 0

    @staticmethod
    def write_bytes(output, bytes_):
        """Write the specified ``bytes`` to the specified file.

        Unlike ``output.write(bytes_)``, this does not assume prior
        knowledge of the number of bytes. It writes the ``bytes`` so
        that the length can be reconstructed later. This is the inverse
        of ``read_bytes``. It duplicates the C++ method
        ``writeByteArray``.

        Arguments:
            output (file): The file to write the value to.
            bytes_ (bytes): The bytes to write.
        """
        ServerIO.write_int(output, len(bytes_))
        output.write(bytes_)

    @staticmethod
    def read_bytes(input_):
        """Read a ``bytes`` object from the specified file.

        Unlike calling ``input_.read``, this does not assume prior
        knowledge of the number of bytes. This is the inverse of
        ``write_bytes``. It duplicates the C++ method ``readByteArray``.

        Arguments:
            input_ (file): The file to bytes the value from.

        Returns:
            bytes: The bytes.
        """
        length = ServerIO.read_int(input_)
        bytes_ = input_.read(length)
        if len(bytes_) < length:
            raise ValueError('Not enough bytes available')
        return bytes_

    @staticmethod
    def image_id(name):
        """Return an ID identifying the status image with the specified name.

        See the comments for ``StatusImage``. The return value is a hash
        of the name. It has length ``STATUS_IMAGE_ID_LENGTH``. By
        internally identifying images using IDs rather than names, we
        avoid the need to worry about long names, variable-length names,
        and non-ASCII characters.

        Arguments:
            name (str): The name of the status image.

        Returns:
            bytes: The image ID.
        """
        digest = hashlib.sha256()
        digest.update(name.encode())
        return digest.digest()
