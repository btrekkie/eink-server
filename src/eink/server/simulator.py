import io
import urllib.request

from PIL import Image

from .request import Request
from .response import Response


class Simulator:
    """Provides the ability to simulate a request to a server."""

    @staticmethod
    def connect(url):
        """Return the image returned when requesting the specified URL.

        This should be the URL of an e-ink server. The image indicates
        the content that the server is instructing the e-ink device to
        display.

        Arguments:
            url (str): The URL.

        Returns:
            Image: The image.
        """
        request_payload = Request().to_bytes()
        url_request = urllib.request.Request(
            url, data=request_payload,
            headers={'Content-Type': 'application/octet-stream'},
            method='POST')
        with urllib.request.urlopen(url_request) as url_response:
            response_payload = url_response.read()
        response = Response.create_from_bytes(response_payload)
        return Image.open(io.BytesIO(response.image_data))
