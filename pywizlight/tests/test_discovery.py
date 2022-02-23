"""Tests for discovery."""
import asyncio
import contextlib
import logging
from typing import AsyncGenerator, Tuple
from unittest.mock import MagicMock, patch

import pytest

from pywizlight.discovery import (
    BroadcastProtocol,
    DiscoveredBulb,
    discover_lights,
    find_wizlights,
)

logging.getLogger("pywizlight").setLevel(logging.DEBUG)


@pytest.fixture
async def mock_discovery_aio_protocol() -> AsyncGenerator:
    """Fixture to mock an asyncio connection."""
    loop = asyncio.get_running_loop()
    future: asyncio.Future[
        Tuple[asyncio.DatagramProtocol, BroadcastProtocol]
    ] = asyncio.Future()

    async def _wait_for_connection():
        transport, protocol = await future
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        return transport, protocol

    async def _mock_create_datagram_endpoint(func, sock=None):
        protocol: BroadcastProtocol = func()
        transport = MagicMock()
        protocol.connection_made(transport)
        with contextlib.suppress(asyncio.InvalidStateError):
            future.set_result((transport, protocol))
        return transport, protocol

    with patch.object(loop, "create_datagram_endpoint", _mock_create_datagram_endpoint):
        yield _wait_for_connection


@pytest.mark.asyncio
async def test_find_wizlights(mock_discovery_aio_protocol):
    """Test find_wizlights."""
    task = asyncio.create_task(
        find_wizlights(wait_time=0.02, broadcast_address="192.168.213.252")
    )
    transport_protocol = await mock_discovery_aio_protocol()
    protocol: BroadcastProtocol = transport_protocol[1]
    protocol.datagram_received(
        b'{"method":"registration","env":"pro","result":{"mac":"d8a01199cf31","success":true}}',
        ("1.3.4.2", 1234),
    )
    protocol.datagram_received(
        b"garbage",
        ("1.3.4.2", 1234),
    )
    protocol.connection_lost(None)
    bulbs = await task
    assert bulbs == [DiscoveredBulb(ip_address="1.3.4.2", mac_address="d8a01199cf31")]


@pytest.mark.asyncio
async def test_discover_lights_fails(mock_discovery_aio_protocol):
    """Test discover_lights."""
    task = asyncio.create_task(discover_lights(wait_time=0.02))
    transport_protocol = await mock_discovery_aio_protocol()
    protocol: BroadcastProtocol = transport_protocol[1]
    protocol.connection_lost(OSError)
    with pytest.raises(OSError):
        await task


@pytest.mark.asyncio
async def test_discover_lights(mock_discovery_aio_protocol):
    """Test discover_lights success."""
    task = asyncio.create_task(discover_lights(wait_time=0.02))
    transport_protocol = await mock_discovery_aio_protocol()
    protocol: BroadcastProtocol = transport_protocol[1]
    protocol.datagram_received(
        b'{"method":"registration","env":"pro","result":{"mac":"d8a01199cf31","success":true}}',
        ("1.3.4.2", 1234),
    )
    protocol.datagram_received(
        b'{"method":"registration","env":"pro","result":{"mac":"d8a01199cf32","success":true}}',
        ("1.3.4.3", 1234),
    )
    protocol.connection_lost(None)
    bulbs = await task
    assert len(bulbs) == 2
