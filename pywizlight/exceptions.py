"""Exceptions for the pywizlight."""


class WizLightError(Exception):
    """General WizLightError exception occurred."""

    pass


class WizLightConnectionError(WizLightError):
    """When a connection error is encountered."""

    pass


class WizLightTimeOutError(WizLightError):
    """When a connection error is encountered."""

    pass


class WizLightNotKnownBulb(WizLightError):
    """The bulb type is not known to the pywizlight."""

    pass
