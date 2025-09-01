"""Tests for the Bulb API with a light strip."""

from typing import AsyncGenerator

import pytest

from pywizlight import PilotBuilder, wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def light_strip() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP20_SHRGB_01ABI", firmware_version="1.25.0"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_setting_rgbww(light_strip: wizlight) -> None:
    """Test setting rgbww."""
    await light_strip.turn_on(PilotBuilder(rgbww=(1, 2, 3, 4, 5)))
    state = await light_strip.updateState()
    assert state and state.get_rgbww() == (1, 2, 3, 4, 5)


@pytest.mark.asyncio
async def test_supported_scenes(light_strip: wizlight) -> None:
    """Test supported scenes."""
    assert await light_strip.getSupportedScenes() == [
        "Alarm",
        "Bedtime",
        "Candlelight",
        "Christmas",
        "Cozy",
        "Cool white",
        "Club",
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
        "Plantgrowth",
        "Romance",
        "Relax",
        "Snowy sky",
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


@pytest.mark.asyncio
async def test_model_description_light_strip(light_strip: wizlight) -> None:
    """Test fetching the model description for a light strip."""
    bulb_type = await light_strip.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(
            color=True, color_tmp=True, effect=True, brightness=True, dual_head=False
        ),
        name="ESP20_SHRGB_01ABI",
        kelvin_range=KelvinRange(max=6500, min=2700),
        bulb_type=BulbClass.RGB,
        fw_version="1.25.0",
        white_channels=2,
        white_to_color_ratio=80,
    )
