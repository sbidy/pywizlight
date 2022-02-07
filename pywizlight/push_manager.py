"""pywizlight integration push updates."""
import asyncio
import json
import logging
import random
import socket
from typing import Callable, Dict, Optional, Tuple, cast

from pywizlight.protocol import WizProtocol
from pywizlight.utils import to_wiz_json

_LOGGER = logging.getLogger(__name__)

RESPOND_PORT = 38899
LISTEN_PORT = 38900


def create_udp_socket(listen_port: int) -> socket.socket:
    """Create a udp socket used for communicating with the device."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", listen_port))
    sock.setblocking(False)
    return sock


def generate_mac():
    """Generates a fake mac address."""
    return "{}{}{}{}{}{}{}{}{}{}{}{}".format(
        *(random.SystemRandom().choice("0123456789abcdef") for _ in range(12))
    )


def get_source_ip(target_ip: str) -> Optional[str]:
    """Return the source ip that will reach target_ip."""
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    test_sock.setblocking(False)  # must be non-blocking for async
    try:
        test_sock.connect((target_ip, 1))
        return cast(str, test_sock.getsockname()[0])
    except Exception:  # pylint: disable=broad-except
        _LOGGER.debug(
            "The system could not auto detect the source ip for %s on your operating system",
            target_ip,
        )
        return None
    finally:
        test_sock.close()


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
        self.lock = asyncio.Lock()
        self.loop = asyncio.get_event_loop()
        self.subscriptions: Dict[str, Callable] = {}
        self.register_msg: Optional[str] = None

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
            push_transport_proto = await self.loop.create_datagram_endpoint(
                lambda: WizProtocol(on_response=self._on_push),
                sock=sock,
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
            if self.push_transport:
                self.push_transport.close()
                self.push_transport = None
                self.push_protocol = None

    def register(self, mac: str, callback: Callable) -> Callable:
        """Register the subscription for a given mac address."""
        self.subscriptions[mac] = callback

        def _cancel():
            del self.subscriptions[mac]
            asyncio.ensure_future(self.stop_if_no_subs())

        return _cancel

    def _on_push(self, message: bytes, addr: Tuple[str, int]) -> None:
        """Handle a response from the device."""
        _LOGGER.debug("%s: PUSH << %s", addr, message)
        try:
            resp = json.loads(message.decode())
        except json.JSONDecodeError:
            _LOGGER.error("%s: Sent invalid push message: %s", addr, message)
            return
        method = resp.get("method")
        mac = resp.get("params", {}).get("mac")
        if method != "syncPilot":
            return
        if self.push_transport:
            data = to_wiz_json({"method": "syncPilot", "result": {"mac": mac}}).encode()
            _LOGGER.debug("%s: PUSH ACK >> %s", (addr[0], RESPOND_PORT), data)
            self.push_transport.sendto(data, (addr[0], RESPOND_PORT))
        subscription = self.subscriptions.get(mac)
        if subscription:
            subscription(resp, addr)
