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
        features=Features(
            color=True, color_tmp=True, effect=True, brightness=True, dual_head=False
        ),
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
        "Alarm",
        "Bedtime",
        "Candlelight",
        "Christmas",
        "Cozy",
        "Cool white",
        "Daylight",
        "Diwali",
        "Deep dive",
        "Fall",
        "Fireplace",
        "Forest",
        "Focus",
        "Golden white",
        "Halloween",
        "Jungle",
        "Mojito",
        "Night light",
        "Ocean",
        "Party",
        "Pulse",
        "Pastel colors",
        "Romance",
        "Relax",
        "Sunset",
        "Spring",
        "Summer",
        "Steampunk",
        "True colors",
        "TV time",
        "White",
        "Wake-up",
        "Warm white",
        "Rhythm",
    ]
