"""Tests for the Bulb API with a light strip."""
from typing import AsyncGenerator

import pytest

from pywizlight import wizlight
from pywizlight.exceptions import WizLightConnectionError
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture()
async def broken_bulb() -> AsyncGenerator[wizlight, None]:
    shutdown, port = await startup_bulb(
        module_name="BROKEN_JSON", firmware_version="1.0.0"
    )
    bulb = wizlight(ip="127.0.0.1", port=port)
    yield bulb
    await bulb.async_close()
    shutdown()


@pytest.mark.asyncio
async def test_model_description_broken_bulb(
    broken_bulb: wizlight, caplog: pytest.LogCaptureFixture
) -> None:
    """Test fetching the model description for an bulb that generates broken json."""
    with pytest.raises(WizLightConnectionError):
        await broken_bulb.get_bulbtype()
    assert "Failed to decode message" in caplog.text
