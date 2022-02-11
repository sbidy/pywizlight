"""Tests for the Bulb API with a light strip."""
from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.exceptions import WizLightNotKnownBulb
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def no_module_bulb() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="MISSING", firmware_version="1.16.64"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_model_description_no_module_bulb(no_module_bulb: wizlight) -> None:
    """Test fetching the model description for a bulb missing the module."""
    with pytest.raises(WizLightNotKnownBulb):
        await no_module_bulb.get_bulbtype()
