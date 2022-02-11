"""pywizlight integration push updates."""
import asyncio
import json
import logging
from typing import Callable, Dict, Optional, Tuple, cast

from pywizlight.models import DiscoveredBulb
from pywizlight.protocol import WizProtocol
from pywizlight.utils import create_udp_socket, generate_mac, get_source_ip, to_wiz_json

_LOGGER = logging.getLogger(__name__)

RESPOND_PORT = 38899
LISTEN_PORT = 38900


class PushManager:

    _manager = None

    @classmethod
    def get(cls):
        """Get push manager instance."""
        if cls._manager is None:
            cls._manager = cls()
        return cls._manager

    def __init__(self) -> None:
        """Initialize push manager."""
        self.push_transport: Optional[asyncio.DatagramTransport] = None
        self.push_protocol: Optional[WizProtocol] = None
        self.push_running = False
        self.discovery_callback: Optional[Callable[[DiscoveredBulb], None]] = None
        self.lock = asyncio.Lock()
        self.subscriptions: Dict[str, Callable[[Dict, Tuple[str, int]], None]] = {}
        self.register_msg: Optional[str] = None

    def set_discovery_callback(
        self, callback: Optional[Callable[[DiscoveredBulb], None]]
    ) -> None:
        """Set the callback to run when there is a new discovery."""
        self.discovery_callback = callback

    async def start(self, target_ip: str) -> bool:
        """Start listening for push updates on LISTEN_PORT if we are not already listening."""
        async with self.lock:
            if self.push_running:
                return True
            source_ip = get_source_ip(target_ip)
            if not source_ip:
                _LOGGER.warning(
                    "Could not determine source ip, falling back to polling"
                )
                return False
            try:
                sock = create_udp_socket(LISTEN_PORT)
            except OSError:
                _LOGGER.warning(
                    "Port %s is in use, cannot listen for push updates, falling back to polling",
                    LISTEN_PORT,
                )
                return False
            self.register_msg = to_wiz_json(
                {
                    "params": {
                        "phoneIp": source_ip,
                        "register": True,
                        "phoneMac": generate_mac(),
                    },
                    "method": "registration",
                }
            )
            push_transport_proto = (
                await asyncio.get_event_loop().create_datagram_endpoint(
                    lambda: WizProtocol(on_response=self._on_push),
                    sock=sock,
                )
            )
            self.push_transport = cast(
                asyncio.DatagramTransport, push_transport_proto[0]
            )
            self.push_protocol = cast(WizProtocol, push_transport_proto[1])
            self.push_running = True
            return True

    async def stop_if_no_subs(self) -> None:
        """Stop push updates if there are no subscriptions."""
        async with self.lock:
            if not self.push_running or self.subscriptions:
                return
            self.push_running = False
            self.discovery_callback = None
            if self.push_transport:
                self.push_transport.close()
                self.push_transport = None
                self.push_protocol = None

    def register(self, mac: str, callback: Callable) -> Callable:
        """Register the subscription for a given mac address."""
        self.subscriptions[mac] = callback

        def _cancel():
            del self.subscriptions[mac]
            asyncio.create_task(self.stop_if_no_subs())

        return _cancel

    def _on_push(self, message: bytes, addr: Tuple[str, int]) -> None:
        """Handle a response from the device."""
        _LOGGER.debug("%s: PUSH << %s", addr, message)
        if message == b"test":
            return  # App sends these to test connectivity
        try:
            resp = json.loads(message.decode())
        except json.JSONDecodeError:
            _LOGGER.error("%s: Sent invalid push message: %s", addr, message)
            return
        method = resp.get("method")
        mac = resp.get("params", {}).get("mac")
        # We used to send an response to `syncPilot` messages
        # but the devices keeps sending them even if we do not
        # so we no longer send them since all it effectively
        # does it generate additional network traffic.
        if method == "firstBeat" and self.discovery_callback:
            self.discovery_callback(DiscoveredBulb(addr[0], mac))
        if method == "syncPilot" and mac in self.subscriptions:
            self.subscriptions[mac](resp, addr)
