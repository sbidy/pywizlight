"""Tests for the Bulb API with a wall switch dimmer."""
from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def wall_switch() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP01_DIMTRIACS_01", firmware_version="1.16.68"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_model_description_wall_switch(wall_switch: wizlight) -> None:
    """Test fetching the model description wall switch."""
    bulb_type = await wall_switch.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(
            color=False, color_tmp=False, effect=False, brightness=True, dual_head=False
        ),
        name="ESP01_DIMTRIACS_01",
        kelvin_range=KelvinRange(max=2700, min=2700),
        bulb_type=BulbClass.DW,
        fw_version="1.16.68",
        white_channels=1,
        white_to_color_ratio=20,
    )
