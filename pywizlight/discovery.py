"""Discover bulbs in a network."""
import asyncio
import json
import logging
from asyncio import AbstractEventLoop, BaseTransport, DatagramTransport, Future
from typing import Any, List, Optional, Tuple, cast

from pywizlight import wizlight
from pywizlight.models import BulbRegistry, DiscoveredBulb
from pywizlight.utils import create_udp_broadcast_socket

_LOGGER = logging.getLogger(__name__)

PORT = 38899
DEFAULT_WAIT_TIME = 5.0

# Note: The IP and address we give the bulb does not matter because
# we have register set to false which is telling the bulb to remove
# the registration
REGISTER_MESSAGE = b'{"method":"registration","params":{"phoneMac":"AAAAAAAAAAAA","register":false,"phoneIp":"1.2.3.4","id":"1"}}'  # noqa: E501


class BroadcastProtocol(asyncio.DatagramProtocol):
    """Protocol that sends an UDP broadcast message for bulb discovery."""

    def __init__(
        self,
        loop: AbstractEventLoop,
        registry: BulbRegistry,
        broadcast_address: str,
        future: Future,
    ) -> None:
        """Init discovery function."""
        self.loop = loop
        self.registry = registry
        self.broadcast_address = broadcast_address
        self.transport: Optional[DatagramTransport] = None
        self.future = future

    def connection_made(self, transport: BaseTransport) -> None:
        """Init connection to socket and register broadcasts."""
        self.transport = cast(DatagramTransport, transport)
        self.broadcast_registration()

    def broadcast_registration(self) -> None:
        """Send a registration method as UDP broadcast."""
        if not self.transport:
            return
        self.transport.sendto(REGISTER_MESSAGE, (self.broadcast_address, PORT))
        self.loop.call_later(1, self.broadcast_registration)

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Receive data from broadcast."""
        _LOGGER.debug(f"Received data {data!r} from IP address {addr}")
        try:
            resp = json.loads(data.decode())
        except json.JSONDecodeError:
            _LOGGER.error("%s: Sent invalid message: %s", addr, data)
            return
        mac = resp.get("result", {}).get("mac")
        if mac:
            _LOGGER.debug("Found bulb with IP: %s and MAC: %s", addr[0], mac)
            self.registry.register(DiscoveredBulb(addr[0], mac))

    def connection_lost(self, exc: Any) -> None:
        """Return connection error."""
        _LOGGER.debug("Closing UDP discovery")
        if exc is None:
            self.future.set_result(None)
        else:
            self.future.set_exception(exc)
        self.transport = None


async def find_wizlights(
    wait_time: float = DEFAULT_WAIT_TIME, broadcast_address: str = "255.255.255.255"
) -> List[DiscoveredBulb]:
    """Start discovery and return list of IPs of the bulbs."""
    registry = BulbRegistry()
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: BroadcastProtocol(loop, registry, broadcast_address, future),
        sock=create_udp_broadcast_socket(PORT),
    )
    await asyncio.sleep(wait_time)
    transport.close()
    await future
    bulbs = registry.bulbs()
    for bulb in bulbs:
        _LOGGER.info(f"Discovered bulb {bulb.ip_address} with MAC {bulb.mac_address}")
    return bulbs


async def discover_lights(
    broadcast_space: str = "255.255.255.255", wait_time: float = DEFAULT_WAIT_TIME
) -> List[wizlight]:
    """Find lights and return list with wizlight objects."""
    discovered_IPs = await find_wizlights(
        wait_time=wait_time, broadcast_address=broadcast_space
    )
    return [
        wizlight(ip=entry.ip_address, mac=entry.mac_address) for entry in discovered_IPs
    ]
