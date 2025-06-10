"""Tests for the Bulb API with a fan."""

from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def fan() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP03_FANDIMS_31", firmware_version="1.31.32"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_model_description_fan(fan: wizlight) -> None:
    """Test fetching the model description of a socket is None."""
    bulb_type = await fan.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(
            color=False,
            color_tmp=False,
            effect=False,
            brightness=True,
            dual_head=False,
            fan=True,
            fan_breeze_mode=True,
            fan_reverse=True,
        ),
        name="ESP03_FANDIMS_31",
        kelvin_range=KelvinRange(max=2700, min=2700),
        bulb_type=BulbClass.FANDIM,
        fw_version="1.31.32",
        white_channels=1,
        white_to_color_ratio=20,
        fan_speed_range=6,
    )


@pytest.mark.asyncio
async def test_diagnostics(fan: wizlight) -> None:
    """Test fetching diagnostics."""
    await fan.get_bulbtype()
    diagnostics = fan.diagnostics
    assert diagnostics["bulb_type"]["bulb_type"] == "FANDIM"
    assert diagnostics["history"]["last_error"] is None
    assert diagnostics["push_running"] is False


@pytest.mark.asyncio
async def test_supported_scenes(fan: wizlight) -> None:
    """Test supported scenes."""
    assert await fan.getSupportedScenes() == []
