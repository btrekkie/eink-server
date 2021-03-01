import io

from .errors import ServerError
from .server_io import ServerIO


class Request:
    """A parsed object representation of a request payload."""

    def to_bytes(self):
        """Return a request payload for this ``Request`` object.

        Returns:
            bytes: The payload.
        """
        result = io.BytesIO()
        result.write(ServerIO.HEADER)
        ServerIO.write_bytes(result, ServerIO.PROTOCOL_VERSION)
        return result.getvalue()

    @staticmethod
    def create_from_bytes(bytes_):
        """Return a ``Request`` representation of the specified payload.

        Arguments:
            bytes_ (bytes): The payload.

        Returns:
            Request: The request.

        Raises:
            ServerError: If we detect that the specified value is not a
                valid encoding of a request payload, or at least not one
                that this version of the library is able to handle.
        """
        input_ = io.BytesIO(bytes_)
        header = input_.read(len(ServerIO.HEADER))
        if header != ServerIO.HEADER:
            raise ServerError('Invalid request payload')
        version = ServerIO.read_bytes(input_)
        if version != ServerIO.PROTOCOL_VERSION:
            raise ServerError(
                'Version mismatch. The server is running a different version '
                'of the eink-server code than the Inkplate device is.')
        return Request()
