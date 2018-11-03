from __future__ import unicode_literals


class NXAPIError(Exception):
    """Generic NXAPI exception."""

    pass


class NXAPICommandError(NXAPIError):
    def __init__(self, command, message):
        self.command = command
        self.message = message

    def __repr__(self):
        return 'The command "{}" gave the error "{}".'.format(
            self.command, self.message
        )

    __str__ = __repr__


class NXAPIConnectionError(NXAPIError):
    """HTTP Post Connection Error."""

    pass


class NXAPIAuthError(NXAPIError):
    """HTTP Post Authentication Error."""

    pass


class NXAPIPostError(NXAPIError):
    """Exception occurred during HTTP POST to NX-API."""

    pass


class NXAPIXMLError(NXAPIError):
    """Exception occurred processing XML response from NX-API."""

    pass
