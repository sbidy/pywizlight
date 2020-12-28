import pytest
import asyncio

from asyncio import TimeoutError

from pywizlight import wizlight, PilotBuilder
from pywizlight.exceptions import WizLightTimeOutError, WizLightConnectionError


@pytest.mark.asyncio
async def test_timeout():
    """Test the timout exception after."""
    test_bulb = wizlight(ip="1.1.1.1")
    with pytest.raises(WizLightTimeOutError):
        await test_bulb.getBulbConfig()


@pytest.mark.asyncio
async def test_timeout_PilotBuilder():
    """Test Timout for Result."""
    test_bulb = wizlight(ip="1.1.1.1")
    # check if the bulb state it given as bool
    with pytest.raises(WizLightTimeOutError):
        await test_bulb.turn_on(PilotBuilder(brightness=255))


@pytest.mark.asyncio
async def test_state_detection():
    """Test state detection."""
    test_bulb = wizlight(ip="192.168.178.95")
    state = await test_bulb.updateState()
    # check if the bulb state it given as bool
    assert type(state.get_state()) is bool
