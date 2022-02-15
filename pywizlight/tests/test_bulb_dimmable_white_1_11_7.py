"""Tests for the Bulb API with a light strip."""
from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def dimmable_bulb() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="ESP06_SHDW9_01", firmware_version="1.11.7"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


# These have a cnx value in the response. Unknown what it means
# {"method":"getPilot","env":"pro","result":{"mac":"a8bb509f71d1","rssi":-54,"cnx":"0000","src":"","state":true,"sceneId":0,"temp":2700,"dimming":100}}
# {"method":"syncPilot","id":25,"env":"pro","params":{"mac":"a8bb509f71d1","rssi":-55,"cnx":"0000","src":"udp","state":true,"sceneId":0,"temp":2700,"dimming":100}}


@pytest.mark.asyncio
async def test_model_description_dimmable_bulb(dimmable_bulb: wizlight) -> None:
    """Test fetching the model description dimmable bulb."""
    bulb_type = await dimmable_bulb.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(color=False, color_tmp=False, effect=True, brightness=True),
        name="ESP06_SHDW9_01",
        kelvin_range=KelvinRange(max=6500, min=2700),
        bulb_type=BulbClass.DW,
        fw_version="1.11.7",
        white_channels=1,
        white_to_color_ratio=20,
    )
