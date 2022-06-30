from datetime import timedelta
import io
import unittest

from PIL import Image

from eink.server import Server
from eink.server.request import Request
from eink.server.response import Response
from eink.server.server_io import ServerIO
from .test_server import TestServer


class ServerTest(unittest.TestCase):
    """Tests the ``Server`` class."""

    def _normalize_request_times(self, request_times_ds):
        """Return a normalized representation of ``request_times_ds``.

        Return a normalized representation of the specified
        ``Response.request_times_ds`` value. This is the shortest
        request times value that is equivalent to ``request_times_ds``.
        For example, ``_normalize_request_times([100, 100])`` returns
        ``[100]``.
        """
        for index, time_ds in enumerate(request_times_ds):
            if time_ds >= Server._INT_MAX:
                return request_times_ds[:index + 1]

        i = len(request_times_ds) - 2
        while i >= 0:
            if request_times_ds[i] != request_times_ds[-1]:
                break
            i -= 1
        return request_times_ds[:i + 2]

    def _are_request_times_equal(self, request_times_ds1, request_times_ds2):
        """Return whether the specified request times are equivalent.

        Return whether the specified ``Response.request_times_ds``
        values are equivalent, meaning that they indicate the same
        sequence of wait times. For example,
        ``_are_request_times_equal([100], [100, 100])`` returns
        ``True``.
        """
        return (
            self._normalize_request_times(request_times_ds1) ==
            self._normalize_request_times(request_times_ds2))

    def test_exec(self):
        """Test ``Server.exec``."""
        pixels = []
        for y in range(16):
            for x in range(16):
                pixels.append((8 * x, 255 - 8 * x, 8 * y))
        image1 = Image.new('RGB', (16, 16))
        image1.putdata(pixels)

        server1 = TestServer(
            image1, timedelta(minutes=5),
            [
                timedelta(minutes=2), timedelta(minutes=5),
                timedelta(minutes=10), timedelta(minutes=10)],
            'mountain', None)
        request_bytes = Request().to_bytes()
        response1 = Response.create_from_bytes(server1.exec(request_bytes))
        Image.open(io.BytesIO(response1.image_data))
        self.assertTrue(
            self._are_request_times_equal(
                [3000, 1200, 3000, 6000], response1.request_times_ds))
        self.assertEqual(
            ServerIO.image_id('mountain'), response1.screensaver_id)
        self.assertEqual(Server._INT_MAX, response1.screensaver_time_ds)

        image2 = Image.new('L', (20, 20), 73)
        server2 = TestServer(
            image2, None, [timedelta(minutes=5)], 'sunrise',
            timedelta(minutes=20))
        response2 = Response.create_from_bytes(server2.exec(request_bytes))
        response_image = Image.open(io.BytesIO(response2.image_data))
        self.assertEqual(
            [73] * 400, list(response_image.convert('L').getdata()))
        self.assertTrue(
            self._are_request_times_equal(
                [Server._INT_MAX], response2.request_times_ds))
        self.assertEqual(
            ServerIO.image_id('sunrise'), response2.screensaver_id)
        self.assertEqual(12000, response2.screensaver_time_ds)

        server3 = TestServer(
            image1, timedelta(minutes=10), [None], 'mountain',
            timedelta(days=365))
        response3 = Response.create_from_bytes(server3.exec(request_bytes))
        Image.open(io.BytesIO(response3.image_data))
        self.assertTrue(
            self._are_request_times_equal(
                [6000, Server._INT_MAX], response3.request_times_ds))
        self.assertEqual(
            ServerIO.image_id('mountain'), response3.screensaver_id)
        self.assertEqual(
            round(10 * timedelta(days=365).total_seconds()),
            response3.screensaver_time_ds)

        server4 = TestServer(image1, None, [None], 'mountain', None)
        response4 = Response.create_from_bytes(server4.exec(request_bytes))
        Image.open(io.BytesIO(response4.image_data))
        self.assertTrue(
            self._are_request_times_equal(
                [Server._INT_MAX], response4.request_times_ds))
        self.assertEqual(
            ServerIO.image_id('mountain'), response4.screensaver_id)
        self.assertEqual(Server._INT_MAX, response4.screensaver_time_ds)

        request_times = list([timedelta(seconds=i) for i in range(10000)])
        server5 = TestServer(
            image1, timedelta(), request_times, 'mountain', None)
        response5 = Response.create_from_bytes(server5.exec(request_bytes))
        Image.open(io.BytesIO(response5.image_data))
        for time_ds in response5.request_times_ds:
            self.assertTrue(0 <= time_ds <= 99990)
        self.assertEqual(
            ServerIO.image_id('mountain'), response5.screensaver_id)
        self.assertEqual(Server._INT_MAX, response5.screensaver_time_ds)
