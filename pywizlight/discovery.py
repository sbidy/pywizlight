"""Discover bulbs in a network."""
import asyncio
import json
import logging
import socket

from pywizlight import wizlight

_LOGGER = logging.getLogger(__name__)


class DiscoveredBulb:
    """Representation of discovered bulb."""

    def __init__(self, ip_address, mac_address):
        """Initialize the discovered bulb."""
        self.ip_address = ip_address
        self.mac_address = mac_address

    @staticmethod
    def create_bulb_from_message(raw_addr, announce_message):
        """Create announce message."""
        ip_address = raw_addr[0]
        _LOGGER.debug("Found bulb with IP: {}".format(ip_address))
        bulb = DiscoveredBulb(
            ip_address=ip_address,
            mac_address=json.loads(announce_message)["result"]["mac"],
        )
        return bulb


class BulbRegistry(object):
    """Representation of the bulb registry."""

    def __init__(self):
        """Initialize the bulb registry."""
        self.bulbs_by_mac = {}

    def register(self, bulb):
        """Register a new bulb."""
        self.bulbs_by_mac[bulb.mac_address] = bulb

    def bulbs(self) -> list:
        """Get all present bulbs."""
        return list(self.bulbs_by_mac.values())


class BroadcastProtocol(object):
    """Protocol that sends an UDP broadcast message for bulb discovery."""

    def __init__(self, loop, registry, broadcast_address):
        """Init discovery function."""
        self.loop = loop
        self.registry = registry
        self.broadcast_address = broadcast_address

    def connection_made(self, transport):
        """Init connection to socket and register broadcasts."""
        self.transport = transport
        sock = transport.get_extra_info("socket")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast_registration()

    def broadcast_registration(self):
        """Send a registration method as UDP broadcast."""
        # Note: The IP and address we give the bulb here don't seem to matter for our
        # intents and purposes, so they're hardcoded to technically valid dummy data.
        # Fix for async problems if boardcast_registration is called twice! See #13.
        # dirty dirty hack
        try:
            register_method = r'{"method":"registration","params":{"phoneMac":"AAAAAAAAAAAA","register":false,"phoneIp":"1.2.3.4","id":"1"}}'  # noqa: E501
            self.transport.sendto(
                register_method.encode(), (self.broadcast_address, 38899)
            )
            self.loop.call_later(1, self.broadcast_registration)
        except AttributeError:
            pass

    def datagram_received(self, data, addr):
        """Receive data from broadcast."""
        _LOGGER.debug("Received data {} from IP address {}".format(data, addr))
        decoded_message = data.decode()
        if """"success":true""" in decoded_message:
            bulb = DiscoveredBulb.create_bulb_from_message(addr, decoded_message)
            self.registry.register(bulb)

    def connection_lost(self, exc):
        """Return connection error."""
        _LOGGER.debug("Closing UDP discovery")


async def find_wizlights(wait_time=5, broadcast_address="255.255.255.255") -> list:
    """Start discovery and return list of IPs of the bulbs."""
    registry = BulbRegistry()
    loop = asyncio.get_event_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: BroadcastProtocol(loop, registry, broadcast_address),
        local_addr=("0.0.0.0", 38899),
    )
    try:
        await asyncio.sleep(wait_time)
    finally:
        transport.close()
        bulbs = registry.bulbs()
        for bulb in bulbs:
            _LOGGER.info(
                "Discovered bulb {} with MAC {}".format(
                    bulb.ip_address, bulb.mac_address
                )
            )
        return bulbs


async def discover_lights(broadcast_space="255.255.255.255") -> list:
    """Find lights and return list with wizlight objects."""
    discovered_IPs = await find_wizlights(broadcast_address=broadcast_space)
    # empty list for adding bulbs
    bulbs = []
    # create light entities from register
    for entries in discovered_IPs:
        bulbs.append(wizlight(ip=entries.ip_address, mac=entries.mac_address))
    return bulbs
