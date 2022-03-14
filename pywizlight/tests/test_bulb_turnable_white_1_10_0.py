"""Tests for the Bulb API with a turnable white device with 1.10.0 firmware."""
from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def turnable_bulb() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP05_SHTW_21", firmware_version="1.10.0"
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
        features=Features(
            color=False, color_tmp=True, effect=True, brightness=True, dual_head=False
        ),
        name="ESP05_SHTW_21",
        kelvin_range=KelvinRange(max=6500, min=2700),
        bulb_type=BulbClass.TW,
        fw_version="1.10.0",
        white_channels=1,
        white_to_color_ratio=20,
    )
