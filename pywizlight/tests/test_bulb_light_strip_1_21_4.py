"""Tests for the Bulb API with a light strip."""
from typing import AsyncGenerator

import pytest

from pywizlight import PilotBuilder, wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def light_strip() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP20_SHRGB_01ABI", firmware_version="1.21.4"
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
async def test_model_description_light_strip(light_strip: wizlight) -> None:
    """Test fetching the model description for a light strip."""
    bulb_type = await light_strip.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(color=True, color_tmp=True, effect=True, brightness=True),
        name="ESP20_SHRGB_01ABI",
        kelvin_range=KelvinRange(max=6500, min=2700),
        bulb_type=BulbClass.RGB,
        fw_version="1.21.4",
        white_channels=2,
        white_to_color_ratio=80,
    )
