"""Exceptions module."""


class A10SAError(Exception):
    """Base A10SA Script exception."""


class ParseError(A10SAError):
    """A script parsing error occured."""


class PlayerError(A10SAError):
    """Script player error occured."""


class DeviceError(PlayerError):
    """Player device error occured."""
