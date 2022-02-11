"""Tests for the Bulb API with a light strip."""
from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def turnable_bulb() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP21_SHTW_01", firmware_version="1.25.0"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_model_description_dimmable_bulb(turnable_bulb: wizlight) -> None:
    """Test fetching the model description dimmable bulb."""
    bulb_type = await turnable_bulb.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(color=False, color_tmp=True, effect=True, brightness=True),
        name="ESP21_SHTW_01",
        kelvin_range=KelvinRange(max=5000, min=2700),
        bulb_type=BulbClass.TW,
        fw_version="1.25.0",
        white_channels=1,
        white_to_color_ratio=20,
    )


@pytest.mark.asyncio
async def test_supported_scenes(turnable_bulb: wizlight) -> None:
    """Test supported scenes."""
    assert await turnable_bulb.getSupportedScenes() == [
        "Cozy",
        "Wake up",
        "Bedtime",
        "Warm White",
        "Daylight",
        "Cool white",
        "Night light",
        "Focus",
        "Relax",
        "TV time",
        "Candlelight",
        "Golden white",
        "Pulse",
        "Steampunk",
    ]
