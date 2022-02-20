"""Tests for the Bulb API with a light strip."""
from typing import AsyncGenerator

import pytest

from pywizlight import PilotBuilder, wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def squire() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP20_DHRGB_01B", firmware_version="1.21.40"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_setting_ratio(squire: wizlight) -> None:
    """Test setting ratio."""
    await squire.set_ratio(50)
    state = await squire.updateState()
    assert state and state.get_ratio() == 50
    await squire.turn_on(PilotBuilder(ratio=20))
    state = await squire.updateState()
    assert state and state.get_ratio() == 20
    with pytest.raises(ValueError):
        await squire.set_ratio(500)


@pytest.mark.asyncio
async def test_model_description_squire(squire: wizlight) -> None:
    """Test fetching the model description for a squire."""
    bulb_type = await squire.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(
            color=True, color_tmp=True, effect=True, brightness=True, dual_head=True
        ),
        name="ESP20_DHRGB_01B",
        kelvin_range=KelvinRange(max=6500, min=2200),
        bulb_type=BulbClass.RGB,
        fw_version="1.21.40",
        white_channels=2,
        white_to_color_ratio=20,
    )
