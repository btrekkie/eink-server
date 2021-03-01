from eink.server import Server


class TestServer(Server):
    """A ``Server`` object to use for testing."""

    def __init__(
            self, image, update_time, retry_times, screensaver_name,
            screensaver_time):
        """Initialize a new ``TestServer``.

        All of the ``Server`` methods that have the same names as one of
        the arguments return those arguments. The ``render()`` method
        returns ``image``.
        """
        self._image = image
        self._update_time = update_time
        self._retry_times = retry_times
        self._screensaver_name = screensaver_name
        self._screensaver_time = screensaver_time

    def render(self):
        return self._image

    def update_time(self):
        return self._update_time

    def retry_times(self):
        return self._retry_times

    def screensaver_name(self):
        return self._screensaver_name

    def screensaver_time(self):
        return self._screensaver_time
