from datetime import timedelta

from ..image import EinkGraphics
from ..image.image_data import ImageData
from .request import Request
from .response import Response
from .server_io import ServerIO


class Server:
    """Serves requests to update an e-ink display.

    ``Server`` is an abstract base class. Its basic function is to take
    a binary request payload, which is a request from an e-ink device,
    and to return a binary response payload containing updated content.
    Subclasses must override at least ``update_time()``,
    ``screensaver_time()``, and ``render()``.
    """

    # The maximum allowed return value for ``update_time()``,
    # ``screensaver_time()``, and ``retry_times()``: 365 days.
    MAX_TIME = timedelta(days=365)

    # The maximum value that can be stored in a signed 32-bit integer. This is
    # used to represent an infinite amount of time.
    _INT_MAX = 2 ** 31 - 1

    # The maximum number of request times. This is the maximum number of
    # elements in the C++ field ``ClientState.requestTimesDs``. See the
    # comments for that field.
    _MAX_REQUEST_TIMES = 20

    def update_time(self):
        """Return the time to wait before making another request to the server.

        This may not exceed 365 days. If the return value is ``None``,
        the e-ink device will never make another request to the server
        (unless rebooted).

        Returns:
            timedelta: The amount of time.
        """
        raise NotImplementedError('Subclasses must implement')

    def screensaver_time(self):
        """Return the amount of time to wait before displaying the screensaver.

        The idea is that if the e-ink device is unable to connect to the
        server for an extended period of time, then its content may
        become so stale that it is no longer worth showing. In this
        case, we display a full-screen "screensaver" image instead. See
        also ``screensaver_name()``.

        The return value may not exceed 365 days. It should be at least
        ``update_time()``. If the return value is ``None``, the e-ink
        device will never display a screensaver.

        Returns:
            timedelta: The amount of time.
        """
        raise NotImplementedError('Subclasses must implement')

    def render(self):
        """Return the ``Image`` for the e-ink device to display.

        This is the (updated) content that we wish to show. The image
        must have the same size as the display, after rotation (as in
        ``ClientConfig.set_rotation``). It may not have an alpha
        channel. We automatically convert it to a 3-bit grayscale image
        using ``EinkGraphics.round``.
        """
        raise NotImplementedError('Subclasses must implement')

    def retry_times(self):
        """Return the times for the client to retry the server.

        After the client receives this response, it will wait
        ``update_time()`` and then query the server for updated content.
        If this request fails, it will wait ``retry_times()[0]`` and
        then query the server again. If this also fails, it will retry
        after ``retry_times()[1]``, then ``retry_times()[2]``, and so
        on. When we reach the end of ``retry_times()``, it will continue
        to retry every ``retry_times()[-1]``.

        If ``update_time()`` is ``None``, then the return value of
        ``retry_times()`` is ignored. The retry times may not exceed 365
        days. A value of ``None`` indicates that we should stop
        retrying.

        There is a limit to the number of retry times the client can
        store. If the return value of ``retry_times()`` exceeds the
        limit (currently 19), we will adjust the retry times as
        appropriate to fit the limit.

        Returns:
            list<timedelta>: The retry intervals.
        """
        update_time = self.update_time()
        if update_time is not None:
            return [0.25 * update_time]
        else:
            return [None]

    def screensaver_name(self):
        """Return the name of the screensaver image in ``StatusImages``.

        The idea is that if the e-ink device is unable to connect to the
        server for an extended period of time, then its content may
        become so stale that it is no longer worth showing. In this
        case, we display a full-screen "screensaver" image instead.

        The screensaver is not an arbitrary image selected at runtime,
        but rather a reference to an image previously specified at
        compile time. The default return value is ``'connecting'``. See
        the comments for ``StatusImages``.

        It may be desirable to return a randomly selected image, e.g.
        ``random.choice(['sunrise', 'mountain', 'beach'])``.
        """
        return 'connecting'

    def exec(self, payload):
        """Execute a server request.

        This takes a binary request payload, which is a request from an
        e-ink device, and returns a binary response payload containing
        updated content.

        Arguments:
            payload (bytes): The request payload.

        Returns:
            bytes: The response payload.

        Raises:
            ServerError: If we detect that the specified value is not a
                correctly formatted e-ink request payload, or at least
                not one that this version of the library is able to
                handle.
        """
        Request.create_from_bytes(payload)
        request_times_ds = self._request_times_ds()
        screensaver_time_ds = self._interval_to_ds(self.screensaver_time())
        screensaver_id = ServerIO.image_id(self.screensaver_name())

        image = self.render()
        if EinkGraphics._has_alpha(image):
            raise ValueError(
                'Server.render() may not return an image with an alpha '
                'channel')
        image_data = ImageData.render_png(EinkGraphics.round(image))
        response = Response(
            image_data, request_times_ds, screensaver_id, screensaver_time_ds)
        return response.to_bytes()

    def _interval_to_ds(self, interval):
        """Convert the specified amount of time to tenths of a second.

        Return the integer number of tenths of a second nearest to the
        specified amount of time. The amount of time must be between 0
        and 365 days. Return ``_INT_MAX`` if ``interval`` is ``None``.

        Arguments:
            interval (timedelta): The amount of time.

        Returns:
            int: The amount of time, in tenths of a second.
        """
        if interval is None:
            return Server._INT_MAX
        elif not isinstance(interval, timedelta):
            raise TypeError('Time intervals must be instances of timedelta')
        elif interval < timedelta():
            raise ValueError('Time intervals may not be negative')
        elif interval > Server.MAX_TIME:
            raise ValueError('Time intervals may not be greater than 365 days')
        else:
            return int(10 * interval.total_seconds() + 0.5)

    def _request_times_ds(self):
        """Return the request times.

        Return the request times in tenths of a second, as in the C++
        field ``ClientState.requestTimesDs``.
        """
        request_times = [self.update_time()] + self.retry_times()
        if len(request_times) <= 1:
            raise ValueError(
                'Server.retry_times() may not return an empty list')
        request_times_ds = list([
            self._interval_to_ds(time) for time in request_times])
        for index, time_ds in enumerate(request_times_ds):
            if time_ds >= Server._INT_MAX:
                request_times_ds = request_times_ds[:index + 1]
                break

        if len(request_times_ds) > Server._MAX_REQUEST_TIMES:
            request_times_ds = (
                request_times_ds[:Server._MAX_REQUEST_TIMES - 1] +
                [request_times_ds[-1]])
        return request_times_ds
