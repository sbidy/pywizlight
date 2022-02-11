"""Tests for the Bulb API with a light strip."""
from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.tests.fake_bulb import startup_bulb
from pywizlight.exceptions import WizLightNotKnownBulb


@pytest.fixture()
async def missing_kelvin_range_bulb() -> AsyncGenerator[wizlight, None]:
    shutdown = startup_bulb(module_name="MISSING_KELVIN", firmware_version="1.16.64")
    bulb = wizlight(ip="127.0.0.1")
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_model_description_missing_kelvin_range(
    missing_kelvin_range_bulb: wizlight,
) -> None:
    """Test fetching the model description for a bulb missing the kelvin range."""
    with pytest.raises(WizLightNotKnownBulb):
        await missing_kelvin_range_bulb.get_bulbtype()
