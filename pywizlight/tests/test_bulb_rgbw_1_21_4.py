"""Tests for the Bulb API with a rgbtw bulb."""
from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def rgbw_bulb() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP20_SHRGBC_01", firmware_version="1.21.4"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_model_description_rgbw_bulb(rgbw_bulb: wizlight) -> None:
    """Test fetching the model description rgbw bulb."""
    bulb_type = await rgbw_bulb.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(color=True, color_tmp=True, effect=True, brightness=True),
        name="ESP20_SHRGBC_01",
        kelvin_range=KelvinRange(max=6500, min=2200),
        bulb_type=BulbClass.RGB,
        fw_version="1.21.4",
        white_channels=1,
        white_to_color_ratio=30,
    )


@pytest.mark.asyncio
async def test_supported_scenes(rgbw_bulb: wizlight) -> None:
    """Test supported scenes."""
    assert await rgbw_bulb.getSupportedScenes() == [
        "Ocean",
        "Romance",
        "Sunset",
        "Party",
        "Fireplace",
        "Cozy",
        "Forest",
        "Pastel Colors",
        "Wake up",
        "Bedtime",
        "Warm White",
        "Daylight",
        "Cool white",
        "Night light",
        "Focus",
        "Relax",
        "True colors",
        "TV time",
        "Plantgrowth",
        "Spring",
        "Summer",
        "Fall",
        "Deepdive",
        "Jungle",
        "Mojito",
        "Club",
        "Christmas",
        "Halloween",
        "Candlelight",
        "Golden white",
        "Pulse",
        "Steampunk",
        "Rhythm",
    ]
