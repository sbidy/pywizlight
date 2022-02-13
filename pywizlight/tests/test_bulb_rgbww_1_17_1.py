"""Tests for the Bulb API."""
from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def rgbww_bulb() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP01_SHRGB1C_31", firmware_version="1.17.1"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_model_description_rgbww_bulb(rgbww_bulb: wizlight) -> None:
    """Test fetching the model description rgbww bulb."""
    bulb_type = await rgbww_bulb.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(color=True, color_tmp=True, effect=True, brightness=True),
        name="ESP01_SHRGB1C_31",
        kelvin_range=KelvinRange(max=6500, min=2700),
        bulb_type=BulbClass.RGB,
        fw_version="1.17.1",
        white_channels=2,
        white_to_color_ratio=20,
    )
