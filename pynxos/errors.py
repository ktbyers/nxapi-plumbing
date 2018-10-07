from __future__ import unicode_literals


class NXAPIError(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return "{}: {}".format(self.__class__.__name__, self.message)

    __str__ = __repr__


class NXAPICommandError(NXAPIError):
    def __init__(self, command, message):
        self.command = command
        self.message = message

    def __repr__(self):
        return 'The command "{}" gave the error "{}".'.format(
            self.command, self.message
        )

    __str__ = __repr__


class NXAPIPostError(NXAPIError):
    """Status code returned by NXAPI indicates an error occurred."""
    pass
