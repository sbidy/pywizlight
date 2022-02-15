"""Tests for the Bulb API with a light strip."""
from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def dimmable_bulb() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP05_SHDW_21", firmware_version="1.25.0"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_model_description_dimmable_bulb(dimmable_bulb: wizlight) -> None:
    """Test fetching the model description dimmable bulb."""
    bulb_type = await dimmable_bulb.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(color=False, color_tmp=False, effect=True, brightness=True),
        name="ESP05_SHDW_21",
        kelvin_range=KelvinRange(max=2700, min=2700),
        bulb_type=BulbClass.DW,
        fw_version="1.25.0",
        white_channels=1,
        white_to_color_ratio=20,
    )


@pytest.mark.asyncio
async def test_supported_scenes(dimmable_bulb: wizlight) -> None:
    """Test supported scenes."""
    assert await dimmable_bulb.getSupportedScenes() == [
        "Wake up",
        "Bedtime",
        "Cool white",
        "Night light",
        "Candlelight",
        "Golden white",
        "Pulse",
        "Steampunk",
    ]
