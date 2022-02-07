import json


def hex_to_percent(hex_value: float) -> float:
    """Convert hex 0-255 values to percent."""
    return round((hex_value / 255) * 100)


def percent_to_hex(percent: float) -> int:
    """Convert percent values 0-100 into hex 0-255."""
    return int(round((percent / 100) * 255))


def to_wiz_json(dump_obj):
    """Convert an object to wiz json."""
    return json.dumps(dump_obj, separators=(",", ":"))
