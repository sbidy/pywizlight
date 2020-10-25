"""Exceptions for the pywizlight."""


class WizLightError(Exception):
    """General WizLightError exception occurred."""

    pass


class WizLightConnectionError(WizLightError):
    """When a connection error is encountered."""

    pass
