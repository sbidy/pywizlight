import json
import socket


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
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", listen_port))
    sock.setblocking(False)
    return sock


def create_udp_socket(listen_port: int) -> socket.socket:
    """Create a udp socket used for communicating with the device."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", listen_port))
    sock.setblocking(False)
    return sock
