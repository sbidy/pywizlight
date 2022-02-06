"""Discover bulbs in a network."""
import asyncio
import dataclasses
import json
import logging
import socket
from asyncio import DatagramTransport, BaseTransport, AbstractEventLoop, Future
from typing import TYPE_CHECKING, Dict, List, Tuple, Optional, Any

from pywizlight import wizlight

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class DiscoveredBulb:
    """Representation of discovered bulb."""

    ip_address: str
    mac_address: str

    @staticmethod
    def create_bulb_from_message(
        raw_addr: Tuple[str, int], announce_message: str
    ) -> "DiscoveredBulb":
        """Create announce message."""
        ip_address = raw_addr[0]
        _LOGGER.debug(f"Found bulb with IP: {ip_address}")
        return DiscoveredBulb(
            ip_address=ip_address,
            mac_address=json.loads(announce_message)["result"]["mac"],
        )


@dataclasses.dataclass
class BulbRegistry:
    """Representation of the bulb registry."""

    bulbs_by_mac: Dict[str, DiscoveredBulb] = dataclasses.field(default_factory=dict)

    def register(self, bulb: DiscoveredBulb) -> None:
        """Register a new bulb."""
        self.bulbs_by_mac[bulb.mac_address] = bulb

    def bulbs(self) -> List[DiscoveredBulb]:
        """Get all present bulbs."""
        return list(self.bulbs_by_mac.values())


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
        if TYPE_CHECKING:
            # TODO: if this is made a runtime check, it needs some changes (see #94)
            assert isinstance(
                transport, BaseTransport
            )  # Required to keep this liskov-safe
        self.transport = transport  # type: ignore
        sock = transport.get_extra_info("socket")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast_registration()

    def broadcast_registration(self) -> None:
        """Send a registration method as UDP broadcast."""
        # Note: The IP and address we give the bulb here don't seem to matter for our
        # intents and purposes, so they're hardcoded to technically valid dummy data.
        # Fix for async problems if broaddcast_registration is called twice! See #13.
        # dirty dirty hack
        if not self.transport:
            return
        try:
            register_method = r'{"method":"registration","params":{"phoneMac":"AAAAAAAAAAAA","register":false,"phoneIp":"1.2.3.4","id":"1"}}'  # noqa: E501
            self.transport.sendto(
                register_method.encode(), (self.broadcast_address, 38899)
            )
            self.loop.call_later(1, self.broadcast_registration)
        except AttributeError:
            pass

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Receive data from broadcast."""
        _LOGGER.debug(f"Received data {data!r} from IP address {addr}")
        decoded_message = data.decode()
        if """"success":true""" in decoded_message:
            bulb = DiscoveredBulb.create_bulb_from_message(addr, decoded_message)
            self.registry.register(bulb)

    def connection_lost(self, exc: Any) -> None:
        """Return connection error."""
        _LOGGER.debug("Closing UDP discovery")
        if exc is None:
            self.future.set_result(None)
        else:
            self.future.set_exception(exc)


async def find_wizlights(
    wait_time: float = 5, broadcast_address: str = "255.255.255.255"
) -> List[DiscoveredBulb]:
    """Start discovery and return list of IPs of the bulbs."""
    registry = BulbRegistry()
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: BroadcastProtocol(loop, registry, broadcast_address, future),
        local_addr=("0.0.0.0", 38899),
    )
    try:
        await asyncio.sleep(wait_time)
    finally:
        transport.close()
        await future
        bulbs = registry.bulbs()
        for bulb in bulbs:
            _LOGGER.info(
                f"Discovered bulb {bulb.ip_address} with MAC {bulb.mac_address}"
            )
        return bulbs


async def discover_lights(broadcast_space: str = "255.255.255.255") -> List[wizlight]:
    """Find lights and return list with wizlight objects."""
    discovered_IPs = await find_wizlights(broadcast_address=broadcast_space)
    # empty list for adding bulbs
    bulbs = []
    # create light entities from register
    for entries in discovered_IPs:
        bulbs.append(wizlight(ip=entries.ip_address, mac=entries.mac_address))
    return bulbs
