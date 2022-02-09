"""Tests for the Bulb API."""
from typing import AsyncGenerator
from unittest.mock import patch

import pytest

from pywizlight import SCENES, PilotBuilder, wizlight
from pywizlight.bulblibrary import BulbClass, BulbType, Features, KelvinRange
from pywizlight.discovery import discover_lights
from pywizlight.exceptions import WizLightTimeOutError
from pywizlight.tests.fake_bulb import startup_bulb


@pytest.fixture(scope="module")
def startup_fake_bulb(request: pytest.FixtureRequest) -> None:
    shutdown = startup_bulb(module_name="ESP01_SHRGB_03")
    request.addfinalizer(shutdown)


@pytest.fixture()
async def correct_bulb(
    startup_fake_bulb: pytest.FixtureRequest,
) -> AsyncGenerator[wizlight, None]:
    bulb = wizlight(ip="127.0.0.1")
    yield bulb
    await bulb.async_close()


@pytest.fixture()
async def bad_bulb() -> AsyncGenerator[wizlight, None]:
    bulb = wizlight(ip="1.1.1.1")
    yield bulb
    await bulb.async_close()


# Non-Error states - PilotBuilder - Turn On
@pytest.mark.asyncio
async def test_Bulb_Discovery(correct_bulb: wizlight) -> None:
    """Test discovery function."""
    # Use a random available port since otherwise the
    # test may fail
    with patch("pywizlight.discovery.PORT", 0):
        bulbs = await discover_lights(broadcast_space="192.168.178.255", wait_time=0.02)
    for bulb in bulbs:
        with patch("pywizlight.bulb.SEND_INTERVAL", 0.01), patch(
            "pywizlight.bulb.TIMEOUT", 0.01
        ):
            state = await bulb.updateState()
        assert state and state.get_state() is False


@pytest.mark.asyncio
async def test_PilotBuilder_state(correct_bulb: wizlight) -> None:
    """Test State."""
    state = await correct_bulb.updateState()
    assert state and state.get_state() is False


@pytest.mark.asyncio
async def test_PilotBuilder_colortemp(correct_bulb: wizlight) -> None:
    """Test Color Temp."""
    await correct_bulb.turn_on(PilotBuilder(colortemp=2800))
    state = await correct_bulb.updateState()

    assert state and state.get_colortemp() == 2800


@pytest.mark.asyncio
async def test_PilotBuilder_brightness(correct_bulb: wizlight) -> None:
    """Test Brightness."""
    await correct_bulb.turn_on(PilotBuilder(brightness=10))
    state = await correct_bulb.updateState()
    # 10% == 26 in Hex
    assert state and state.get_brightness() == 26


@pytest.mark.asyncio
async def test_PilotBuilder_warm_wite(correct_bulb: wizlight) -> None:
    """Test Warm White."""
    await correct_bulb.turn_on(PilotBuilder(warm_white=255))
    state = await correct_bulb.updateState()

    assert state and state.get_warm_white() == 255


@pytest.mark.asyncio
async def test_PilotBuilder_cold_white(correct_bulb: wizlight) -> None:
    """Test Cold White."""
    await correct_bulb.turn_on(PilotBuilder(cold_white=255))
    state = await correct_bulb.updateState()

    assert state and state.get_cold_white() == 255


@pytest.mark.asyncio
async def test_PilotBuilder_rgb(correct_bulb: wizlight) -> None:
    """Test RGB Value."""
    await correct_bulb.turn_on(PilotBuilder(rgb=(0, 128, 255)))
    state = await correct_bulb.updateState()

    assert state and state.get_rgb() == (0, 127, 255)


@pytest.mark.asyncio
async def test_PilotBuilder_hucolor(correct_bulb: wizlight) -> None:
    """Test RGB Value via hucolor."""
    await correct_bulb.turn_on(PilotBuilder(hucolor=(100, 50)))
    state = await correct_bulb.updateState()

    assert state and state.get_rgb() == (88.0, 255.0, 0.0)


@pytest.mark.asyncio
async def test_setting_rgbw(correct_bulb: wizlight) -> None:
    """Test setting rgbw."""
    await correct_bulb.turn_on(PilotBuilder(rgbw=(1, 2, 3, 4)))
    state = await correct_bulb.updateState()
    assert state and state.get_rgbw() == (1, 2, 3, 4)


@pytest.mark.asyncio
async def test_PilotBuilder_scene(correct_bulb: wizlight) -> None:
    """Test scene."""
    await correct_bulb.turn_on(PilotBuilder(scene=1))
    state = await correct_bulb.updateState()

    assert state and state.get_scene() == SCENES[1]


@pytest.mark.asyncio
async def test_PilotBuilder_speed(correct_bulb: wizlight) -> None:
    """Test speed."""
    await correct_bulb.turn_on(PilotBuilder(scene=1, speed=50))
    state = await correct_bulb.updateState()

    assert state and state.get_scene() == SCENES[1]
    assert state and state.get_speed() == 50


# ------ Error states -------------------------------------
@pytest.mark.asyncio
async def test_error_PilotBuilder_brightness(correct_bulb: wizlight) -> None:
    """Error Brightness."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(brightness=500))


@pytest.mark.asyncio
async def test_error_PilotBuilder_warm_wite(correct_bulb: wizlight) -> None:
    """Error Warm White."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(warm_white=300))
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(warm_white=-1))


@pytest.mark.asyncio
async def test_error_PilotBuilder_cold_white_upper(correct_bulb: wizlight) -> None:
    """Error Cold White."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(cold_white=300))


@pytest.mark.asyncio
async def test_error_PilotBuilder_cold_white_lower(correct_bulb: wizlight) -> None:
    """Error Cold White."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(cold_white=-1))


@pytest.mark.asyncio
async def test_error_PilotBuilder_r(correct_bulb: wizlight) -> None:
    """Error Red Value."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(rgb=(300, 0, 0)))


@pytest.mark.asyncio
async def test_error_PilotBuilder_green(correct_bulb: wizlight) -> None:
    """Error Green Value."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(rgb=(0, 300, 0)))


@pytest.mark.asyncio
async def test_error_PilotBuilder_blue(correct_bulb: wizlight) -> None:
    """Error Blue Value."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(rgb=(0, 0, 300)))


@pytest.mark.asyncio
async def test_error_PilotBuilder_cold_white(correct_bulb: wizlight) -> None:
    """Error Cold White Value."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(cold_white=9999))


@pytest.mark.asyncio
async def test_error_PilotBuilder_scene(correct_bulb: wizlight) -> None:
    """Error scene."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(scene=532))


@pytest.mark.asyncio
async def test_error_PilotBuilder_speed(correct_bulb: wizlight) -> None:
    """Error speed."""
    with pytest.raises(ValueError):
        await correct_bulb.turn_on(PilotBuilder(speed=532))


@pytest.mark.asyncio
async def test_fw_version(correct_bulb: wizlight) -> None:
    """Test fetching the firmware version."""
    bulb_type = await correct_bulb.get_bulbtype()
    assert bulb_type == BulbType(
        features=Features(color=True, color_tmp=True, effect=True, brightness=True),
        name="ESP01_SHRGB_03",
        kelvin_range=KelvinRange(max=6500, min=2200),
        bulb_type=BulbClass.RGB,
        fw_version="1.21.0",
        white_channels=1,
        white_to_color_ratio=30,
    )
    assert correct_bulb.mac == "a8bb5006033d"


@pytest.mark.asyncio
async def test_get_mac(correct_bulb: wizlight) -> None:
    """Test getting the mac address."""
    mac = await correct_bulb.getMac()
    assert mac == "a8bb5006033d"
    mac = await correct_bulb.getMac()
    assert mac == "a8bb5006033d"


# Error states / Timout
@pytest.mark.asyncio
async def test_timeout(bad_bulb: wizlight) -> None:
    """Test the timout exception after."""
    with pytest.raises(WizLightTimeOutError), patch(
        "pywizlight.bulb.SEND_INTERVAL", 0.01
    ), patch("pywizlight.bulb.TIMEOUT", 0.01):
        await bad_bulb.getBulbConfig()


@pytest.mark.asyncio
async def test_timeout_PilotBuilder(bad_bulb: wizlight) -> None:
    """Test Timout for Result."""
    # check if the bulb state it given as bool - mock ?
    with pytest.raises(WizLightTimeOutError), patch(
        "pywizlight.bulb.SEND_INTERVAL", 0.01
    ), patch("pywizlight.bulb.TIMEOUT", 0.01):
        await bad_bulb.turn_on(PilotBuilder(brightness=255))
