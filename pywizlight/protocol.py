"""pywizlight integration protocol."""
import asyncio
import logging
from typing import Callable, Optional, Tuple

_LOGGER = logging.getLogger(__name__)


class WizProtocol(asyncio.DatagramProtocol):
    def __init__(
        self,
        on_response: Callable[[bytes, Tuple[str, int]], None],
        on_error: Optional[Callable[[Optional[Exception]], None]] = None,
    ) -> None:
        """Init the protocol."""
        self.transport = None
        self.on_response = on_response
        self.on_error = on_error

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Trigger on_response."""
        self.on_response(data, addr)

    def error_received(self, ex: Optional[Exception]) -> None:
        """Handle error."""
        _LOGGER.debug("WizProtocol error: %s", ex)
        if self.on_error is not None:
            self.on_error(ex)

    def connection_lost(self, ex: Optional[Exception]) -> None:
        """The connection is lost."""
        _LOGGER.debug("WizProtocol connection lost: %s", ex)
