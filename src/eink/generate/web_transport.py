from .transport import Transport


class WebTransport(Transport):
    """A ``Transport`` for connecting to a web server.

    Each request is submitted as a POST request to a given URL, with the
    request payload as the POST body. The response is returned in the
    response payload.
    """

    # Private attributes:
    #
    # str _url - The server URL.

    def __init__(self, url):
        """Initialize a new ``WebTransport``.

        Arguments:
            url (str): The server URL.
        """
        self._url = url
