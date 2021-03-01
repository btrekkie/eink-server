import io

from .server_io import ServerIO


class Response:
    """A parsed object representation of a response payload.

    Public attributes:

    bytes image_data - The contents of the PNG image file that the e-ink
        device should display.
    list<int> request_times_ds - The amount of time between requests to
        the server, in tenths of a second, as in the C++ field
        ``ClientState.requestTimesDs``.
    bytes screensaver_id - The ID of the screensaver image, as in
        ``ServerIO.image_id``.
    int screensaver_time_ds - The amount of time to wait before
        displaying the screensaver, in tenths of a second. If this is
        ``Server._INT_MAX``, we will never display a screensaver.
    """

    def __init__(
            self, image_data, request_times_ds, screensaver_id,
            screensaver_time_ds):
        self.image_data = image_data
        self.request_times_ds = request_times_ds
        self.screensaver_id = screensaver_id
        self.screensaver_time_ds = screensaver_time_ds

    def to_bytes(self):
        """Return a response payload for this ``Response`` object.

        Returns:
            bytes: The payload.
        """
        result = io.BytesIO()
        result.write(ServerIO.HEADER)

        ServerIO.write_int(result, len(self.request_times_ds))
        for request_time_ds in self.request_times_ds:
            ServerIO.write_int(result, request_time_ds)

        result.write(self.screensaver_id)
        ServerIO.write_int(result, self.screensaver_time_ds)

        ServerIO.write_int(result, len(self.image_data))
        result.write(self.image_data)
        return result.getvalue()

    @staticmethod
    def create_from_bytes(bytes_):
        """Return a ``Response`` representation of the specified payload.

        Arguments:
            bytes_ (bytes): The payload.

        Returns:
            Response: The response.
        """
        input_ = io.BytesIO(bytes_)
        header = input_.read(len(ServerIO.HEADER))
        if header != ServerIO.HEADER:
            raise ValueError('Invalid response payload')

        request_times_count = ServerIO.read_int(input_)
        request_times_ds = []
        for _ in range(request_times_count):
            request_times_ds.append(ServerIO.read_int(input_))

        screensaver_id = input_.read(ServerIO.STATUS_IMAGE_ID_LENGTH)
        screensaver_time_ds = ServerIO.read_int(input_)

        image_data_length = ServerIO.read_int(input_)
        image_data = input_.read(image_data_length)
        if len(image_data) < image_data_length:
            raise ValueError('Invalid response payload')
        return Response(
            image_data, request_times_ds, screensaver_id, screensaver_time_ds)
