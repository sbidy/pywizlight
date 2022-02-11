"""Tests for the Bulb API with a socket."""
from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def socket() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP10_SOCKET_06", firmware_version="1.25.0"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_model_description_socket(socket: wizlight) -> None:
    """Test fetching the model description of a socket is None."""
    bulb_type = await socket.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(color=False, color_tmp=False, effect=False, brightness=False),
        name="ESP10_SOCKET_06",
        kelvin_range=KelvinRange(max=2700, min=2700),
        bulb_type=BulbClass.SOCKET,
        fw_version="1.25.0",
        white_channels=2,
        white_to_color_ratio=20,
    )


@pytest.mark.asyncio
async def test_supported_scenes(socket: wizlight) -> None:
    """Test supported scenes."""
    assert await socket.getSupportedScenes() == []
