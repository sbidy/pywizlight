import json
import logging
import random
import socket
from typing import Optional, cast

_LOGGER = logging.getLogger(__name__)


def hex_to_percent(hex_value: float) -> float:
    """Convert hex 0-255 values to percent."""
    return round((hex_value / 255) * 100)


def percent_to_hex(percent: float) -> int:
    """Convert percent values 0-100 into hex 0-255."""
    return int(round((percent / 100) * 255))


def to_wiz_json(dump_obj):
    """Convert an object to wiz json."""
    return json.dumps(dump_obj, separators=(",", ":"))


def create_udp_broadcast_socket(listen_port: int) -> socket.socket:
    """Create a udp broadcast socket used for communicating with the device."""
    return _create_udp_socket(listen_port, reuseaddr=True, broadcast=True)


def create_udp_socket(listen_port: int) -> socket.socket:
    """Create a udp socket used for communicating with the device."""
    return _create_udp_socket(listen_port, reuseaddr=False, broadcast=False)


def _create_udp_socket(
    listen_port: int, reuseaddr: bool = False, broadcast: bool = False
) -> socket.socket:
    """Create a udp socket used for communicating with the device."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if reuseaddr:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if broadcast:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
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
