"""Tests for the Bulb API with a socket."""
import asyncio
import logging
from typing import AsyncGenerator, Optional, cast
from unittest.mock import patch

import pytest

from pywizlight import wizlight
from pywizlight.bulb import PilotParser
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.models import DiscoveredBulb
from pywizlight.protocol import WizProtocol
from pywizlight.push_manager import PushManager
from pywizlight.tests.fake_bulb import startup_bulb
from pywizlight.utils import to_wiz_json

logging.getLogger("pywizlight").setLevel(logging.DEBUG)


@pytest.fixture()
async def socket_push() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP10_SOCKET_06", firmware_version="1.25.0"
    )
    with patch("pywizlight.push_manager.RESPOND_PORT", port):
        bulb = wizlight(ip="127.0.0.1", port=port)
        yield bulb
        await bulb.async_close()
        shutdown()


@pytest.mark.asyncio
async def test_push_updates(socket_push: wizlight) -> None:
    """Test push updates."""
    bulb_type = await socket_push.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(color=False, color_tmp=False, effect=False, brightness=False),
        name="ESP10_SOCKET_06",
        kelvin_range=KelvinRange(max=2700, min=2700),
        bulb_type=BulbClass.SOCKET,
        fw_version="1.25.0",
        white_channels=2,
        white_to_color_ratio=20,
    )
    last_data = PilotParser({})
    data_event = asyncio.Event()

    def _on_push(data: PilotParser) -> None:
        nonlocal last_data
        last_data = data
        data_event.set()

    with patch("pywizlight.push_manager.LISTEN_PORT", 0):
        await socket_push.start_push(_on_push)

    push_manager = PushManager().get()
    push_port = push_manager.push_transport.get_extra_info("sockname")[1]

    push_in_transport_proto = await asyncio.get_event_loop().create_datagram_endpoint(
        lambda: WizProtocol(on_response=lambda resp, addr: None),
        remote_addr=("127.0.0.1", push_port),
    )
    push_transport = cast(asyncio.DatagramTransport, push_in_transport_proto[0])
    params = {
        "mac": "a8bb5006033d",
        "rssi": -71,
        "src": "hb",
        "mqttCd": 255,
        "ts": 1644593327,
        "state": False,
        "sceneId": 0,
        "temp": 6500,
        "dimming": 100,
    }

    push_transport.sendto(
        to_wiz_json(
            {
                "method": "syncPilot",
                "env": "pro",
                "params": params,
            }
        ).encode(),
        ("127.0.0.1", push_port),
    )
    await asyncio.wait_for(data_event.wait(), timeout=1)
    assert last_data.pilotResult == params
    update = await socket_push.updateState()
    assert update is not None
    assert update.pilotResult == params
    push_transport.close()


@pytest.mark.asyncio
async def test_discovery_by_firstbeat(
    socket_push: wizlight, caplog: pytest.LogCaptureFixture
) -> None:
    """Test discovery from first beat."""
    bulb_type = await socket_push.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(color=False, color_tmp=False, effect=False, brightness=False),
        name="ESP10_SOCKET_06",
        kelvin_range=KelvinRange(max=2700, min=2700),
        bulb_type=BulbClass.SOCKET,
        fw_version="1.25.0",
        white_channels=2,
        white_to_color_ratio=20,
    )
    last_discovery: Optional[DiscoveredBulb] = None
    discovery_event = asyncio.Event()

    def _on_discovery(discovery: DiscoveredBulb) -> None:
        nonlocal last_discovery
        last_discovery = discovery
        discovery_event.set()

    with patch("pywizlight.push_manager.LISTEN_PORT", 0):
        await socket_push.start_push(lambda data: None)

    assert socket_push.mac is not None
    socket_push.set_discovery_callback(_on_discovery)
    push_manager = PushManager().get()
    push_port = push_manager.push_transport.get_extra_info("sockname")[1]

    push_in_transport_proto = await asyncio.get_event_loop().create_datagram_endpoint(
        lambda: WizProtocol(on_response=lambda resp, addr: None),
        remote_addr=("127.0.0.1", push_port),
    )
    push_transport = cast(asyncio.DatagramTransport, push_in_transport_proto[0])
    push_transport.sendto(
        b"test",
        ("127.0.0.1", push_port),
    )
    push_transport.sendto(
        b"GARBAGE",
        ("127.0.0.1", push_port),
    )
    push_transport.sendto(
        to_wiz_json(
            {
                "method": "firstBeat",
                "env": "pro",
                "params": {"mac": socket_push.mac},
            }
        ).encode(),
        ("127.0.0.1", push_port),
    )
    await asyncio.wait_for(discovery_event.wait(), timeout=1)
    assert last_discovery is not None
    assert last_discovery == DiscoveredBulb("127.0.0.1", socket_push.mac)
    push_transport.close()
    assert "GARBAGE" in caplog.text
