"""Tests for recovering the bulb connection after network changes."""

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, Tuple, cast
from unittest.mock import AsyncMock, patch

import pytest

from pywizlight import wizlight
from pywizlight.exceptions import WizLightConnectionError, WizLightTimeOutError
from pywizlight.push_manager import PushManager

NEW_SOURCE_IP = "192.0.2.20"


class FakeDevice(asyncio.DatagramProtocol):
    """A device that answers every request while responding is set."""

    def __init__(self) -> None:
        self.transport: asyncio.DatagramTransport
        self.responding = True

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = cast(asyncio.DatagramTransport, transport)

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        if not self.responding:
            return
        method = json.loads(data)["method"]
        response = {"method": method, "env": "pro", "result": {"success": True}}
        self.transport.sendto(json.dumps(response).encode(), addr)


@pytest.fixture()
async def device() -> AsyncGenerator[FakeDevice, None]:
    _, protocol = await asyncio.get_running_loop().create_datagram_endpoint(
        FakeDevice, local_addr=("127.0.0.1", 0)
    )
    device = cast(FakeDevice, protocol)
    yield device
    device.transport.close()


@pytest.fixture()
async def bulb(device: FakeDevice) -> AsyncGenerator[wizlight, None]:
    bulb = wizlight(ip="127.0.0.1", port=device.transport.get_extra_info("sockname")[1])
    with patch("pywizlight.bulb.FIRST_SEND_INTERVAL", 0.01), patch(
        "pywizlight.bulb.TIMEOUT", 0.05
    ):
        yield bulb
    await bulb.async_close()


@pytest.mark.asyncio
async def test_reuses_connection_when_route_unchanged(bulb: wizlight) -> None:
    """Test a healthy connection is reused while the source address is unchanged."""
    await bulb.getBulbConfig()
    transport = bulb.transport
    await bulb.getBulbConfig()
    assert bulb.transport is transport


@pytest.mark.asyncio
async def test_reconnects_when_source_address_changes(bulb: wizlight) -> None:
    """Test the connection is replaced when the route uses a new source address."""
    await bulb.getBulbConfig()
    old_transport = bulb.transport
    assert old_transport is not None
    with patch("pywizlight.bulb.get_source_ip", return_value=NEW_SOURCE_IP):
        await bulb.getBulbConfig()
    assert old_transport.is_closing()
    assert bulb.transport is not None and bulb.transport is not old_transport


@pytest.mark.asyncio
async def test_keeps_connection_when_source_unknown(bulb: wizlight) -> None:
    """Test the connection is kept when the route cannot be determined."""
    await bulb.getBulbConfig()
    transport = bulb.transport
    with patch("pywizlight.bulb.get_source_ip", return_value=None):
        await bulb.getBulbConfig()
    assert bulb.transport is transport


@pytest.mark.asyncio
async def test_reconnects_when_transport_closed(bulb: wizlight) -> None:
    """Test a closed transport is not reused."""
    await bulb.getBulbConfig()
    old_transport = bulb.transport
    assert old_transport is not None
    old_transport.close()
    await bulb.getBulbConfig()
    assert bulb.transport is not None and bulb.transport is not old_transport


@pytest.mark.asyncio
async def test_timeout_discards_connection(bulb: wizlight, device: FakeDevice) -> None:
    """Test a timed out connection is replaced while keeping push subscriptions."""
    bulb.mac = "a8bb5006033d"
    with patch("pywizlight.push_manager.LISTEN_PORT", 0):
        assert await bulb.start_push(lambda data: None)
    await bulb.getBulbConfig()
    old_transport = bulb.transport
    assert old_transport is not None

    device.responding = False
    # Python 3.11+ timeouts are OSErrors, which send() reports as connection errors
    with pytest.raises((WizLightConnectionError, WizLightTimeOutError)):
        await bulb.getBulbConfig()
    assert old_transport.is_closing()
    assert bulb.transport is None
    assert bulb.mac in PushManager().get().subscriptions

    device.responding = True
    await bulb.getBulbConfig()
    assert bulb.transport is not None and bulb.transport is not old_transport


@pytest.mark.asyncio
async def test_connection_error_discards_connection(bulb: wizlight) -> None:
    """Test a connection that reported an error is replaced."""
    await bulb.getBulbConfig()
    old_transport = bulb.transport
    assert old_transport is not None and bulb.protocol is not None
    with patch.object(
        old_transport,
        "sendto",
        side_effect=lambda *_: bulb.protocol.error_received(OSError("unreachable")),
    ):
        with pytest.raises(WizLightConnectionError):
            await bulb.getBulbConfig()
    assert old_transport.is_closing()
    await bulb.getBulbConfig()
    assert bulb.transport is not None and bulb.transport is not old_transport


@pytest.mark.asyncio
async def test_cancelled_send_keeps_connection(
    bulb: wizlight, device: FakeDevice
) -> None:
    """Test cancelling a request does not discard the connection or hold the lock."""
    await bulb.getBulbConfig()
    transport = bulb.transport
    device.responding = False
    task = asyncio.create_task(bulb.getBulbConfig())
    await asyncio.sleep(0.02)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    device.responding = True
    await bulb.getBulbConfig()
    assert bulb.transport is transport


@pytest.mark.asyncio
async def test_concurrent_sends_replace_connection_once(bulb: wizlight) -> None:
    """Test concurrent requests after a source change share one new connection."""
    await bulb.getBulbConfig()
    old_transport = bulb.transport
    loop = asyncio.get_running_loop()
    with patch(
        "pywizlight.bulb.get_source_ip",
        side_effect=[NEW_SOURCE_IP, "127.0.0.1", "127.0.0.1"],
    ), patch.object(
        loop, "create_datagram_endpoint", wraps=loop.create_datagram_endpoint
    ) as create_endpoint:
        await asyncio.gather(bulb.getBulbConfig(), bulb.getBulbConfig())
    assert create_endpoint.call_count == 1
    assert bulb.transport is not None and bulb.transport is not old_transport


@pytest.mark.asyncio
async def test_registration_uses_current_source_ip(bulb: wizlight) -> None:
    """Test push registration advertises the current source address."""
    message: Dict[str, Any] = {
        "method": "registration",
        "params": {"phoneIp": "192.0.2.10", "register": True, "phoneMac": "aabb"},
    }
    with patch(
        "pywizlight.bulb.get_source_ip", return_value=NEW_SOURCE_IP
    ), patch.object(bulb, "send", AsyncMock()) as send:
        await bulb._async_send_register(message)
    assert send.call_args.args[0]["params"] == {
        "phoneIp": NEW_SOURCE_IP,
        "register": True,
        "phoneMac": "aabb",
    }
    assert message["params"]["phoneIp"] == "192.0.2.10"


@pytest.mark.asyncio
async def test_registration_falls_back_when_source_unknown(bulb: wizlight) -> None:
    """Test push registration keeps the original address when the route is unknown."""
    message: Dict[str, Any] = {
        "method": "registration",
        "params": {"phoneIp": "192.0.2.10", "register": True, "phoneMac": "aabb"},
    }
    with patch("pywizlight.bulb.get_source_ip", return_value=None), patch.object(
        bulb, "send", AsyncMock()
    ) as send:
        await bulb._async_send_register(message)
    send.assert_awaited_once_with(message)
