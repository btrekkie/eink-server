class Transport:
    """A transport mechanism for the client to communicate with a server.

    This is an abstract base class. For now, the only subclass is
    ``WebTransport``, but we could imagine adding ``BluetoothTransport``
    or ``SerialTransport`` in the future.
    """
    pass
