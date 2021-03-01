from .rotation import Rotation
from .transport import Transport


class ClientConfig:
    """The configuration information for generating the client's source code.
    """

    # Private attributes:
    #
    # Rotation _rotation - The rotation to use when drawing to the Inkplate
    #     device.
    # StatusImages _status_images - The status images. See the comments for
    #     StatusImages.
    # list<Transport> _transports - The servers the client should try to
    #     connect to, in order. Each time the client tries to fetch updated
    #     content, it tries each of the transports in order until it succeeds.
    # list<tuple<str, str>> _wi_fi_networks - The Wi-Fi networks the client may
    #     connect to, in descending order of preference. Each network is
    #     represented as a pair of the SSID and the password, if any.

    def __init__(self, transport, status_images):
        """Initialize a new ``ClientConfig``.

        Arguments:
            transport (Transport|list<Transport>): The server or servers
                the client should try to connect to. Each time the
                client tries to fetch updated content, it tries each of
                the transports in order until it succeeds.
            status_images (StatusImages): The status images. See the
                comments for ``StatusImages``.
        """
        if isinstance(transport, Transport):
            self._transports = [transport]
        else:
            self._transports = transport
        self._status_images = status_images
        self._wi_fi_networks = []
        self._rotation = Rotation.LANDSCAPE

    def add_wi_fi_network(self, ssid, password):
        """Add the specified Wi-Fi network to the list of networks.

        Add the specified Wi-Fi network to the list of networks the
        client may connect to. Networks from earlier calls to
        ``add_wi_fi_network`` are connected to in preference to networks
        from later calls.

        Arguments:
            ssid (str): The network's SSID.
            password (str): The network's password, if any.
        """
        self._wi_fi_networks.append((ssid, password))

    def set_rotation(self, rotation):
        """Set the rotation to use when drawing to the Inkplate device.

        The default is ``Rotation.LANDSCAPE``.

        Arguments:
            rotation (Rotation): The rotation.
        """
        self._rotation = rotation
